import easyocr
import os
from .nlp_engine import EDUSCAN_NLP # Import your new intelligence layer

# Initialize EasyOCR
reader = easyocr.Reader(['en', 'hi'], gpu=False)

# Initialize your NLP engine
nlp_processor = EDUSCAN_NLP()

def extract_student_info(image_path):
    ocr_results = reader.readtext(image_path)
    
    # IMPORTANT: Only extract the string (the second item in the tuple)
    raw_text_list = [res[1] for res in ocr_results]
    
    # Pass just the strings to the NLP engine
    return nlp_processor.classify_text(raw_text_list)

if __name__ == "__main__":
    test_path = 'data/processed/cleaned_marksheet.jpg'
    print("--- EDUSCAN Hybrid Extraction (OCR + NLP) ---")
    
    data = extract_student_info(test_path)
    
    print(f"Result from NLP Engine:")
    print(f"Name: {data['NAME']}")
    print(f"Roll: {data['ROLL_NO']}")