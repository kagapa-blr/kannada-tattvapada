import os
import re
import pandas as pd
from docx import Document

def get_input_folder():
    folder = input("Enter the folder path containing DOCX files: ").strip()
    if not os.path.exists(folder):
        print("❌ Folder not found.")
        exit(1)
    return folder

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def extract_authors(text):
    pattern = r"ತತ್ತ್ವಪದಕಾರರು\s+([\s\S]+?)\n\n"
    match = re.search(pattern, text)
    if not match:
        return []
    author_block = match.group(1)
    authors = []
    for line in author_block.splitlines():
        line = line.strip()
        if line:
            name = re.sub(r"^\d+[.ೕ)]\s*", "", line)
            authors.append(name)
    return authors

def normalize_author_name(name):
    return re.sub(r"[ರನವರತರ]+$", "", name).strip()

def parse_tatvapada_blocks(text, authors):
    lines = text.splitlines()
    data = []

    tatvapadakosha = ""
    samputa_sankhye = ""
    tatvapadakosha_sheershike = ""
    current_author = None
    current_mukhya_sheershike = ""
    current_title = None
    current_poem = []
    tatvapada_counter = 0

    known_authors = authors.copy()
    prev_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Extract metadata
        if not tatvapadakosha and "ಸಮಗ್ರ ತತ್ವಪದಗಳ" in line:
            tatvapadakosha = line
        elif not samputa_sankhye and "ಸಂಪುಟ" in line:
            match = re.search(r"ಸಂಪುಟ\s*[-–]?\s*([೧೨೩೪೫೬೭೮೯೦]+)", line)
            if match:
                samputa_sankhye = match.group(1)
        elif not tatvapadakosha_sheershike and ("ತತ್ತ್ವಪದಗಳು" in line or "ತತ್ತ್ವಪದಗಳ" in line):
            tatvapadakosha_sheershike = line

        # Detect author section
        if "ತತ್ತ್ವಪದಗಳು" in line or "ತತ್ವ ಪದಗಳು" in line:
            current_mukhya_sheershike = line
            norm_line = normalize_author_name(re.sub(r"ತತ್ತ್ವಪದ[ಗಳಗಳು]*", "", line).strip())
            for a in known_authors:
                if normalize_author_name(a) in norm_line:
                    current_author = a
                    break

        # Detect new tatvapada
        tatvapada_match = re.match(r"^([೧೨೩೪೫೬೭೮೯೦]+)[\.\)]\s*(.+)", line)
        if tatvapada_match:
            kannada_digit = tatvapada_match.group(1)
            if kannada_digit == "೧":
                # Try to infer new author above
                for back_line in reversed(prev_lines):
                    if "ತತ್ತ್ವಪದಗಳು" in back_line or "ತತ್ವ ಪದಗಳು" in back_line:
                        norm_back = normalize_author_name(back_line)
                        for a in known_authors:
                            if normalize_author_name(a) in norm_back:
                                current_author = a
                                current_mukhya_sheershike = back_line
                                break
                        break

            if current_poem:
                poem_text = "\n".join(current_poem).strip()
                first_line = current_poem[0].strip() if current_poem else ""
                tatvapada_counter += 1
                data.append({
                    "tatvapadakosha": tatvapadakosha,
                    "samputa_sankhye": samputa_sankhye,
                    "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
                    "tatvapadakarara_hesaru": current_author,
                    "mukhya_sheershike": current_mukhya_sheershike,
                    "tatvapada_sankhye": tatvapada_counter,
                    "tatvapada_hesaru": current_title,
                    "tatvapada_first_line": current_poem[0].strip() if current_poem else "",
                    "tatvapada": poem_text
                })
                current_poem = []

            current_title = tatvapada_match.group(2)
        elif current_title:
            current_poem.append(line)

        # Maintain previous line buffer
        prev_lines.append(line)
        if len(prev_lines) > 5:
            prev_lines.pop(0)

    # Save last tatvapada
    if current_title and current_poem:
        poem_text = "\n".join(current_poem).strip()
        tatvapada_counter += 1
        data.append({
            "tatvapadakosha": tatvapadakosha,
            "samputa_sankhye": samputa_sankhye,
            "tatvapadakosha_sheershike": tatvapadakosha_sheershike,
            "tatvapadakarara_hesaru": current_author,
            "mukhya_sheershike": current_mukhya_sheershike,
            "tatvapada_sankhye": tatvapada_counter,
            "tatvapada_hesaru": current_title,
            "tatvapada_first_line": current_poem[0].strip() if current_poem else "",
            "tatvapada": poem_text
        })

    authors_with_poems = set(entry['tatvapadakarara_hesaru'] for entry in data if entry['tatvapadakarara_hesaru'])
    missing_authors = set(authors) - authors_with_poems
    if missing_authors:
        print(f"⚠️ Warning: No tatvapadas found for authors: {list(missing_authors)}")

    return data

def main():
    folder = get_input_folder()
    all_data = []

    for filename in os.listdir(folder):
        if filename.endswith(".docx"):
            path = os.path.join(folder, filename)
            print(f"\n🔍 Processing: {filename}")
            text = extract_text_from_docx(path)
            authors = extract_authors(text)
            tatvapadas = parse_tatvapada_blocks(text, authors)
            all_data.extend(tatvapadas)
            print(f"✅ Found {len(tatvapadas)} tatvapadas in '{filename}'")
            print(f"👤 Authors found: {authors}")

    if not all_data:
        print("❌ No tatvapadas extracted.")
        return

    df = pd.DataFrame(all_data)
    output_csv = "tatvapada_extracted.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")

    print("\n✅ Extraction Complete!")
    print(f"📄 Total Tatvapadas: {len(df)}")
    print(f"👥 Unique Authors: {df['tatvapadakarara_hesaru'].nunique()}")
    print(f"📁 Output saved to: {output_csv}")

if __name__ == "__main__":
    main()
