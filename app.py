import sys
import os
import io

# --- 1. FORCE THE PATH ---
# We are telling Python exactly where to look for your files
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.append(src_path)

import streamlit as st
import pandas as pd
import cv2
import numpy as np

# --- 2. DIRECT IMPORTS ---
# Since we added 'src' to the path above, we import directly from the filenames
try:
    from extract import extract_student_info
    from preprocess import preprocess_image
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
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
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_stdio=True)

# --- 4. UI ELEMENTS ---
st.title("📄 EDUSCAN: Intelligent Marksheet Extraction")
st.subheader("Automate academic data entry using OCR & NLP")
st.divider()

with st.sidebar:
    st.header("Settings")
    st.info("Upload scanned marksheets (JPG/PNG) to extract student names and roll numbers into Excel.")
    if st.button("Clear Cache"):
        st.cache_resource.clear()
        st.rerun()

# --- 5. FILE UPLOADER ---
uploaded_files = st.file_uploader(
    "Upload Marksheet Images", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Start Batch Processing"):
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create a temporary directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")

        for i, file in enumerate(uploaded_files):
            # Save uploaded file to a temporary path
            t_path = os.path.join("temp", file.name)
            with open(t_path, "wb") as f:
                f.write(file.getbuffer())
            
            status_text.text(f"Processing: {file.name}...")

            try:
                # The extraction function handles preprocessing and OCR internally
                data = extract_student_info(t_path)
                data['Filename'] = file.name
                results.append(data)
                
                st.success(f"Extracted: **{data.get('NAME', 'Unknown')}** (Roll: {data.get('ROLL_NO', 'N/A')})")
            
            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
            
            finally:
                # Cleanup temp file
                if os.path.exists(t_path):
                    os.remove(t_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("✅ All files processed!")

        # --- 6. RESULTS & EXPORT ---
        if results:
            st.divider()
            st.header("📊 Extraction Results")
            df = pd.DataFrame(results)
            
            # Reorder columns to put Filename first
            cols = ['Filename'] + [c for c in df.columns if c != 'Filename']
            df = df[cols]
            
            st.dataframe(df, use_container_width=True)
            
            # Excel Download logic
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Marksheet_Data')
            
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name="EDUSCAN_Extraction_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
