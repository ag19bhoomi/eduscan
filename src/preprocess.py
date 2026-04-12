import cv2
import numpy as np
import os

def get_clean_marksheet(image_path):
    """
    Cleans the marksheet image to improve OCR accuracy.
    """
    # 1. Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not open or find the image: {image_path}")
        
    # 2. Convert to Grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 3. Denoising
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # 4. Adaptive Thresholding (Black text on white background)
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

# ALIAS: This ensures that if another file asks for 'preprocess_image', 
# it points to the same function.
preprocess_image = get_clean_marksheet
