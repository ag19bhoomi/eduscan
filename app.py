import sys
import os
import io

# --- 1. FORCE PATH INJECTION ---
# This tells Python to look inside the 'src' folder for your modules
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

import streamlit as st
import pandas as pd
import cv2
import numpy as np

# --- 2. INTERNAL IMPORTS ---
try:
    # We import these directly because we added 'src' to the sys.path above
    from preprocess import get_clean_marksheet
    from extract import extract_student_info
except ImportError as e:
    st.error(f"❌ Critical Import Error: {e}")
    st.info("Ensure your 'src' folder contains __init__.py, preprocess.py, and extract.py")
    st.stop()

# --- 3. APP CONFIGURATION ---
st.set_page_config(
    page_title="EDUSCAN | AI Marksheet Automation",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True) # Changed from unsafe_allow_stdio to unsafe_allow_html

# --- 4. UI ELEMENTS ---
st.title("📄 EDUSCAN: Intelligent Marksheet Extraction")
st.subheader("Automate academic data entry using OCR & NLP")
st.divider()

with st.sidebar:
    st.header("Control Panel")
    st.write("Upload scanned marksheets to extract names and roll numbers.")
    if st.button("♻️ Clear Server Cache"):
        st.cache_resource.clear()
        st.rerun()

# --- 5. BATCH PROCESSING LOGIC ---
uploaded_files = st.file_uploader(
    "Upload Marksheet Images (JPG/PNG)", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Start Batch Processing"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Ensure a temporary directory exists
        temp_dir = "temp_processing"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        for i, file in enumerate(uploaded_files):
            # 1. Save uploaded file temporarily
            raw_path = os.path.join(temp_dir, f"raw_{file.name}")
            clean_path = os.path.join(temp_dir, f"clean_{file.name}")
            
            with open(raw_path, "wb") as f:
                f.write(file.getbuffer())
            
            status_text.text(f"Processing: {file.name}...")

            try:
                # 2. Preprocess (Cleaning the image)
                cleaned_img = get_clean_marksheet(raw_path)
                cv2.imwrite(clean_path, cleaned_img)
                
                # 3. Extract (OCR + NLP)
                # Note: extract_student_info should handle the OCR call internally
                data = extract_student_info(clean_path)
                
                # Add metadata
                data['Filename'] = file.name
                results.append(data)
                
                st.success(f"✅ **{file.name}**: Extracted {data.get('NAME', 'Unknown')}")
            
            except Exception as e:
                st.error(f"❌ Error in {file.name}: {e}")
            
            finally:
                # 4. Cleanup temporary files
                if os.path.exists(raw_path): os.remove(raw_path)
                if os.path.exists(clean_path): os.remove(clean_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("✨ All files processed!")

        # --- 6. DISPLAY RESULTS & DOWNLOAD ---
        if results:
            st.divider()
            st.header("📊 Extracted Data")
            df = pd.DataFrame(results)
            
            # Reorder columns to make 'Filename' the first column
            if 'Filename' in df.columns:
                cols = ['Filename'] + [c for c in df.columns if c != 'Filename']
                df = df[cols]
            
            st.dataframe(df, use_container_width=True)
            
            # Export to Excel
            output = io.BytesIO()
            try:
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='EDUSCAN_Data')
                
                st.download_button(
                    label="📥 Download Excel Report",
                    data=output.getvalue(),
                    file_name="EDUSCAN_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.warning(f"Excel export failed (Check if openpyxl is installed): {e}")
