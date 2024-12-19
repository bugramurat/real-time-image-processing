import cv2
import numpy as np
from PIL import Image

def apply_global_threshold(image, threshold_value):
    # Grayscale formatına dönüştür
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresholded_image = cv2.threshold(
        gray_image, threshold_value, 255, cv2.THRESH_BINARY
    )
    return thresholded_image

def apply_adaptive_threshold(img, factor):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresholded_img = cv2.adaptiveThreshold(
        img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,  # Block size, adjust if needed
        factor  # The factor is used as a constant subtracted from the mean
    )
    return thresholded_img

def apply_otsu_threshold(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresholded_image = cv2.threshold(
        img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresholded_image

def hsv_threshold(img, lower_hue, upper_hue):
    if isinstance(img, Image.Image):
        img = np.array(img)

    if len(img.shape) == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif len(img.shape) != 3:
        raise ValueError("Input image must be a 3-channel (RGB/BGR) image.")

    try:
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    except cv2.error as e:
        print(f"Error converting to HSV: {e}")
        return None

    lower_bound = np.array([lower_hue, 100, 100], dtype=np.uint8) 
    upper_bound = np.array([upper_hue, 255, 255], dtype=np.uint8) 

    # Maskeyi uygula ve kontrol et
    try:
        mask = cv2.inRange(img_hsv, lower_bound, upper_bound)
    except cv2.error as e:
        print(f"Error in cv2.inRange: {e}")
        return None

    return mask