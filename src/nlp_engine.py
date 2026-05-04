import difflib
import re

class EDUSCAN_NLP:
    def __init__(self):
        # Database of valid candidates
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        # Words to ignore when searching for a name
        self.banned = {"MOTHER", "FATHER", "GUARDIAN", "SCHOOL", "BOARD", "EXAMINATION", "SECONDARY", "PRIVATE"}
    def classify_text(self, text_list):
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        
        # Words we know are NOT names
        banned_words = {"MOTHER", "FATHER", "ROLL", "DATE", "SCHOOL", "BOARD", "EXAMINATION", "SECONDARY", "MARKS", "STATEMENT", "CERTIFICATE"}
        
        clean_list = [t.strip() for t in text_list if len(t.strip()) > 3]

        # --- 1. IMPROVED NAME DETECTION ---
        for text in clean_list:
            upper_text = text.upper()
            words = upper_text.split()
            
            # A candidate name is usually 2 or 3 words long
            if 2 <= len(words) <= 4:
                # If the line contains a banned word, skip it
                if any(b in upper_text for b in banned_words):
                    continue
                
                # If the line is all letters (no numbers), it's likely a name
                if re.match(r'^[A-Z\s]+$', upper_text):
                    results["NAME"] = self.fuzzy_correction(upper_text)
                    break # Stop at the first valid name found

        # --- 2. ROLL NUMBER DETECTION ---
        for text in clean_list:
            # Look for 7 or 8 digits
            roll_match = re.search(r'\b\d{7,8}\b', text)
            if roll_match:
                val = roll_match.group()
                # Exclude obvious dates or serial numbers
                if not val.startswith("027") and not val.endswith(("2005", "2021")):
                    results["ROLL_NO"] = val
                    break

        return results
