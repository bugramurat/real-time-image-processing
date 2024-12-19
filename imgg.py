from flask import Flask, render_template, request, jsonify, send_file
import io
import cv2
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import logging
from adjustments import adjust_brightness, adjust_contrast, adjust_exposure, adjust_shadows, adjust_highlights, enhance_sharpness, enhance_definition, apply_blur, enhance_brilliance
from filters import apply_global_threshold, apply_adaptive_threshold, apply_otsu_threshold, hsv_threshold
from utils import rgb_to_hsv, rgb_to_lab

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to capture all log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('app.log')  # Output to a log file
    ]
)

param_defaults = {
    'adaptive_threshold': '0',
    'global_threshold': '128',
    'otsu_threshold': 'off',
    'apply_hsv': 'off',
    'lower_hue': '0',
    'upper_hue': '179',
    'grayscale': 'off',
    'brightness': '1',
    'contrast': '1',
    'exposure': '1',
    'shadows': '1',
    'highlights': '1',
    'sharpness': '1',
    'definition': '1',
    'blur': '0',
    'brilliance': '1',
    'colorspace': 'rgb',
    'hue': '0',
    'saturation': '1',
    'vibrance': '1',
}
def get_form_param(request, param_name, default_value):
    return request.form.get(param_name, default_value)

app = Flask(__name__)

@app.route('/some-route')
def some_route():
    app.logger.debug("This is a debug message.")
    app.logger.info("This is an info message.")
    app.logger.error("This is an error message.")
    return "Check logs for messages!"

# Asynchronous processing with ThreadPoolExecutor
executor = ThreadPoolExecutor(4)  # Processing with 4 threads

# Home route to render the HTML file
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    try:
        file = request.files['image']

        params = {key: get_form_param(request, key, default) for key, default in param_defaults.items()}

        img = Image.open(file)
        img = img.resize((img.width // 2, img.height // 2))  # Reduce size by half
        img = np.array(img)

        # Starting asynchronous processing
        processed_img_future = executor.submit(apply_filters, img, **params)
        processed_img = processed_img_future.result()

        # Convert to byte format for sending the image
        img_io = io.BytesIO()
        processed_img.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process-original', methods=['POST'])
def process_original():
    # Log the incoming request to check if it's being triggered
    logging.debug("Process original image route triggered.")
    if 'image' not in request.files:
        logging.error("No image uploaded.")
        return "Image or settings are missing", 400
    try:
        # Read the image from the request into memory using BytesIO
        img_bytes = request.files['image'].read()
        logging.debug(f"Image size: {len(img_bytes)} bytes")
        org_img_io = io.BytesIO(img_bytes)
        
        params = {key: get_form_param(request, key, default) for key, default in param_defaults.items()}

        img = Image.open(org_img_io)
        img = np.array(img)
        if len(img.shape) == 2: 
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        processed_org_img_future = executor.submit(apply_filters, img, **params)
        processed_org_img = processed_org_img_future.result()

        # Log the processed image size
        processed_img_bytes = io.BytesIO()
        processed_org_img.save(processed_img_bytes, 'JPEG')
        processed_img_bytes.seek(0)
        logging.debug(f"Processed image size: {len(processed_img_bytes.getvalue())} bytes")

        # Send processed image
        org_img_io = io.BytesIO()
        processed_org_img.save(org_img_io, 'JPEG')
        org_img_io.seek(0)
        logging.debug("Returning processed image.")
        return send_file(org_img_io, mimetype='image/jpeg', as_attachment=True, download_name='processed-original.jpg')
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download-array', methods=['POST'])
def download_array():
    try:
        # Read the image from the request into memory using BytesIO
        img_bytes = request.files['image'].read()
        logging.debug(f"Image size: {len(img_bytes)} bytes")
        org_img_io = io.BytesIO(img_bytes)

        params = {key: get_form_param(request, key, default) for key, default in param_defaults.items()}

        img = Image.open(org_img_io)
        img = np.array(img)
        if len(img.shape) == 2: 
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        processed_org_img_future = executor.submit(apply_filters, img, **params)
        processed_org_img = processed_org_img_future.result()

        img_array = np.array(processed_org_img)

        if params['colorspace'] == 'hsv':
            img_array = rgb_to_hsv(img_array)
        elif params['colorspace'] == 'lab':
            img_array = rgb_to_lab(img_array)

        # Save the processed image array in a temporary storage for download
        last_image_array = img_array.tolist()  
        # Ensure last_image_array is a NumPy array
        last_image_array = np.array(last_image_array)
        # Get the shape of the array
        if len(last_image_array.shape) == 2:
            height, width = last_image_array.shape
            channels = 1 
        else:
            height, width, channels = last_image_array.shape

        # Reshape the 3D array to a 2D array
        reshaped_array = last_image_array.reshape(height, -1)

        # Create a file-like object for the array text
        array_io = io.StringIO()
        np.savetxt(array_io, reshaped_array, fmt='%d', delimiter=",")
        array_io.seek(0)

        # Add metadata for reconstructing the array
        metadata = f"# Shape: {height}x{width}x{channels}\n"

        # Combine metadata and array data into a single output
        output = metadata + array_io.getvalue()

        return send_file(
            io.BytesIO(output.encode('utf-8')),
            as_attachment=True,
            download_name="image_array.txt",
            mimetype="text/plain"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def apply_filters(img, **kwargs):
    try:
        if kwargs['grayscale'] == 'on':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)  # Revert to 3 channel format

        img = apply_color_adjustments(img, kwargs['hue'], kwargs['saturation'], kwargs['vibrance'])
        img = apply_basic_adjustments(img, kwargs['brightness'], kwargs['contrast'], kwargs['exposure'], kwargs['shadows'], kwargs['highlights'])
        img = apply_effects(img, kwargs['sharpness'], kwargs['definition'], kwargs['blur'], kwargs['brilliance'])
        img = apply_thresholds(img, kwargs['global_threshold'], kwargs['adaptive_threshold'], kwargs['otsu_threshold'], kwargs['apply_hsv'], kwargs['lower_hue'], kwargs['upper_hue'])

        # Return to PIL format from NumPy
        img = Image.fromarray(img)
        return img
    except Exception as e:
        print(f"Error in apply_filters: {str(e)}")
        raise e  # Raise again to propagate the error

def apply_basic_adjustments(img, brightness, contrast, exposure, shadows, highlights):
    if brightness != '1':
        img = adjust_brightness(img, float(brightness))
    if contrast != '1':
        img = adjust_contrast(img, float(contrast))
    if exposure != '1':
        img = adjust_exposure(img, float(exposure))
    if shadows != '1':
        img = adjust_shadows(img, float(shadows))
    if highlights != '1':
        img = adjust_highlights(img, float(highlights))
    return img

def apply_effects(img, sharpness, definition, blur, brilliance):
    if sharpness != '1':
        img = enhance_sharpness(img, float(sharpness))
    if definition != '1':
        img = enhance_definition(img, float(definition))
    if blur != '0':
        img = apply_blur(img, int(float(blur)))
    if brilliance != '1':
        img = enhance_brilliance(img, float(brilliance))
    return img

def apply_thresholds(img, global_threshold, adaptive_threshold, otsu_threshold, apply_hsv, lower_hue, upper_hue):
    if global_threshold != '128': 
        img = apply_global_threshold(img, int(float(global_threshold)))
    if adaptive_threshold != '0': 
        img = apply_adaptive_threshold(img, int(float(adaptive_threshold)))
    if otsu_threshold == 'on':
        img = apply_otsu_threshold(img)
    if apply_hsv == 'on' :
        img = hsv_threshold(img, lower_hue, upper_hue)
    return img

def apply_color_adjustments(img, hue, saturation, vibrance):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # Ensure hue is treated as integer
    if hue != '0':
        hue = int(hue) 
        h = (h + hue) % 180  # Hue ranges from 0 to 179 in OpenCV

    # Ensure saturation is treated as float
    if saturation != '1':
        saturation = float(saturation)
        s = s.astype(np.float32)  # Ensure that saturation values are in float32
        s = np.clip(s * saturation, 0, 255)  # Saturation values between 0 and 255
        s = s.astype(np.uint8)  # Convert back to uint8 after clipping

    # Ensure vibrance is treated as float and adjust saturation for lower saturation values
    if vibrance != '1':
        vibrance = float(vibrance) 
        mask = s < 128  # Mask for lower saturation areas
        s[mask] = np.clip(s[mask] * vibrance, 0, 255)  # Apply vibrance to low saturation areas

    hsv = cv2.merge([h, s, v])
    img_adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img_adjusted

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
