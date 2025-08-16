import re, shutil, unicodedata
from pathlib import Path
from docx import Document
import pandas as pd

# === CONSTANTS ===
KANNADA_NUM_MAP = {
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
}
SAMPUTA_RE = re.compile(r'^\s*ಸಂಪುಟ\s*[-:–—]*\s*([೦-೯0-9]+)', re.IGNORECASE)
VERSE_HEADER_RE = re.compile(r'^\s*([೦-೯0-9]+)(?:[\.\(]|\s+)\s*')

SPECIAL_ENDINGS = ("||", "॥")

# === HELPERS ===
def normalize_para(text):
    return unicodedata.normalize('NFC', text.strip())

def kannada_to_number(s):
    trans = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    if re.match(r'^\d+(\.\d+)?$', trans):
        return trans
    return None

def kannada_to_int(s):
    trans = ''.join(KANNADA_NUM_MAP.get(ch, ch) for ch in s)
    digits = ''.join(ch for ch in trans if ch.isdigit())
    return int(digits) if digits.isdigit() else None

def ends_with_special(line):
    s = line.strip()
    return any(s.endswith(se) for se in SPECIAL_ENDINGS)

def valid_heading_line(line):
    s = line.strip()
    if not s:
        return False
    # reject lines with bars anywhere
    if "|" in s:
        return False
    # reject lines with Kannada danda marks
    if "।" in s or "॥" in s:
        return False
    if any(s.endswith(se) for se in SPECIAL_ENDINGS):
        return False
    if any(s.startswith(se) for se in SPECIAL_ENDINGS):
        return False
    if re.match(r'^[0-9೦-೯]', s):
        return False
    # reject lines that are too long to be headings
    if len(s.split()) > 5:
        return False
    return True

def extract_paragraphs_from_docx(path):
    doc = Document(path)
    return [normalize_para(p.text) for p in doc.paragraphs if normalize_para(p.text)]

def load_authors_list(file_path="authors.txt"):
    authors_set = set()
    if Path(file_path).is_file():
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                name = line.strip()
                if name:
                    authors_set.add(name)
    return authors_set

def is_author_name(candidate, authors_set):
    """
    True if candidate's first word matches any word in any author name,
    and candidate has at least 2 words.
    """
    cand = candidate.strip()
    if not cand or not valid_heading_line(cand):
        return False

    cand_parts = cand.split()
    if len(cand_parts) < 2:  # must have at least 2 parts
        return False

    cand_first = cand_parts[0]
    for auth in authors_set:
        auth_words = auth.split()
        if cand_first in auth_words:
            return True
    return False


# === NEW HELPERS FOR AUTHOR/VIBHAG DETECTION ===
def get_heading_lines_above(paras, index):
    heading_lines = []
    j = index - 1
    while j >= 0 and len(heading_lines) < 2:
        line = paras[j].strip()
        if not line:
            j -= 1
            continue
        if VERSE_HEADER_RE.match(line) or line.lower().startswith("ಸಂಪುಟ"):
            break
        if any(c in line for c in ('|', '।', '॥', ',', ';', ':')):
            break
        if not valid_heading_line(line):
            break
        heading_lines.insert(0, line)  # keep order top to bottom
        j -= 1
    return heading_lines

def detect_author_vibhag(heading_lines, default_author, authors_set):
    if len(heading_lines) == 2:
        author = heading_lines[0] if is_author_name(heading_lines[0], authors_set) else default_author
        vibhag = heading_lines[1]
    elif len(heading_lines) == 1:
        if is_author_name(heading_lines[0], authors_set):
            author = heading_lines[0]
            vibhag = "-"
        else:
            author = default_author
            vibhag = heading_lines[0]
    else:
        author = default_author
        vibhag = "-"
    return author, vibhag

# === CORE PARSER ===
# === CORE PARSER ===
def parse_document(paras, authors_set=None):
    if not paras:
        return []
    if authors_set is None:
        authors_set = set()

    samputa_sankhye, tatvapadakosha_sheershike = "-", "-"
    samputa_index, tatvapadakosha_index = -1, -1

    # Find samputa
    for i, p in enumerate(paras):
        if p.lower().startswith("ಸಂಪುಟ"):
            m = SAMPUTA_RE.match(p)
            if m:
                samputa_sankhye = kannada_to_number(m.group(1)) or m.group(1)
                samputa_index = i
                break

    # Find sheershike (title)
    for j in range(samputa_index + 1, len(paras)):
        if paras[j]:
            tatvapadakosha_sheershike = paras[j]
            tatvapadakosha_index = j
            break

    entries = []
    current_author = tatvapadakosha_sheershike
    current_vibhag = "-"
    last_vibhag = "-"

    i = 0
    while i < len(paras):
        line = paras[i]
        verse_match = VERSE_HEADER_RE.match(line)
        if not verse_match:
            i += 1
            continue

        raw_num = verse_match.group(1)
        num_int = kannada_to_int(raw_num)
        tatvapada_sankhye = str(num_int) if num_int else raw_num

        # get up to 2 valid heading lines immediately above this verse
        heading_lines = get_heading_lines_above(paras, i)
        # detect author and vibhag using the new helper
        author, vibhag = detect_author_vibhag(heading_lines, tatvapadakosha_sheershike, authors_set)

        # sanitize vibhag
        if is_author_name(vibhag, authors_set) or not valid_heading_line(vibhag):
            vibhag = "-"

        # carry forward vibhag if current vibhag is "-"
        if vibhag == "-":
            vibhag = last_vibhag
        else:
            last_vibhag = vibhag

        current_author = author if author.strip() else "-"
        current_vibhag = vibhag if vibhag.strip() else "-"

        # collect verse block paragraphs until next verse header
        block = []
        k = i + 1
        while k < len(paras) and not VERSE_HEADER_RE.match(paras[k]):
            block.append(paras[k])
            k += 1

        # special sections extraction
        bhavanuvada, klishta_padagalu_artha, tippani = "-", "-", "-"
        remaining = []
        for para_text in block:
            if para_text.startswith("ಭಾವಾನುವಾದ"):
                bhavanuvada = para_text[len("ಭಾವಾನುವಾದ"):].lstrip(" :-–—").strip() or "-"
            elif para_text.startswith("ಅರ್ಥ"):
                klishta_padagalu_artha = para_text[len("ಅರ್ಥ"):].lstrip(" :-–—").strip() or "-"
            elif para_text.startswith("ಟಿಪ್ಪಣಿ"):
                tippani = para_text[len("ಟಿಪ್ಪಣಿ"):].lstrip(" :-–—").strip() or "-"
            else:
                remaining.append(para_text)

        tatvapada_content = "\n".join(remaining).strip() or "-"
        clean_sheershike = re.sub(r"^[೦-೯0-9]+[.(]?\s*", "", line)

        entries.append({
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapadakarara_hesaru": current_author,
            "vibhag": current_vibhag if current_vibhag.strip() else last_vibhag or "-",
            "tatvapada_sheershike": clean_sheershike,
            "tatvapada_sankhye": tatvapada_sankhye,
            "tatvapada_first_line": remaining[0].strip() if remaining else "-",
            "tatvapada": tatvapada_content,
            "bhavanuvada": bhavanuvada,
            "klishta_padagalu_artha": klishta_padagalu_artha,
            "tippani": tippani
        })

        i = k

    # normalize blanks and sort
    for e in entries:
        if not e["tatvapadakarara_hesaru"].strip():
            e["tatvapadakarara_hesaru"] = "-"
        if not e["vibhag"].strip():
            e["vibhag"] = "-"

    try:
        entries.sort(key=lambda e: (float(e["samputa_sankhye"]), float(e["tatvapada_sankhye"])))
    except:
        pass

    return entries

# === RUN FOLDER ===
def process_folder(input_dir, authors_file="filters/authors.txt"):
    authors_set = load_authors_list(authors_file)
    print(f"author set count : {len(authors_set)}")
    base_dir = Path("output_csv")
    shutil.rmtree(base_dir, ignore_errors=True)
    out_dir = base_dir / "individual"
    out_dir.mkdir(parents=True, exist_ok=True)
    for docx_file in sorted(Path(input_dir).glob("*.docx")):
        try:
            paras = extract_paragraphs_from_docx(docx_file)
            parsed = parse_document(paras, authors_set)
            if not parsed:
                continue
            df = pd.DataFrame(parsed)
            out_path = out_dir / f"{docx_file.stem}.csv"
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            print("Saved:", out_path)
        except Exception as e:
            print("Error:", docx_file, e)


if __name__ == "__main__":
    inp = input("Folder with .docx: ").strip()
    process_folder(inp)
