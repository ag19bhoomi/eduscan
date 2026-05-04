import spacy
import difflib
import re

# Load SpaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback if model isn't loaded
    pass

class EDUSCAN_NLP:
    def __init__(self):
        # Your existing lists
        self.known_names = ["BHOOMI AGARWAL", "HIMANSHI MAHAVAR", "VISHVMOHAN PARASHAR", "LAKSHY AGGARWAL", "PRAJJVAL RAWAT"]
        self.banned = {"certify", "that", "this", "is", "to", "board", "secondary", "examination", "school", "roll", "no"}
        
        # New flexible keywords
        self.name_keywords = ['name', 'student', 'candidate', 'examinee', 'name of student']
        self.roll_keywords = ['roll', 'enrollment', 'seat no', 'reg', 'index', 'roll no']

    def classify_text(self, text_list):
        results = {"NAME": "Not Found", "ROLL_NO": "Not Found"}
        
        # Clean the list for line-by-line heuristic processing
        clean_list = [t.strip() for t in text_list if len(t.strip()) > 3]
        # Create a lowercase full string for global pattern searching
        full_text = " ".join(text_list).lower()

        # --- 1. GLOBAL KEYWORD SEARCH (New Flexible Logic) ---
        # Search for Name
        for kw in self.name_keywords:
            if kw in full_text:
                pattern = f"{kw}\s*[:\-]?\s*([a-zA-Z\s]{{3,30}})"
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    results["NAME"] = match.group(1).strip().upper()
                    break

        # Search for Roll No
        for kw in self.roll_keywords:
            if kw in full_text:
                pattern = f"{kw}\s*[:\-]?\s*(\d{{4,20}})"
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    results["ROLL_NO"] = match.group(1).strip()
                    break

        # --- 2. HEURISTIC ANCHOR SEARCH (Your Original Logic) ---
        # If the global search didn't find a high-quality name, try the "CERTIFY" anchor
        if results["NAME"] == "Not Found" or len(results["NAME"].split()) < 2:
            for i, text in enumerate(clean_list):
                upper_text = text.upper()
                if "CERTIFY" in upper_text or "THAT" in upper_text:
                    for offset in range(1, 4):
                        if i + offset < len(clean_list):
                            candidate = clean_list[i + offset]
                            words = set(candidate.lower().split())
                            if not (words & self.banned) and len(candidate.split()) >= 2:
                                results["NAME"] = candidate.upper()
                                break

        # --- 3. ROBUST ROLL NUMBER REFINEMENT ---
        # Apply your ghost character fix and exclusions to the Roll No
        for text in clean_list:
            digits_only = re.sub(r'\D', '', text)
            
            # Ghost character fix
            if len(digits_only) == 9 and digits_only.startswith('1'):
                digits_only = digits_only[1:]

            if len(digits_only) == 8:
                # Exclusions
                if digits_only.startswith("027"): continue # Serial No
                if digits_only.endswith(("2004", "2005", "2006", "2007")): continue # DOB
                
                # High confidence if 'ROLL' is in the line
                if "ROLL" in text.upper() or "NO" in text.upper():
                    results["ROLL_NO"] = digits_only
                    break
                # Fallback if nothing found yet
                elif results["ROLL_NO"] == "Not Found":
                    results["ROLL_NO"] = digits_only

        # --- 4. FUZZY CORRECTION ---
        # Final pass to clean up OCR errors in the name
        if results["NAME"] != "Not Found":
            results["NAME"] = self.fuzzy_correction(results["NAME"])

        return results

    def fuzzy_correction(self, name):
        matches = difflib.get_close_matches(name, self.known_names, n=1, cutoff=0.6)
        return matches[0] if matches else name
