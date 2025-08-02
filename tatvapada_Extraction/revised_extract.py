import re
import unicodedata
from pathlib import Path
from docx import Document
import pandas as pd

# === CONFIGURATION / PREFIX KEYWORDS ===
KANNADA_NUM_MAP = {
    '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
    '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
}

# Patterns
VERSE_HEADER_RE = re.compile(r'^([೦-೯]+)\.\s*(.*)')
SAMPUTA_RE = re.compile(r'^\s*ಸಂಪುಟ\s*[-:]*\s*([೦-೯\d]+)', re.IGNORECASE)
BLOCKER_RE = re.compile(r'(?:\|\|.*\|\||[೦-೯0-9])\s*$')  # paragraph ending with ||...|| or a digit

# Special-field prefixes
BHAVANUVADA_PREFIXES = ("ಭವಾನುವಾದ",)
KLISHTA_PREFIXES = ("ಅರ್ಥ",)
TIPPANI_PREFIXES = ("ಟಿಪ್ಪಣಿ", "ತಿಪ್ಪಣಿ")

def normalize_para(text: str) -> str:
    return unicodedata.normalize('NFC', text.strip())

def kannada_to_int(s: str) -> int | None:
    digits = ''.join(KANNADA_NUM_MAP.get(ch, '') for ch in s if ch in KANNADA_NUM_MAP)
    return int(digits) if digits.isdigit() else None

def is_blocker_para(para: str) -> bool:
    return bool(BLOCKER_RE.search(para))

def starts_with_any(para: str, prefixes: tuple[str, ...]) -> bool:
    stripped = para.strip()
    return any(stripped.startswith(pref) for pref in prefixes)

def extract_paragraphs_from_docx(path: Path) -> list[str]:
    doc = Document(path)
    paras = []
    for para in doc.paragraphs:
        text = normalize_para(para.text)
        if text:
            paras.append(text)
    return paras

def backward_author_and_vibhag(paras: list[str], index: int) -> tuple[str, str]:
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
    if len(candidates) == 2:
        return candidates[1], candidates[0]
    elif len(candidates) == 1:
        return candidates[0], "-"
    else:
        return "-", "-"

def parse_document(paras: list[str]) -> list[dict]:
    entries = []
    if not paras:
        return entries

    tatvapadakosha_sheershike = paras[0]
    samputa_sankhye = "-"
    samputa_index = -1
    for i, p in enumerate(paras):
        m = SAMPUTA_RE.match(p)
        if m:
            raw = m.group(1)
            num = kannada_to_int(raw) if any(ch in KANNADA_NUM_MAP for ch in raw) else None
            samputa_sankhye = str(num) if num is not None else raw
            samputa_index = i
            break

    current_author = "-"
    default_tatvapada_sheershike = "-"
    for j in range(samputa_index + 1, len(paras)):
        p = paras[j].strip()
        if not p or VERSE_HEADER_RE.match(p):
            continue
        current_author = p
        default_tatvapada_sheershike = p
        break

    current_vibhag = "-"
    last_vibhag = "-"

    i = 0
    while i < len(paras):
        p = paras[i]
        verse_match = VERSE_HEADER_RE.match(p)
        if not verse_match:
            i += 1
            continue

        raw_num = verse_match.group(1)
        tatvapada_sankhye = str(kannada_to_int(raw_num) or raw_num)
        sheershike_rest = verse_match.group(2).strip()

        # If verse number is 1, resolve both author and vibhag by backward scan
        if tatvapada_sankhye in ("1", "೧"):
            author_back, vibhag_back = backward_author_and_vibhag(paras, i)
            if author_back != "-":
                current_author = author_back
                default_tatvapada_sheershike = current_author
            if vibhag_back != "-":
                current_vibhag = vibhag_back
                last_vibhag = current_vibhag
        else:
            # For other verses, resolve vibhag by scanning backward until a non-blocker non-verse line
            j = i - 1
            found_vibhag = None
            while j >= 0:
                candidate = paras[j].strip()
                if not candidate:
                    j -= 1
                    continue
                if VERSE_HEADER_RE.match(candidate):
                    j -= 1
                    continue
                if is_blocker_para(candidate):
                    break  # don't go past content that looks like verse-body marker
                found_vibhag = candidate
                break
            if found_vibhag:
                current_vibhag = found_vibhag
                last_vibhag = current_vibhag

        tatvapada_sheershike = sheershike_rest if sheershike_rest else default_tatvapada_sheershike
        tatvapada_first_line = paras[i + 1] if i + 1 < len(paras) else "-"

        # Collect block until next verse header
        block = []
        k = i + 1
        while k < len(paras) and not VERSE_HEADER_RE.match(paras[k]):
            block.append(paras[k])
            k += 1
        tatvapada_content = "\n".join(block).strip() or tatvapada_first_line

        # Special fields
        bhavanuvada = "-"
        klishta_padagalu_artha = "-"
        tippani = "-"
        for b in block:
            if bhavanuvada == "-" and starts_with_any(b, BHAVANUVADA_PREFIXES):
                bhavanuvada = b.strip()
            if klishta_padagalu_artha == "-" and starts_with_any(b, KLISHTA_PREFIXES):
                klishta_padagalu_artha = b.strip()
            if tippani == "-" and starts_with_any(b, TIPPANI_PREFIXES):
                tippani = b.strip()

        entries.append({
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapada_author_id": "-",
            "tatvapadakarara_hesaru": current_author or "-",
            "vibhag": current_vibhag or last_vibhag or "-",
            "tatvapada_sheershike": tatvapada_sheershike,
            "tatvapada_sankhye": tatvapada_sankhye,
            "tatvapada_first_line": tatvapada_first_line,
            "tatvapada": tatvapada_content,
            "bhavanuvada": bhavanuvada,
            "klishta_padagalu_artha": klishta_padagalu_artha,
            "tippani": tippani
        })
        i = k

    return entries

def gather_stats(df: pd.DataFrame) -> dict:
    return {
        "total_tatvapada_entries": len(df),
        "distinct_authors": df["tatvapadakarara_hesaru"].nunique(),
        "distinct_vibhag": df["vibhag"].nunique(),
        "per_author_counts": df["tatvapadakarara_hesaru"].value_counts().to_dict()
    }

def process_folder(input_dir: Path):
    output_dir = Path("output_csv")
    output_dir.mkdir(exist_ok=True)
    consolidated = []
    stats_rows = []

    for docx_file in sorted(input_dir.glob("*.docx")):
        try:
            paras = extract_paragraphs_from_docx(docx_file)
            print(f"paragraph: {paras}")
            parsed = parse_document(paras)
            if not parsed:
                print(f"[WARN] No entries extracted from {docx_file.name}")
                continue
            df = pd.DataFrame(parsed)
            per_doc_csv = output_dir / f"{docx_file.stem}.csv"
            df.to_csv(per_doc_csv, index=False, encoding="utf-8-sig")
            print(f"Wrote: {per_doc_csv}")

            stats = gather_stats(df)
            stats_row = {
                "source_file": docx_file.name,
                "total_tatvapada_entries": stats["total_tatvapada_entries"],
                "distinct_authors": stats["distinct_authors"],
                "distinct_vibhag": stats["distinct_vibhag"],
                "author_breakdown": "; ".join(f"{author}:{count}" for author, count in stats["per_author_counts"].items())
            }
            stats_rows.append(stats_row)

            df["source_file"] = docx_file.name
            consolidated.append(df)
        except Exception as e:
            print(f"[ERROR] Failed {docx_file.name}: {e}")

    if consolidated:
        big = pd.concat(consolidated, ignore_index=True)
        big.to_csv(output_dir / "consolidated.csv", index=False, encoding="utf-8-sig")
        print(f"Consolidated CSV saved to: {output_dir / 'consolidated.csv'}")
    else:
        print("No data to consolidate.")

    if stats_rows:
        stats_df = pd.DataFrame(stats_rows)
        stats_df.to_csv(output_dir / "stats.csv", index=False, encoding="utf-8-sig")
        print(f"Statistics summary saved to: {output_dir / 'stats.csv'}")

def main():
    inp = input("Enter folder path containing .docx files: ").strip()
    input_dir = Path(inp)
    if not input_dir.is_dir():
        print(f"Invalid input folder: {input_dir}")
        return
    process_folder(input_dir)

if __name__ == "__main__":
    main()
