import json
import base64
import sys
import os
import io
import streamlit as st
import pandas as pd
import cv2
import numpy as np

# --- 1. HELPERS ---
def create_labeling_task(results_list):
    """Formats all current batch results for export."""
    return json.dumps(results_list, indent=4)

# --- 2. FORCE PATH INJECTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    from preprocess import get_clean_marksheet
    from extract import extract_student_info
except ImportError as e:
    st.error(f"❌ Critical Import Error: {e}")
    st.stop()

# --- 3. APP CONFIG ---
st.set_page_config(page_title="EDUSCAN | AI Marksheet Automation", page_icon="📄", layout="wide")

# Initialize Session State for results if it doesn't exist
if 'final_results' not in st.session_state:
    st.session_state.final_results = []

# --- 4. SIDEBAR (Training Lab) ---
with st.sidebar:
    st.header("🧪 Training Lab")
    if st.session_state.final_results:
        st.info("Errors found? Export this batch to 'teach' the model.")
        json_data = create_labeling_task(st.session_state.final_results)
        st.download_button(
            label="📥 Export Batch for Training",
            data=json_data,
            file_name="eduscan_training_batch.json",
            mime="application/json"
        )
    else:
        st.write("No data processed yet.")
    
    st.divider()
    if st.button("♻️ Clear Server Cache"):
        st.cache_resource.clear()
        st.session_state.final_results = []
        st.rerun()

# --- 5. MAIN UI ---
st.title("📄 EDUSCAN: Intelligent Marksheet Extraction")
st.divider()

uploaded_files = st.file_uploader("Upload Marksheet Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("🚀 Start Batch Processing"):
        current_batch = []
        progress_bar = st.progress(0)
        
        temp_dir = "temp_processing"
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)

        for i, file in enumerate(uploaded_files):
            raw_path = os.path.join(temp_dir, f"raw_{file.name}")
            clean_path = os.path.join(temp_dir, f"clean_{file.name}")
            
            with open(raw_path, "wb") as f:
                f.write(file.getbuffer())

            try:
                # Process
                cleaned_img = get_clean_marksheet(raw_path)
                cv2.imwrite(clean_path, cleaned_img)
                data = extract_student_info(clean_path)
                
                # Metadata
                data['Filename'] = file.name
                current_batch.append(data)
                st.success(f"✅ {file.name}: {data.get('NAME', 'Not Found')}")
            
            except Exception as e:
                st.error(f"❌ Error in {file.name}: {e}")
            finally:
                if os.path.exists(raw_path): os.remove(raw_path)
                if os.path.exists(clean_path): os.remove(clean_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Save to Session State so the sidebar can see it!
        st.session_state.final_results = current_batch

# --- 6. DISPLAY RESULTS ---
if st.session_state.final_results:
    st.divider()
    df = pd.DataFrame(st.session_state.final_results)
    
    # Column Reordering
    cols = ['Filename'] + [c for c in df.columns if c != 'Filename']
    st.dataframe(df[cols], use_container_width=True)

    # Excel Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button(label="📥 Download Excel Report", data=output.getvalue(), file_name="EDUSCAN_Report.xlsx")
