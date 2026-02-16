import os
import pandas as pd
from datetime import datetime
import unicodedata
import re

# CONFIG (based on your folder structure)
ARTHAKOSHA_FOLDER = "./input/arthakosha"
TEMPLATE_CSV_PATH = "./input/template/arthakosha_template.csv"

# Create dated output folder: arthakosha_ouput_files/dd-mm-yyyy/files
today_str = datetime.now().strftime("%d-%m-%Y")
OUTPUT_FOLDER = os.path.join("arthakosha_ouput_files", today_str, "files")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.casefold()
    return s

def first_word(s: str) -> str:
    s = normalize_text(s)
    if not s:
        return ""
    return s.split(" ")[0]

# Load template (mapping) CSV
template_df = pd.read_csv(TEMPLATE_CSV_PATH, dtype=str).fillna("")
template_df["samputa"] = template_df["samputa"].astype(str).str.strip()
template_df["author_first_norm"] = template_df["author_name"].apply(first_word)
template_df["author_id"] = template_df["author_id"].astype(str).str.strip()

# Build mapping: samputa -> { first_word_norm: author_id }
template_grouped = {}
for _, row in template_df.iterrows():
    samputa = row["samputa"]
    first_norm = row["author_first_norm"]
    author_id = row["author_id"]

    if samputa not in template_grouped:
        template_grouped[samputa] = {}

    template_grouped[samputa][first_norm] = author_id

# For debug: template first-words per samputa
template_first_words_by_samputa = (
    template_df.groupby("samputa")["author_name"]
    .apply(lambda x: [first_word(v) for v in x.dropna().astype(str).tolist()])
    .to_dict()
)

# Process each arthakosha CSV file
for filename in os.listdir(ARTHAKOSHA_FOLDER):
    if not filename.lower().endswith(".csv"):
        continue

    input_path = os.path.join(ARTHAKOSHA_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    print(f"\nProcessing: {filename}")

    df = pd.read_csv(input_path, dtype=str).fillna("")
    df["samputa"] = df["samputa"].astype(str).str.strip()
    df["author_first_norm"] = df["author_name"].apply(first_word)

    def update_author_id(row):
        samputa = row["samputa"]
        first_norm = row["author_first_norm"]

        if samputa in template_grouped:
            samputa_map = template_grouped[samputa]
            if first_norm in samputa_map and samputa_map[first_norm] != "":
                return samputa_map[first_norm]

            main_name = row["author_name"]
            sample_first_words = template_first_words_by_samputa.get(samputa, [])[:10]
            print("Not matched | samputa:", repr(samputa), "| main name:", repr(main_name))
            print("Sample template first-words for this samputa:", sample_first_words)
            print("-" * 60)
            return ""

        else:
            print("Samputa not found in template:", repr(samputa))
            return ""

    df["author_id"] = df.apply(update_author_id, axis=1)

    # Drop helper column so output CSV structure is unchanged
    df = df.drop(columns=["author_first_norm"])

    df.to_csv(output_path, index=False)

print("\nDone. Updated files saved in:", OUTPUT_FOLDER)
