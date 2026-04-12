import easyocr
import streamlit as st
import os

# Absolute imports to keep Streamlit Cloud happy
try:
    from src.preprocess import get_clean_marksheet
    from src.nlp_engine import EDUSCAN_NLP
except ImportError:
    from preprocess import get_clean_marksheet
    from nlp_engine import EDUSCAN_NLP

# Cache the OCR reader so it doesn't download every time you click a button
@st.cache_resource
def get_ocr_reader():
    # 'en' for English; gpu=False because Streamlit Cloud is CPU-only
    return easyocr.Reader(['en'], gpu=False)

def extract_student_info(image_path):
    """
    Takes a path to an image, cleans it, runs OCR, and structures the data.
    """
    # 1. Initialize the NLP 'Brain'
    nlp_processor = EDUSCAN_NLP()
    
    # 2. Get the OCR Reader (triggers download on first run)
    reader = get_ocr_reader()
    
    # 3. Preprocess the image
    cleaned_img = get_clean_marksheet(image_path)
    
    # We need to save the cleaned image temporarily for EasyOCR to read it
    temp_clean_path = f"temp_ocr_{os.path.basename(image_path)}"
    import cv2
    cv2.imwrite(temp_clean_path, cleaned_img)
    
    # 4. Run OCR
    try:
        raw_text_list = reader.readtext(temp_clean_path, detail=0)
        
        # 5. Use NLP to find Name and Roll Number
        structured_data = nlp_processor.classify_text(raw_text_list)
        return structured_data
        
    finally:
        # Cleanup the temporary cleaned file
        if os.path.exists(temp_clean_path):
            os.remove(temp_clean_path)
