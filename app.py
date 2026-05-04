import streamlit as st
import pandas as pd
import cv2
import numpy as np
import os
import sys
import io
import json
import tempfile

# --- 1. HELPERS & EXPORT LOGIC ---
def create_labeling_task(results_list):
    """Formats all current batch results into a JSON for labeling tools."""
    return json.dumps(results_list, indent=4)

# --- 2. PATH INJECTION ---
# Ensures the app can find modules in the 'src' folder
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

# --- 3. APP CONFIGURATION ---
st.set_page_config(
    page_title="EDUSCAN | AI Marksheet Automation",
    page_icon="📄",
    layout="wide"
)

# Initialize Session State
if 'final_results' not in st.session_state:
    st.session_state.final_results = []

# --- 4. SIDEBAR (Training Lab & Controls) ---
with st.sidebar:
    st.header("🧪 Training Lab")
    if st.session_state.final_results:
        st.info("Download this batch to fix 'Not Found' errors and train the model.")
        json_data = create_labeling_task(st.session_state.final_results)
        st.download_button(
            label="📥 Export Batch for Training",
            data=json_data,
            file_name="eduscan_training_samples.json",
            mime="application/json"
        )
    else:
        st.write("Process files to enable training export.")
    
    st.divider()
    if st.button("♻️ Reset App & Cache"):
        st.cache_resource.clear()
        st.session_state.final_results = []
        st.rerun()

# --- 5. MAIN UI ---
st.title("📄 EDUSCAN: Intelligent Marksheet Extraction")
st.markdown("### Automate academic data entry using OCR & NLP")
st.divider()

uploaded_files = st.file_uploader(
    "Upload Marksheet Images (JPG/PNG)", 
    type=['png', 'jpg', 'jpeg'], 
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🚀 Start Batch Processing"):
        current_batch = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing: {file.name}...")
            
            # Use tempfile to avoid directory permission issues
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp_raw:
                tmp_raw.write(file.getbuffer())
                raw_path = tmp_raw.name
            
            try:
                # 1. Preprocess
                cleaned_img = get_clean_marksheet(raw_path)
                
                # 2. Save cleaned image temporarily for extraction
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_clean:
                    clean_path = tmp_clean.name
                    cv2.imwrite(clean_path, cleaned_img)
                
                # 3. Extract (OCR + NLP)
                data = extract_student_info(clean_path)
                
                # 4. Store metadata
                data['Filename'] = file.name
                current_batch.append(data)
                
                if data.get('NAME') == "Not Found":
                    st.warning(f"⚠️ **{file.name}**: Name not detected.")
                else:
                    st.success(f"✅ **{file.name}**: {data.get('NAME')}")
                
                # Cleanup clean_path
                if os.path.exists(clean_path): os.remove(clean_path)

            except Exception as e:
                st.error(f"❌ Error in {file.name}: {str(e)}")
            
            finally:
                # Cleanup raw_path
                if os.path.exists(raw_path): os.remove(raw_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        st.session_state.final_results = current_batch
        status_text.text("✨ Batch Processing Complete!")

# --- 6. DISPLAY RESULTS ---
if st.session_state.final_results:
    st.divider()
    st.header("📊 Extracted Data")
    
    df = pd.DataFrame(st.session_state.final_results)
    
    # Ensure Filename is the first column
    cols = ['Filename'] + [c for c in df.columns if c != 'Filename']
    df = df[cols]
    
    st.dataframe(df, use_container_width=True)
    
    # Excel Export
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='ExtractedData')
        
        st.download_button(
            label="📥 Download Excel Report",
            data=output.getvalue(),
            file_name="EDUSCAN_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Excel generation failed: {e}")
