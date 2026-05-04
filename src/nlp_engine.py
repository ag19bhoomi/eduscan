import difflib
import re

class EDUSCAN_NLP:
    def __init__(self):
        # Database of valid candidates for fuzzy matching
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        # Words to ignore when searching for a name
        self.banned_words = {"MOTHER", "FATHER", "ROLL", "DATE", "SCHOOL", "BOARD", "EXAMINATION", "SECONDARY", "MARKS", "STATEMENT", "CERTIFICATE"}

    def fuzzy_correction(self, name):
        """Lowered cutoff to 0.3 to catch heavily garbled OCR results."""
        matches = difflib.get_close_matches(name, self.known_names, n=1, cutoff=0.3)
        return matches[0] if matches else name

    def classify_text(self, text_list):
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        
        # Clean lines and remove small noise
        clean_list = [t.strip() for t in text_list if len(t.strip()) > 3]

        # --- 1. NAME DETECTION (Brute Force) ---
        for text in clean_list:
            upper_text = text.upper()
            words = upper_text.split()
            
            # A candidate name is usually 2 to 4 words long
            if 2 <= len(words) <= 4:
                # If the line contains a banned word (like 'BOARD'), skip it
                if any(b in upper_text for b in self.banned_words):
                    continue
                
                # If the line is only letters/spaces, it's likely the student name
                if re.match(r'^[A-Z\s]+$', upper_text):
                    results["NAME"] = self.fuzzy_correction(upper_text)
                    break 

        # --- 2. ROLL NUMBER DETECTION ---
        for text in clean_list:
            # Look for 7 or 8 consecutive digits
            roll_match = re.search(r'\b\d{7,8}\b', text)
            if roll_match:
                val = roll_match.group()
                # Filter out obvious dates or serial numbers (027...)
                if not val.startswith("027") and not val.endswith(("2005", "2021")):
                    results["ROLL_NO"] = val
                    break

        return results
