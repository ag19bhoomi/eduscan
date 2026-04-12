import streamlit as st
import pandas as pd
import cv2
import os
import io
import sys

# This line ensures Python can see the 'src' folder clearly
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocess import get_clean_marksheet
from src.extract import extract_student_info

st.set_page_config(page_title="EDUSCAN", layout="wide")

st.title("📄 EDUSCAN: Batch Extraction")

uploaded_files = st.file_uploader("Upload Marksheets", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Start Processing"):
        results = []
        progress = st.progress(0)
        
        for i, file in enumerate(uploaded_files):
            # Save temp
            t_path = f"temp_{file.name}"
            with open(t_path, "wb") as f:
                f.write(file.getbuffer())
            
            try:
                # Process
                cleaned = get_clean_marksheet(t_path)
                c_path = f"c_{file.name}"
                cv2.imwrite(c_path, cleaned)
                
                # Extract
                data = extract_student_info(c_path)
                data['Filename'] = file.name
                results.append(data)
                
                st.write(f"✅ Processed {file.name}: **{data['NAME']}**")
                os.remove(c_path)
            finally:
                if os.path.exists(t_path): os.remove(t_path)
            
            progress.progress((i + 1) / len(uploaded_files))

        # Show Table and Download
        df = pd.DataFrame(results)
        st.table(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button("📥 Download Excel Report", output.getvalue(), "EDUSCAN_Report.xlsx")