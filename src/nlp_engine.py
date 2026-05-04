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
        clean_list = [t.strip() for t in text_list]
        
        for i, text in enumerate(clean_list):
            upper_text = text.upper()
            
            # 1. FIXED NAME ANCHOR: Search for 'certify that' and grab the next line
            if "CERTIFY" in upper_text:
                if i + 1 < len(clean_list):
                    candidate = clean_list[i+1].upper()
                    # Ignore the header if it was accidentally grabbed
                    if "MARKS" not in candidate and "CERTIFICATE" not in candidate:
                        results["NAME"] = self.fuzzy_correction(candidate)
                        break

            # 2. FIXED ROLL NO: Find 7-8 digits that ARE NOT dates
            roll_match = re.search(r'\b\d{7,8}\b', text)
            if roll_match:
                candidate_roll = roll_match.group()
                # Filter out likely dates (2021, 2005) or Serial Nos (027)
                if not candidate_roll.endswith(("2021", "2005", "2006")) and not candidate_roll.startswith("027"):
                    results["ROLL_NO"] = candidate_roll
        
        return results
