import os
import re
import csv
import shutil
import hashlib
from typing import List, Dict, Tuple, Optional
import docx

# Regex for Samputa number (Kannada or Arabic digits, optional dash)
SAMPUTA_RE = re.compile(r"ಸಂಪುಟ\s*[-–]?\s*([೦-೯0-9]+)")

KAN_DIGIT_MAP = {
    "೦": "0", "೧": "1", "೨": "2", "೩": "3", "೪": "4",
    "೫": "5", "೬": "6", "೭": "7", "೮": "8", "೯": "9",
}

def normalize_digits(text: str) -> str:
    """Convert Kannada digits in string to English digits."""
    return "".join(KAN_DIGIT_MAP.get(ch, ch) for ch in text)

def stable_id(author: str) -> int:
    """Generate stable numeric ID for author based on hashing."""
    return int(hashlib.md5(author.encode("utf-8")).hexdigest(), 16) % 100000

def process_docx_file(file_path: str,
                      author_id_map: Dict[str, int]) -> Tuple[Optional[List[Dict]], Optional[List[Dict]]]:
    """
    Extract Tippani and Arthakosha from one DOCX file.
    Returns (tippani_rows, arthakosha_rows) or (None, None) if none found.
    """
    doc = docx.Document(file_path)

    samputa_sankhye = None
    tatvapada_author_id = None
    author_name = None

    tippani_rows = []
    arthakosha_rows = []
    current_section = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect samputa number and normalize digits
        if text.startswith("ಸಂಪುಟ"):
            m = SAMPUTA_RE.match(text)
            if m:
                samputa_sankhye = normalize_digits(m.group(1))
            continue

        # Detect author line with "ತತ್ವಪದಗಳು"
        if "ತತ್ವಪದಗಳು" in text:
            author_name = text
            if text not in author_id_map:
                author_id_map[text] = stable_id(text)
            tatvapada_author_id = author_id_map[text]
            continue

        # Only set current_section if not set yet (file has either Tippani or Arthakosha)
        if current_section is None:
            if text.startswith("ಟಿಪ್ಪಣಿ"):
                current_section = "tippani"
                continue
            elif text.startswith("ಅರ್ಥಕೋಶ"):
                current_section = "arthakosha"
                continue
        else:
            # Section already set, ignore other section markers

            # Parse lines depending on current_section
            if current_section == "tippani":
                if "-" in text or "–" in text:
                    parts = re.split(r"[-–]", text, maxsplit=1)
                    if len(parts) == 2:
                        title, content = parts
                        tippani_rows.append({
                            "samputa_sankhye": samputa_sankhye,
                            "author_name": author_name,
                            "tatvapada_author_id": tatvapada_author_id,
                            "tippani_title": title.strip(),
                            "tippani": content.strip()
                        })
            elif current_section == "arthakosha":
                if "-" in text or "–" in text:
                    parts = re.split(r"[-–]", text, maxsplit=1)
                    if len(parts) == 2:
                        word, meaning = parts
                        arthakosha_rows.append({
                            "samputa_sankhye": samputa_sankhye,
                            "author_name": author_name,
                            "word": word.strip(),
                            "meaning": meaning.strip()
                        })

    if not tippani_rows and not arthakosha_rows:
        print(f"Skipping {os.path.basename(file_path)} (no Tippani or Arthakosha found)")
        return None, None

    return tippani_rows, arthakosha_rows

def process_folder(input_folder: str,
                   tippani_output_folder: str,
                   arthakosha_output_folder: str):
    """
    Process DOCX files and save separate Tippani and Arthakosha CSVs in respective folders,
    creating folders if needed.
    """
    author_id_map: Dict[str, int] = {}

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".docx"):
            filepath = os.path.join(input_folder, filename)
            tippani_rows, arthakosha_rows = process_docx_file(filepath, author_id_map)

            if tippani_rows:
                os.makedirs(tippani_output_folder, exist_ok=True)
                csv_path = os.path.join(tippani_output_folder, f"{os.path.splitext(filename)[0]}_tippani.csv")
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    fieldnames = ["samputa_sankhye", "author_name", "tatvapada_author_id", "tippani_title", "tippani"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(tippani_rows)
                print(f"Wrote Tippani CSV: {csv_path}")

            if arthakosha_rows:
                os.makedirs(arthakosha_output_folder, exist_ok=True)
                csv_path = os.path.join(arthakosha_output_folder, f"{os.path.splitext(filename)[0]}_arthakosha.csv")
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    fieldnames = ["samputa_sankhye", "author_name", "word", "meaning"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(arthakosha_rows)
                print(f"Wrote Arthakosha CSV: {csv_path}")

if __name__ == "__main__":
    input_folder = input("Enter the folder path containing DOCX files: ").strip()
    output_folder = "output_tippani_arthakosha"
    tippani_output_folder = os.path.join(output_folder, "output_tippani")
    arthakosha_output_folder = os.path.join(output_folder, "output_arthakosha")

    if not os.path.isdir(input_folder):
        print("Invalid folder path. Please try again.")
    else:
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)  # clean old run

        process_folder(input_folder, tippani_output_folder, arthakosha_output_folder)
        print("✅ Processing completed.")
