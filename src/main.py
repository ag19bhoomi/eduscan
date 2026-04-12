import os
import pandas as pd
import cv2
from preprocess import get_clean_marksheet
from extract import extract_student_info

def run_automation():
    # Define your project paths
    raw_dir = 'data/raw/'
    processed_dir = 'data/processed/'
    output_path = 'data/output/Final_Extraction_Report.xlsx'
    
    # Create output directory if it doesn't exist
    if not os.path.exists('data/output/'):
        os.makedirs('data/output/')

    results_list = []

    print("--- EDUSCAN: Starting Batch Processing ---")

    # Loop through all images in the raw data folder
    for filename in os.listdir(raw_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing: {filename}...")
            
            input_path = os.path.join(raw_dir, filename)
            
            # 1. Clean the image (Preprocessing)
            cleaned_img = get_clean_marksheet(input_path)
            temp_cleaned_path = os.path.join(processed_dir, f"cleaned_{filename}")
            cv2.imwrite(temp_cleaned_path, cleaned_img)
            
            # 2. Extract Data (OCR + NLP)
            data = extract_student_info(temp_cleaned_path)
            data['Filename'] = filename
            
            results_list.append(data)

    # 3. Save everything to Excel
    if results_list:
        df = pd.DataFrame(results_list)
        # Reordering columns for a cleaner look
        df = df[['Filename', 'NAME', 'ROLL_NO']]
        df.to_excel(output_path, index=False)
        print(f"\nSuccess! Data exported to: {output_path}")
    else:
        print("No images found in the raw data folder.")

if __name__ == "__main__":
    run_automation()