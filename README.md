# EDUSCAN: Intelligent Marksheet Automation

EDUSCAN is an automated data extraction system designed to process academic marksheets using **Computer Vision**, **OCR**, and **Natural Language Processing (NLP)**. It eliminates manual data entry by converting scanned images into structured Excel reports with high precision.

##  Live Demo
[Check out the Live App on Streamlit Cloud](https://share.streamlit.io/) *(Replace this with your actual URL once deployed)*

##  Key Features
- **Batch Processing:** Upload multiple marksheets simultaneously.
- **Advanced Preprocessing:** Uses OpenCV for noise reduction and contrast enhancement to improve OCR accuracy.
- **Intelligent Extraction:** Employs **EasyOCR** and custom **NLP Heuristics** to distinguish between names, roll numbers, and "noise" (like dates or serial numbers).
- **Fuzzy Matching:** Utilizes `difflib` to correct OCR misspellings against a known database of student names.
- **Excel Export:** Generates a professional, downloadable report in `.xlsx` format.

## Tech Stack
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Image Processing:** [OpenCV](https://opencv.org/)
- **OCR Engine:** [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- **NLP Layer:** [SpaCy](https://spacy.io/) & Regex
- **Data Handling:** [Pandas](https://pandas.pydata.org/)

## Project Structure
```text
eduscan/
├── app.py              # Main Streamlit UI and app logic
├── requirements.txt    # List of dependencies for cloud deployment
└── src/                # Backend Logic Folder
    ├── __init__.py     # Makes src a Python package
    ├── preprocess.py   # OpenCV image cleaning logic
    ├── extract.py      # OCR execution layer
    └── nlp_engine.py   # High-precision NLP and Heuristic filtering
