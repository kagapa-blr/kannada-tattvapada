import os
import re
import shutil
import unicodedata
from pathlib import Path
from docx import Document
import pandas as pd

# === CONSTANTS ===
KANNADA_NUM_MAP = {
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
}
SAMPUTA_RE = re.compile(r'^\s*ಸಂಪುಟ\s*[-:–—]*\s*([೦-೯0-9.]+)', re.IGNORECASE)
VERSE_HEADER_RE = re.compile(r'^\s*([೦-೯0-9]+)(?:[\.\(]|\s+)\s*')
SPECIAL_ENDINGS = ("||", "॥")

# === HELPERS ===
def normalize_para(text):
    return unicodedata.normalize('NFC', text.strip())

def kannada_to_number(s):
    trans = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    if re.match(r'^\d*\.?\d*$', trans) and trans not in ("", ".",):
        num = float(trans)
        return int(num) if num.is_integer() else num
    return None

def kannada_to_int(s):
    trans = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    digits = ''.join(ch for ch in trans if ch.isdigit())
    return int(digits) if digits.isdigit() else None

def valid_heading_line(line):
    s = line.strip()
    if not s:
        return False
    if "|" in s or "।" in s or "॥" in s:
        return False
    if any(s.endswith(se) for se in SPECIAL_ENDINGS):
        return False
    if any(s.startswith(se) for se in SPECIAL_ENDINGS):
        return False
    if re.match(r'^[0-9೦-೯]', s):  # starts with digit
        return False
    if len(s.split()) > 5:
        return False
    return True

def extract_paragraphs_from_docx(path):
    doc = Document(path)
    return [normalize_para(p.text) for p in doc.paragraphs if normalize_para(p.text)]

# === Author detection ===
def is_author_name(candidate):
    cand = candidate.strip()
    if not cand or not valid_heading_line(cand):
        return False
    return cand.endswith("ತತ್ವಪದಗಳು")

# === Get max 2 valid headings before verse ===
def get_heading_lines_before_verse(paras, verse_index):
    heading_lines = []
    j = verse_index - 1
    while j >= 0 and len(heading_lines) < 2:
        line = paras[j].strip()
        if not line:
            j -= 1
            continue
        if valid_heading_line(line):
            heading_lines.insert(0, line)
        else:
            break
        j -= 1
    return heading_lines

# === CORE PARSER ===
def parse_document(paras):
    if not paras:
        return []

    samputa_sankhye, tatvapadakosha_sheershike = "-", "-"
    samputa_index = -1

    # Find samputa
    for i, p in enumerate(paras):
        if p.lower().startswith("ಸಂಪುಟ"):
            m = SAMPUTA_RE.match(p)
            if m:
                samputa_sankhye = kannada_to_number(m.group(1)) or m.group(1)
                samputa_index = i
                break

    # Find document title
    for j in range(samputa_index + 1, len(paras)):
        if paras[j]:
            tatvapadakosha_sheershike = paras[j]
            break

    # Get first author (mandatory)
    current_author = "-"
    for p in paras:
        if is_author_name(p):
            current_author = p
            break

    last_vibhag = "-"
    author_verse_counter = 0
    entries = []

    i = 0
    while i < len(paras):
        line = paras[i]
        verse_match = VERSE_HEADER_RE.match(line)
        if not verse_match:
            i += 1
            continue

        # Get headings before verse
        heading_lines = get_heading_lines_before_verse(paras, i)
        detected_author = None
        detected_vibhag = None

        for hl in heading_lines:
            if is_author_name(hl):
                detected_author = hl
            else:
                detected_vibhag = hl

        # Author reset counter if changed
        if detected_author and detected_author != tatvapadakosha_sheershike:
            if detected_author != current_author:
                current_author = detected_author
                author_verse_counter = 0  # reset for new author

        # Increment verse counter for this author
        author_verse_counter += 1
        tatvapada_sankhye = str(author_verse_counter)

        # Vibhag carry-forward
        if detected_vibhag and not is_author_name(detected_vibhag):
            last_vibhag = detected_vibhag
        current_vibhag = last_vibhag or "-"

        # Collect tatvapada block (telugu/original)
        block = []
        k = i + 1
        while k < len(paras) and not VERSE_HEADER_RE.match(paras[k]):
            block.append(paras[k])
            k += 1

        tatvapada_content = "\n".join(block).strip() or "-"
        clean_sheershike = re.sub(r"^[೦-೯0-9]+[.(]?\s*", "", line)

        # Special fields
        bhavanuvada, klishta_padagalu_artha, tippani = "-", "-", "-"

        # === Look ahead: check if next verse is actually "ಭಾವಾನುವಾದ" ===
        if k < len(paras):
            next_line = paras[k]
            next_match = VERSE_HEADER_RE.match(next_line)
            if next_match:
                after_num = re.sub(r"^[೦-೯0-9]+[.(]?\s*", "", next_line).strip()
                if re.match(r"^(ಕನ್ನಡ\s*)?ಭಾವಾನುವಾದ\s*[:：]", after_num):
                    # Collect its block
                    bhava_block = []
                    k2 = k + 1
                    while k2 < len(paras) and not VERSE_HEADER_RE.match(paras[k2]):
                        bhava_block.append(paras[k2])
                        k2 += 1

                    # Keep full line, just remove colon
                    bhavanuvada_line = re.sub(r"[:：]\s*", " ", after_num).strip()
                    bhavanuvada = bhavanuvada_line
                    if bhava_block:
                        bhavanuvada += "\n" + "\n".join(bhava_block)

                    # Skip this whole block
                    k = k2

        entries.append({
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapadakarara_hesaru": current_author,
            "vibhag": current_vibhag,
            "tatvapada_sheershike": clean_sheershike,
            "tatvapada_sankhye": tatvapada_sankhye,
            "tatvapada_first_line": block[0].strip() if block else "-",
            "tatvapada": tatvapada_content,
            "bhavanuvada": bhavanuvada,
            "klishta_padagalu_artha": klishta_padagalu_artha,
            "tippani": tippani
        })

        i = k

    return entries

# === PROCESS FOLDER ===
def process_folder(input_dir):
    base_dir = Path("output_csv")
    shutil.rmtree(base_dir, ignore_errors=True)
    out_dir = base_dir / "individual"
    out_dir.mkdir(parents=True, exist_ok=True)

    for docx_file in sorted(Path(input_dir).glob("*.docx")):
        try:
            paras = extract_paragraphs_from_docx(docx_file)
            parsed = parse_document(paras)
            if not parsed:
                continue
            df = pd.DataFrame(parsed)
            out_path = out_dir / f"{docx_file.stem}.csv"
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            print("Saved:", out_path)
        except Exception as e:
            print("Error processing", docx_file, ":", e)

# === Rename DOCX Utility ===
kannada_to_arabic = str.maketrans({
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
})

def rename_docx_files(directory):
    for filename in os.listdir(directory):
        if filename.lower().endswith(".docx"):
            clean_name = re.sub(r'\s+', '', filename)
            clean_name = clean_name.translate(kannada_to_arabic)
            numbers = re.findall(r'\d+', clean_name)

            if numbers:
                if len(numbers) >= 2:
                    new_name = f"samputa_{numbers[0]}.{numbers[1]}.docx"
                else:
                    new_name = f"samputa_{numbers[0]}.docx"

                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_name)
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    print(f"Renamed: {filename} → {new_name}")
                else:
                    print(f"Skipped (already exists): {new_name}")

# === MAIN ===
if __name__ == "__main__":
    inp = input("Folder with .docx: ").strip()
    # rename_docx_files(inp)
    process_folder(inp)
