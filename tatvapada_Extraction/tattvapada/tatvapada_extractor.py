import os
import re
import shutil
import unicodedata
from pathlib import Path
from docx import Document
import pandas as pd
from datetime import datetime

# === CONSTANTS ===
KANNADA_NUM_MAP = {
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
}
SAMPUTA_RE = re.compile(r'^\s*ಸಂಪುಟ\s*[-:–—]*\s*([೦-೯0-9.]+)', re.IGNORECASE)
VERSE_HEADER_RE = re.compile(r'^\s*([೦-೯0-9]+)(?:[\.\)]|\s+)\s*')
SPECIAL_ENDINGS = ("||", "॥",'.')

# === BASIC HELPERS ===
def normalize_para(text):
    return unicodedata.normalize('NFC', text.strip())

def extract_paragraphs_from_docx(path):
    doc = Document(path)
    return [normalize_para(p.text) for p in doc.paragraphs if normalize_para(p.text)]

def kannada_to_number(s):
    trans = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    try:
        num = float(trans)
        return int(num) if num.is_integer() else num
    except:
        return s

# === HEADING RULES ===
def is_valid_heading_line(line):
    s = line.strip()
    if not s:
        return False
    if "|" in s or "॥" in s or "।" in s:
        return False
    if any(s.endswith(se) for se in SPECIAL_ENDINGS):
        return False
    if re.match(r'^[0-9೦-೯]', s):
        return False
    if len(s.split()) > 5:
        return False
    return True

def is_author_name(line):
    return is_valid_heading_line(line) and line.endswith("ತತ್ವಪದಗಳು")

def is_valid_vibhaga(line, prev_line):
    if not is_valid_heading_line(line):
        return False
    if prev_line and prev_line.strip().endswith(("||", "॥")):
        return True
    if not prev_line:
        return True
    return False

# === COLUMN FUNCTIONS ===
def get_samputa_sankhye(paras):
    for p in paras:
        m = SAMPUTA_RE.match(p)
        if m:
            return kannada_to_number(m.group(1))
    return "-"

def get_tatvapadakosha_sheershike(paras):
    found_samputa = False
    for p in paras:
        if found_samputa and p:
            return p
        if p.lower().startswith("ಸಂಪುಟ"):
            found_samputa = True
    return "-"

def get_tatvapadakarara_hesaru(paras):
    for p in paras:
        if is_author_name(p):
            return p
    return "-"

# === UPDATED: ONLY ONE NEAREST NON-EMPTY LINE FOR VIBHAG ===
def get_heading_before_verse(paras, idx):
    j = idx - 1
    prev_line = None
    while j >= 0:
        line = paras[j].strip()
        if not line:
            j -= 1
            continue

        if is_author_name(line):
            return line, None

        if is_valid_vibhaga(line, prev_line):
            return None, line

        return None, None

    return None, None

# === CORE PARSER ===
def parse_document(paras):
    samputa_sankhye = get_samputa_sankhye(paras)
    tatvapadakosha_sheershike = get_tatvapadakosha_sheershike(paras)
    current_author = get_tatvapadakarara_hesaru(paras)

    last_vibhag = "-"
    author_counter = 0
    rows = []

    i = 0
    while i < len(paras):
        line = paras[i]
        if not VERSE_HEADER_RE.match(line):
            i += 1
            continue

        detected_author, detected_vibhag = get_heading_before_verse(paras, i)

        # === Reset when author changes ===
        if detected_author and detected_author != current_author:
            current_author = detected_author
            author_counter = 0
            last_vibhag = "-"

        author_counter += 1
        tatvapada_sankhye = str(author_counter)

        # === Carry forward vibhag ===
        if detected_vibhag:
            last_vibhag = detected_vibhag

        k = i + 1
        block = []
        while k < len(paras) and not VERSE_HEADER_RE.match(paras[k]):
            block.append(paras[k])
            k += 1

        tatvapada = "\n".join(block).strip() or "-"
        tatvapada_first_line = block[0] if block else "-"
        tatvapada_sheershike = re.sub(r'^[೦-೯0-9]+[.)]?\s*', '', line)

        bhavanuvada = "-"
        if k < len(paras):
            after = re.sub(r'^[೦-೯0-9]+[.)]?\s*', '', paras[k])
            if after.startswith("ಭಾವಾನುವಾದ"):
                bhavanuvada = paras[k]
                k += 1

        rows.append({
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapadakarara_hesaru": current_author,
            "vibhag": last_vibhag,
            "tatvapada_sheershike": tatvapada_sheershike,
            "tatvapada_sankhye": tatvapada_sankhye,
            "tatvapada_first_line": tatvapada_first_line,
            "tatvapada": tatvapada,
            "bhavanuvada": bhavanuvada,
            "klishta_padagalu_artha": "-",
            "tippani": "-"
        })

        i = k

    return rows

# === PROCESS FOLDER WITH DATE + STATS ===
def process_folder(folder):
    base_dir = Path("output_csv")
    base_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%d-%m-%Y")
    out_dir = base_dir / today / "files"
    out_dir.mkdir(parents=True, exist_ok=True)

    for f in sorted(Path(folder).glob("*.docx")):
        print("=" * 60)
        print("Processing:", f.name)

        paras = extract_paragraphs_from_docx(f)
        rows = parse_document(paras)
        df = pd.DataFrame(rows)
        out_file = out_dir / f"{f.stem}.csv"
        df.to_csv(out_file, index=False, encoding="utf-8-sig")

        print("Saved:", out_file)
        print("Total tattvapada:", len(rows))
        print("Unique authors:", len(set(r["tatvapadakarara_hesaru"] for r in rows)))
        print("Unique vibhag:", len(set(r["vibhag"] for r in rows)))

# === MAIN ===
if __name__ == "__main__":
    folder = input("Enter DOCX folder: ").strip()
    process_folder(folder)
