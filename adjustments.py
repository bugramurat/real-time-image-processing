import cv2
import numpy as np
from PIL import Image, ImageEnhance

def adjust_brightness(img, factor):
    img_array = np.array(img, dtype=np.float32)

    # Normalize (between 0 and 1)
    img_array = img_array / 255.0 

    # Instead of adjusting pixel values ​​directly without checking them, we process each pixel differently
    # Let's process shadow and highlight areas separately
    # We apply a non-linear process for high brightness
    img_array = img_array ** (1 / factor)  # Increase or decrease in brightness
    img_array = np.clip(img_array * 255, 0, 255)
    img_array = np.uint8(img_array)  
    return img_array

def adjust_contrast(img, factor):
    return np.array(ImageEnhance.Contrast(Image.fromarray(img)).enhance(factor))

def adjust_exposure(img, factor):
    # Exposure is usually done with gamma correction or contrast
    # If the factor is greater than 1, the brightness increases, if it is smaller, the darkness becomes more pronounced
    # Exposure correction can be done with OpenCV's convertScaleAbs function
    factor = float(factor)

    # Multiply each pixel to adjust pixel values
    img = np.array(img, dtype=np.float32)
    img *= factor 
    
    # There may be high values, so we limit it to 255
    img = np.clip(img, 0, 255)
    return np.array(img, dtype=np.uint8)

def adjust_shadows(img, factor):
    if isinstance(img, Image.Image):
        img = np.array(img)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Identify shadow areas (low 'v' values, below a certain threshold)
    shadow_mask = v < 80  # Threshold value for targeting shadow areas
    
    # Increase the brightness of shadow areas based on the factor
    v[shadow_mask] = np.clip(v[shadow_mask] * factor, 0, 255)
    
    hsv = cv2.merge([h, s, v])
    img_adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return img_adjusted

def adjust_highlights(img, factor):
    img_array = np.array(img, dtype=np.float32)

    # Normalize the image to range [0, 1]
    img_array /= 255.0  # Convert to [0, 1] range

    # Define the mask for bright regions
    mask = img_array > 0.7  # Increase the threshold to target the highlights more accurately

    # Apply the factor to the bright areas
    img_array[mask] *= factor
    
    # Ensure the values remain in the [0, 1] range after adjustments
    img_array = np.clip(img_array, 0, 1)
    
    # Convert the array back to the [0, 255] range
    img_array = (img_array * 255).astype(np.uint8)
    return img_array

def enhance_sharpness(img, factor):
    return np.array(ImageEnhance.Sharpness(Image.fromarray(img)).enhance(factor))

def enhance_definition(img, factor):
    img = enhance_sharpness(img, factor)
    return adjust_contrast(img, factor)

def apply_blur(img, blur_radius):
    if blur_radius > 0:
        return cv2.GaussianBlur(img, (2 * blur_radius + 1, 2 * blur_radius + 1), 0)
    return img

def enhance_brilliance(img, factor):
    img = adjust_brightness(img, factor)
    return adjust_contrast(img, factor)