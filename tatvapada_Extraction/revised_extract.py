import re
import shutil

import unicodedata
from pathlib import Path
from docx import Document
import pandas as pd
import string

# === CONFIGURATION / CONSTANTS ===

KANNADA_NUM_MAP = {
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
}

VERSE_HEADER_RE = re.compile(r'^([೦-೯0-9]+)\.\s*(.*)')
SAMPUTA_RE = re.compile(r'^\s*ಸಂಪುಟ\s*[-:]*\s*([೦-೯0-9]+)', re.IGNORECASE)
BLOCKER_RE = re.compile(r'(?:\|\|.*?\|\||॥|[೦-೯0-9])\s*$')

PUNCTUATION_KANNADA_PLUS = set(".,:;？！|॥||")

# === HELPER FUNCTIONS ===

def normalize_para(text: str) -> str:
    return unicodedata.normalize('NFC', text.strip())

def kannada_to_int(s: str) -> int | None:
    translated = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    digits = ''.join(ch for ch in translated if ch.isdigit())
    return int(digits) if digits.isdigit() else None

def is_blocker_para(para: str) -> bool:
    return bool(BLOCKER_RE.search(para))

def ends_with_punctuation(line: str) -> bool:
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in PUNCTUATION_KANNADA_PLUS or stripped[-1] in string.punctuation

def is_clean_kannada_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    pattern = r'^[\u0C80-\u0CFF\s]+$'
    return bool(re.match(pattern, s))

def extract_paragraphs_from_docx(path: Path) -> list[str]:
    doc = Document(path)
    paras = []
    for para in doc.paragraphs:
        text = normalize_para(para.text)
        if text:
            paras.append(text)
    return paras

def backward_author_and_vibhag(paras: list[str], index: int, prev_author: str = "-") -> tuple[str, str]:
    """
    Look backwards from the verse index to find author and vibhag.
    If prev_author is "-" or empty, and current candidate has only one line,
    treat it as author and skip vibhag.
    """
    candidates = []
    j = index - 1
    while j >= 0 and len(candidates) < 2:
        p = paras[j].strip()
        if not p:
            j -= 1
            continue
        if BLOCKER_RE.search(p):
            break
        if VERSE_HEADER_RE.match(p):
            j -= 1
            continue
        candidates.append(p)
        j -= 1

    if prev_author in ("-", "") and candidates:
        first_candidate = candidates[0]
        if "\n" not in first_candidate and len(first_candidate.split()) <= 6:
            return first_candidate, "-"

    if len(candidates) == 2:
        return candidates[1], candidates[0]
    elif len(candidates) == 1:
        return candidates[0], "-"
    else:
        return "-", "-"

# === CORE PARSING FUNCTION ===

def parse_document(paras: list[str]) -> list[dict]:
    entries = []
    if not paras:
        return entries

    # 1. Detect samputa (volume) line
    samputa_sankhye = "-"
    tatvapadakosha_sheershike = "-"
    samputa_index = -1

    for i, p in enumerate(paras):
        stripped = p.strip()
        if stripped.lower().startswith("ಸಂಪುಟ"):
            m = SAMPUTA_RE.match(stripped)
            if m:
                raw = m.group(1)
                num = kannada_to_int(raw)
                samputa_sankhye = str(num) if num is not None else raw
                samputa_index = i
                break

    # 2. Next non-empty line after samputa is tatvapadakosha_sheershike
    for j in range(samputa_index + 1, len(paras)):
        line = paras[j].strip()
        if line:
            tatvapadakosha_sheershike = line
            break

    current_author = tatvapadakosha_sheershike
    current_vibhag = "-"
    last_vibhag = "-"

    i = 0
    while i < len(paras):
        p = paras[i]
        line_stripped = p.strip()

        # Match verse header with digits followed by ( or .
        verse_match = re.match(r'^([೦-೯0-9]+)[\(\.]', line_stripped)
        if not verse_match:
            i += 1
            continue

        raw_num = verse_match.group(1)
        num_int = kannada_to_int(raw_num)
        tatvapada_sankhye = str(num_int) if num_int is not None else raw_num.lstrip('0')  # remove leading 0 if any

        # NEW LOGIC: If tatvapada_sankhye == "1", update author and vibhag by backward scan
        if tatvapada_sankhye == "1":
            author_back, vibhag_back = backward_author_and_vibhag(paras, i, prev_author=current_author)
            if author_back != "-":
                current_author = author_back
            if vibhag_back != "-":
                current_vibhag = vibhag_back

        author = current_author
        vibhag = "-"

        # Backward scan for author/vibhag, stops at punctuation-ending lines or headers or samputa lines
        j = i - 1
        candidate_lines = []
        while j >= 0:
            line = paras[j].strip()
            if not line:
                j -= 1
                continue
            if re.match(r'^([೦-೯0-9]+)[\(\.]', line) or line.lower().startswith("ಸಂಪುಟ"):
                break
            if ends_with_punctuation(line):
                break
            candidate_lines.append((j, line))
            j -= 1

        # Determine vibhag and author from candidate lines
        vibhag_idx = None
        for idx, (_, line_text) in enumerate(candidate_lines):
            if not ends_with_punctuation(line_text):
                vibhag_idx = idx
                vibhag = line_text
                break

        if vibhag_idx is not None and vibhag_idx + 1 < len(candidate_lines):
            possible_author = candidate_lines[vibhag_idx + 1][1]
            if is_clean_kannada_line(possible_author):
                author = possible_author
            else:
                author = current_author
        else:
            author = current_author
            if vibhag == "-":
                vibhag = current_vibhag or "-"

        current_author = author
        current_vibhag = vibhag
        last_vibhag = vibhag if vibhag != "-" else last_vibhag

        # Collect tatvapada content until next verse header
        block = []
        k = i + 1
        while k < len(paras) and not re.match(r'^([೦-೯0-9]+)[\(\.]', paras[k].strip()):
            block.append(paras[k])
            k += 1
        tatvapada_content = "\n".join(block).strip() or "-"

        # Remove number prefix from verse header to get clean sheershike
        clean_sheershike = re.sub(r'^[೦-೯0-9]+[\.\(]\s*', '', line_stripped)

        entries.append({
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapadakarara_hesaru": author,
            "vibhag": current_vibhag or last_vibhag or "-",
            "tatvapada_sheershike": clean_sheershike,
            "tatvapada_sankhye": tatvapada_sankhye,
            "tatvapada_first_line": block[0].strip() if block else "-",
            "tatvapada": tatvapada_content,
            "bhavanuvada": "-",
            "klishta_padagalu_artha": "-",
            "tippani": "-"
        })

        i = k

    return entries




def process_folder(input_dir: Path):
    base_output_dir = Path("output_csv")

    try:
        shutil.rmtree(base_output_dir)
    except Exception as e:
        print(f"Cannot delete output folder: {e}")

    # Prepare only the individual directory
    individual_dir = base_output_dir / "individual"
    individual_dir.mkdir(parents=True, exist_ok=True)

    for docx_file in sorted(input_dir.glob("*.docx")):
        try:
            paras = extract_paragraphs_from_docx(docx_file)
            parsed = parse_document(paras)
            if not parsed:
                print(f"[WARN] No entries extracted from {docx_file.name}")
                continue

            df = pd.DataFrame(parsed)

            # Save individual CSV (one per docx)
            per_doc_csv = individual_dir / f"{docx_file.stem}.csv"
            df.to_csv(per_doc_csv, index=False, encoding="utf-8-sig")
            print(f"Wrote individual file: {per_doc_csv}")

        except Exception as e:
            print(f"[ERROR] Failed {docx_file.name}: {e}")

# === MAIN ENTRYPOINT ===

def main():
    inp = input("Enter folder path containing .docx files: ").strip()
    input_dir = Path(inp)
    if not input_dir.is_dir():
        print(f"Invalid input folder: {input_dir}")
        return
    process_folder(input_dir)

if __name__ == "__main__":
    main()
