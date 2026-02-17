import os
import pandas as pd
from datetime import datetime
import re

# CONFIG
MAIN_CSV_FOLDER = "./input/paribhashika"
TEMPLATE_CSV_PATH = "./input/template/paribhashika_template.csv"
OUTPUT_ROOT = "./paribhashika_output_files"

# Create dated output folder
today_str = datetime.now().strftime("%d-%m-%Y")
OUTPUT_FOLDER = os.path.join(OUTPUT_ROOT, today_str, "files")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load template
template_df = pd.read_csv(TEMPLATE_CSV_PATH, dtype=str).fillna("")

TEMPLATE_COLS = [
    "tatvapada_author_id",
    "tatvapadakarara_hesaru",
    "samputa_sankhye",
    "paribhashika_padavivarana_title",
    "paribhashika_padavivarana_content",
]

def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = re.sub(r"\s+", " ", name.strip())
    return name.split(" ")[0].lower()  # first word only

for file in os.listdir(MAIN_CSV_FOLDER):
    if not file.lower().endswith(".csv"):
        continue

    input_path = os.path.join(MAIN_CSV_FOLDER, file)
    print("Processing:", file)

    df = pd.read_csv(input_path, dtype=str).fillna("")
    output_rows = []
    warnings = []

    for i, row in df.iterrows():
        samputa = str(row.get("samputa_sankhye", "")).strip()
        author_name = str(row.get("tatvapadakarara_hesaru", "")).strip()
        author_key = normalize_name(author_name)

        # Step 1: match samputa first
        candidates = template_df[
            template_df["samputa_sankhye"].astype(str).str.strip() == samputa
        ]

        # Step 2: match author first word
        matched = None
        for _, trow in candidates.iterrows():
            template_author_key = normalize_name(trow.get("tatvapadakarara_hesaru", ""))
            if author_key and author_key == template_author_key:
                matched = trow
                break

        if matched is None:
            # 👉 KEEP ROW AS-IS (only reorder columns)
            warnings.append(f"Row {i+1}: No match for samputa={samputa}, author={author_name}")
            output_rows.append({
                "tatvapada_author_id": row.get("tatvapada_author_id", ""),
                "tatvapadakarara_hesaru": row.get("tatvapadakarara_hesaru", ""),
                "samputa_sankhye": row.get("samputa_sankhye", ""),
                "paribhashika_padavivarana_title": row.get("paribhashika_padavivarana_title", ""),
                "paribhashika_padavivarana_content": row.get("paribhashika_padavivarana_content", ""),
            })
            continue

        # 👉 Matched: fix author_id using template
        output_rows.append({
            "tatvapada_author_id": matched["tatvapada_author_id"],
            "tatvapadakarara_hesaru": matched["tatvapadakarara_hesaru"],
            "samputa_sankhye": samputa,
            "paribhashika_padavivarana_title": row.get("paribhashika_padavivarana_title", ""),
            "paribhashika_padavivarana_content": row.get("paribhashika_padavivarana_content", ""),
        })

    out_df = pd.DataFrame(output_rows, columns=TEMPLATE_COLS)
    output_path = os.path.join(OUTPUT_FOLDER, file)
    out_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"✔ Saved: {output_path}")
    if warnings:
        print("⚠ Warnings:")
        for w in warnings:
            print("  -", w)

print("\nAll Paribhashika files processed successfully.")
