import spacy
import difflib
import re

nlp = spacy.load("en_core_web_sm")

class EDUSCAN_NLP:
    def __init__(self):
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        self.banned = {"certify", "that", "this", "is", "to", "board", "secondary", "examination", "school", "roll", "no"}

    def classify_text(self, text_list):
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        clean_list = [t.strip() for t in text_list if len(t.strip()) > 3]

        for i, text in enumerate(clean_list):
            upper_text = text.upper()

            # --- NAME LOGIC ---
            if "CERTIFY" in upper_text or "THAT" in upper_text:
                for offset in range(1, 4):
                    if i + offset < len(clean_list):
                        candidate = clean_list[i + offset]
                        words = set(candidate.lower().split())
                        if not (words & self.banned) and len(candidate.split()) >= 2:
                            results["NAME"] = self.fuzzy_correction(candidate.upper())
                            break

            # --- ROBUST ROLL NUMBER LOGIC ---
            # Step 1: Extract all digits from current block
            digits_only = re.sub(r'\D', '', text)
            
            # Step 2: Ghost character fix (trim 9 digits starting with 1 to 8 digits)
            if len(digits_only) == 9 and digits_only.startswith('1'):
                digits_only = digits_only[1:]

            # Step 3: Check if it's a valid 8-digit number
            if len(digits_only) == 8:
                # Filter out the Serial Number (starts with 027)
                if digits_only.startswith("027"):
                    continue
                
                # Filter out Date of Birth (ends with 2005, 2006, etc.)
                if digits_only.endswith(("2004", "2005", "2006", "2007")):
                    continue

                # If we already found a Roll No near the word "ROLL", don't overwrite it
                # Otherwise, this acts as our 'Global Search' fallback
                if results["ROLL_NO"] == "Not Found":
                    results["ROLL_NO"] = digits_only
                
                # If the word 'ROLL' is actually in the text, this is a high-confidence match
                if "ROLL" in upper_text or "NO" in upper_text:
                    results["ROLL_NO"] = digits_only

        return results

    def fuzzy_correction(self, name):
        matches = difflib.get_close_matches(name, self.known_names, n=1, cutoff=0.6)
        return matches[0] if matches else name