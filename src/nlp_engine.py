import difflib
import re

class EDUSCAN_NLP:
    def __init__(self):
        # Database of valid candidates for fuzzy matching
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        # Words to ignore when searching for a name - tightened to exclude marksheet headers
        self.banned_words = {
            "MOTHER", "FATHER", "ROLL", "DATE", "SCHOOL", "BOARD", "EXAMINATION", 
            "SECONDARY", "MARKS", "STATEMENT", "CERTIFICATE", "CUM", "SENIOR", "DELHI"
        }

    def fuzzy_correction(self, name):
        """Finds the closest match from known_names to correct OCR typos."""
        matches = difflib.get_close_matches(name, self.known_names, n=1, cutoff=0.3)
        return matches[0] if matches else name

    def classify_text(self, text_list):
        # 1. Skip the first few lines to avoid headers and watermark noise
        # This is where 'FARINMHT HZ' likely lives
        filtered_list = text_list[6:] if len(text_list) > 6 else text_list
    
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        
        # 2. Clean lines from the FILTERED list, not the raw list
        clean_list = [t.strip() for t in filtered_list if len(t.strip()) > 3]

        # --- 3. NAME DETECTION (Brute Force) ---
        for text in clean_list:
            upper_text = text.upper()
            words = upper_text.split()
            
            # A candidate name is usually 2 to 4 words long
            if 2 <= len(words) <= 4:
                # Filter out lines that contain common board headers
                if any(b in upper_text for b in self.banned_words):
                    continue
                
                # If the line is strictly letters and spaces, it's our candidate
                if re.match(r'^[A-Z\s]+$', upper_text):
                    results["NAME"] = self.fuzzy_correction(upper_text)
                    break 

        # --- 4. ROLL NUMBER DETECTION ---
        # We scan the full text for Roll Numbers since they can be anywhere
        for text in text_list:
            roll_match = re.search(r'\b\d{7,8}\b', text)
            if roll_match:
                val = roll_match.group()
                # Filter out dates (2005/2021) and Serial Nos (starting with 027)
                if not val.startswith("027") and not val.endswith(("2005", "2021")):
                    results["ROLL_NO"] = val
                    break

        return results
