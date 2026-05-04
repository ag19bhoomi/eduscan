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
        # Clean lines and remove small artifacts
        clean_list = [t.strip() for t in text_list if len(t.strip()) > 2]
        
        # --- 1. THE "CERTIFY" ANCHOR (Optimized for CBSE) ---
        for i, text in enumerate(clean_list):
            # Flexible check for "This is to certify that"
            if re.search(r'certi[fily][fily]', text, re.IGNORECASE):
                # Check current line (after the phrase)
                potential = re.sub(r'(?i).*certi[fily][fily]\s+that\s*', '', text).strip()
                
                # If name isn't on the same line, check the next two lines
                candidates = [potential]
                if i + 1 < len(clean_list): candidates.append(clean_list[i+1])
                if i + 2 < len(clean_list): candidates.append(clean_list[i+2])
                
                for cand in candidates:
                    # A name should be 2-3 words and not contain banned keywords
                    if len(cand.split()) >= 2 and not any(b in cand.upper() for b in self.banned):
                        results["NAME"] = cand.upper()
                        break
                if results["NAME"] != "Not Found": break

        # --- 2. ROLL NUMBER FILTERING ---
        for text in clean_list:
            # Look for 7 or 8 digit numbers
            nums = re.findall(r'\b\d{7,8}\b', text)
            for n in nums:
                # CRITICAL: Ignore Serial Numbers starting with 027
                if n.startswith("027"):
                    continue
                # If we find a valid number, assign it
                results["ROLL_NO"] = n
                # If the word 'ROLL' is nearby, we are certain
                if "ROLL" in text.upper():
                    break

        # --- 3. FUZZY MATCHING (Safety Net) ---
        if results["NAME"] != "Not Found":
            # Strip non-alphabetic noise
            results["NAME"] = re.sub(r'[^A-Z\s]', '', results["NAME"]).strip()
            # Find closest match from your list
            matches = difflib.get_close_matches(results["NAME"], self.known_names, n=1, cutoff=0.4)
            if matches:
                results["NAME"] = matches[0]

        return results
