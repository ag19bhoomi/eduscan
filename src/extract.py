import easyocr
import streamlit as st
from .preprocess import preprocess_image
from .nlp_engine import EDUSCAN_NLP

# Move the reader into a cached function to prevent startup hangs
@st.cache_resource
def get_ocr_reader():
    # This will now download the models ONLY when needed
    return easyocr.Reader(['en'], gpu=False)

def extract_student_info(image_path):
    # Initialize the brain
    nlp_processor = EDUSCAN_NLP()
    
    # Get the reader (it will download models here if not present)
    with st.spinner("Downloading/Loading OCR Models... Please wait."):
        reader = get_ocr_reader()
    
    # 1. Preprocess
    processed_img = preprocess_image(image_path)
    
    # 2. Extract Text
    result = reader.readtext(processed_img, detail=0)
    
    # 3. NLP Intelligence
    structured_data = nlp_processor.classify_text(result)
    
    return structured_data
