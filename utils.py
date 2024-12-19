import cv2

def rgb_to_hsv(img):
    bgr_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
    return hsv_img
def rgb_to_lab(img):
    bgr_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    lab_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2LAB)
    return lab_img
