import os
import re
import csv
import shutil
import hashlib
from typing import List, Dict, Tuple, Optional
import docx

# ---------------- Constants ----------------
SAMPUTA_RE = re.compile(r"ಸಂಪುಟ\s*[-–]?\s*([೦-೯0-9]+)")

KAN_DIGIT_MAP = {
    "೦": "0", "೧": "1", "೨": "2", "೩": "3", "೪": "4",
    "೫": "5", "೬": "6", "೭": "7", "೮": "8", "೯": "9",
}

# ---------------- Utilities ----------------
def normalize_digits(text: str) -> str:
    return "".join(KAN_DIGIT_MAP.get(ch, ch) for ch in text)

def stable_id(author: str) -> int:
    return int(hashlib.md5(author.encode("utf-8")).hexdigest(), 16) % 100000

# ---------------- DOCX Processing ----------------
def process_docx_file(file_path: str,
                      author_id_map: Dict[str, int]) -> Tuple[Optional[List[Dict]], Optional[List[Dict]]]:
    doc = docx.Document(file_path)

    samputa_sankhye = None
    tatvapada_author_id = None
    author_name = None

    padavivarana_rows = []
    arthakosha_rows = []
    current_section = None
    last_row = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect samputa number
        if text.startswith("ಸಂಪುಟ"):
            m = SAMPUTA_RE.match(text)
            if m:
                samputa_sankhye = normalize_digits(m.group(1))
            continue

        # Detect author line
        if "ತತ್ವಪದಗಳು" in text:
            author_name = text
            if text not in author_id_map:
                author_id_map[text] = stable_id(text)
            tatvapada_author_id = author_id_map[text]
            continue

        # Detect section headers
        if text.startswith("ಟಿಪ್ಪಣಿ") or text.startswith("ಪಾರಿಭಾಷಿಕ"):
            current_section = "padavivarana"
            last_row = None
            continue
        elif text.startswith("ಅರ್ಥಕೋಶ"):
            current_section = "arthakosha"
            last_row = None
            continue

        # ---------------- Padavivarana ----------------
        if current_section == "padavivarana":
            if "-" in text or "–" in text:
                parts = re.split(r"[-–]", text, maxsplit=1)
                if len(parts) == 2:
                    title, content = parts
                    last_row = {
                        "samputa_sankhye": samputa_sankhye,
                        "author_name": author_name,
                        "tatvapada_author_id": tatvapada_author_id,
                        "paribhashika_padavivarana_title": title.strip(),
                        "paribhashika_padavivarana_content": content.strip()
                    }
                    padavivarana_rows.append(last_row)
            elif last_row:
                last_row["paribhashika_padavivarana_content"] += " " + text

        # ---------------- Arthakosha ----------------
        elif current_section == "arthakosha":
            if "-" in text or "–" in text:
                parts = re.split(r"[-–]", text, maxsplit=2)
                if len(parts) == 2:
                    word, meaning = parts
                    last_row = {
                        "author_id": tatvapada_author_id,
                        "author_name": author_name,
                        "samputa": samputa_sankhye,
                        "title": None,
                        "word": word.strip(),
                        "meaning": meaning.strip(),
                        "notes": None
                    }
                    arthakosha_rows.append(last_row)
                elif len(parts) == 3:
                    title, word, meaning = parts
                    last_row = {
                        "author_id": tatvapada_author_id,
                        "author_name": author_name,
                        "samputa": samputa_sankhye,
                        "title": title.strip(),
                        "word": word.strip(),
                        "meaning": meaning.strip(),
                        "notes": None
                    }
                    arthakosha_rows.append(last_row)
            elif last_row:
                last_row["meaning"] += " " + text

    if not padavivarana_rows and not arthakosha_rows:
        print(f"Skipping {os.path.basename(file_path)} (no Padavivarana or Arthakosha found)")
        return None, None

    return padavivarana_rows, arthakosha_rows

# ---------------- Folder Processing ----------------
def process_folder(input_folder: str,
                   padavivarana_output_folder: str,
                   arthakosha_output_folder: str):
    author_id_map: Dict[str, int] = {}

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".docx"):
            filepath = os.path.join(input_folder, filename)
            padavivarana_rows, arthakosha_rows = process_docx_file(filepath, author_id_map)

            # Padavivarana CSV
            if padavivarana_rows:
                os.makedirs(padavivarana_output_folder, exist_ok=True)
                csv_path = os.path.join(padavivarana_output_folder, f"{os.path.splitext(filename)[0]}_padavivarana.csv")
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    fieldnames = [
                        "samputa_sankhye",
                        "author_name",
                        "tatvapada_author_id",
                        "paribhashika_padavivarana_title",
                        "paribhashika_padavivarana_content"
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(padavivarana_rows)
                print(f"Wrote Padavivarana CSV: {csv_path}")

            # Arthakosha CSV with requested columns order
            if arthakosha_rows:
                os.makedirs(arthakosha_output_folder, exist_ok=True)
                csv_path = os.path.join(arthakosha_output_folder, f"{os.path.splitext(filename)[0]}_arthakosha.csv")
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    fieldnames = [
                        "author_id",
                        "author_name",
                        "samputa",
                        "title",
                        "word",
                        "meaning",
                        "notes"
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(arthakosha_rows)
                print(f"Wrote Arthakosha CSV: {csv_path}")

# ---------------- Main ----------------
if __name__ == "__main__":
    input_folder = input("Enter the folder path containing DOCX files: ").strip()
    output_folder = "output_padavivarana_arthakosha"
    padavivarana_output_folder = os.path.join(output_folder, "output_padavivarana")
    arthakosha_output_folder = os.path.join(output_folder, "output_arthakosha")

    if not os.path.isdir(input_folder):
        print("Invalid folder path. Please try again.")
    else:
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)  # clean old run
        process_folder(input_folder, padavivarana_output_folder, arthakosha_output_folder)
        print("✅ Processing completed.")
