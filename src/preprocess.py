import cv2
import numpy as np

def get_clean_marksheet(image_path):
    # 1. Load the image
    image = cv2.imread(image_path)
    
    # 2. Convert to Grayscale
    # Essential for reducing complexity before text extraction [cite: 88]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 3. Denoising
    # Removes small dots/grain often found in scans 
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # 4. Adaptive Thresholding
    # Best for marksheets because it handles shadows/uneven light 
    # It makes the background white and the text black
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

# Test it out
if __name__ == "__main__":
    # 1. Path to your input image (Make sure you put an image in this folder first!)
    # Change 'my_marksheet.jpg' to the actual name of your file
    input_path = 'data/raw/marksheet1.png' 
    
    # 2. Path where you want to save the cleaned version
    output_path = 'data/processed/cleaned_marksheet.jpg'
    
    try:
        # Run the cleaning function
        processed_img = get_clean_marksheet(input_path)
        
        # Save the result to the 'processed' folder
        cv2.imwrite(output_path, processed_img)
        print(f"Success! Cleaned image saved at: {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Check if the file name in 'input_path' is correct.")