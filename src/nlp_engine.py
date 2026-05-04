import spacy
import difflib
import re

class EDUSCAN_NLP:
    def __init__(self):
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        # Words we definitely don't want in a name
        self.banned = {"MOTHER", "FATHER", "GUARDIAN", "SCHOOL", "BOARD", "EXAMINATION", "SECONDARY"}

    def classify_text(self, text_list):
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        full_text_raw = " ".join(text_list)
        clean_list = [t.strip() for t in text_list]

        # --- 1. CBSE SPECIFIC ANCHOR (Highest Priority) ---
        # Look for the line that starts with "This is to certify that"
        for i, text in enumerate(clean_list):
            if "certify that" in text.lower():
                # Usually, the name is either in the same line or the very next one
                # Remove the trigger phrase to see if name is on the same line
                potential = re.sub(r'(?i)This is to certify that', '', text).strip()
                
                if len(potential) > 5:
                    candidate = potential
                elif i + 1 < len(clean_list):
                    candidate = clean_list[i+1]
                
                # Verify it's not a banned line
                if not any(word in candidate.upper() for word in self.banned):
                    results["NAME"] = candidate.upper()
                    break

        # --- 2. ROLL NUMBER LOGIC (Optimized) ---
        for text in clean_list:
            # Look for 7 or 8 digit numbers
            nums = re.findall(r'\b\d{7,8}\b', text)
            if nums:
                # If "ROLL" is in the same line, it's definitely the one
                if "ROLL" in text.upper():
                    results["ROLL_NO"] = nums[0]
                    break
                # Fallback to the first 7-8 digit number found
                if results["ROLL_NO"] == "Not Found":
                    results["ROLL_NO"] = nums[0]

        # --- 3. GENERAL NAME SEARCH (Only if Anchor failed) ---
        if results["NAME"] == "Not Found":
            pattern = r"(?:Candidate's Name|Name of Student)\s*[:\-]?\s*([A-Z\s]{3,30})"
            match = re.search(pattern, full_text_raw, re.IGNORECASE)
            if match:
                results["NAME"] = match.group(1).strip().upper()

        # --- 4. FUZZY CORRECTION & CLEANUP ---
        if results["NAME"] != "Not Found":
            # Remove any trailing junk OCR might have picked up
            results["NAME"] = re.sub(r'[^A-Z\s]', '', results["NAME"]).strip()
            # Correct against your list
            results["NAME"] = self.fuzzy_correction(results["NAME"])

        return results

    def fuzzy_correction(self, name):
        matches = difflib.get_close_matches(name, self.known_names, n=1, cutoff=0.5)
        return matches[0] if matches else name
