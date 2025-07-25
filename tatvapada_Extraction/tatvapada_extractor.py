import os
import re
import unicodedata
import pandas as pd
from docx import Document
from docx.shared import Pt

class TatvapadaExtractor:
    COLUMNS = [
        'tatvapadakosha',
        'samputa',
        'sheershike',
        'tatvapadakarar_hesaru',
        'mukhya_sheershike',
        'tatvapada_sankya_hesaru',
        'tatvapada'
    ]

    DIGIT_PATTERN = r'[೦೧೨೩೪೫೬೭೮೯0-9]'
    ENTRY_PATTERN = re.compile(rf'^0*({DIGIT_PATTERN}+)[\s\.]*.*')

    IGNORE_PREFIXES = ['ಪರಿವಿಡಿ']

    def __init__(self, input_folder, output_folder, consolidated_csv):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.consolidated_csv = consolidated_csv
        self.all_rows = []

    def clean_line(self, text):
        normalized = unicodedata.normalize('NFKC', text.replace('\u200b', '').replace('\u200c', ''))
        return re.sub(r'\s+', ' ', normalized).strip()

    def to_kannada(self, number: int) -> str:
        return ''.join({
            '0': '೦', '1': '೧', '2': '೨', '3': '೩', '4': '೪',
            '5': '೫', '6': '೬', '7': '೭', '8': '೮', '9': '೯'
        }[d] for d in str(number))

    def is_valid_mukhya_sheershike(self, line: str) -> bool:
        if not line:
            return False
        if self.ENTRY_PATTERN.match(line):
            return False
        if line.endswith(('||', '।', '॥')) or any(x in line for x in ['|', '।', '॥']):
            return False
        if len(line) > 60:
            return False
        return True

    def extract_from_docx(self, file_path):
        print(f'\n📄 Processing: {os.path.basename(file_path)}')
        doc = Document(file_path)
        paragraphs = [self.clean_line(p.text) for p in doc.paragraphs]
        non_empty = [p for p in paragraphs if p.strip()]

        if not non_empty:
            print("⚠️ Empty document.")
            return []

        tatvapadakosha = non_empty[0]
        samputa = next((p for p in non_empty if p.startswith('ಸಂಪುಟ')), '')

        sheershike = ''
        for p in non_empty:
            if p not in [tatvapadakosha, samputa] and not self.ENTRY_PATTERN.match(p):
                sheershike = p
                break

        tatvapadakarar_hesaru = sheershike

        rows = []
        current_entry = None
        current_lines = []
        current_mukhya_sheershike = ''
        started = False
        expected_number = 1

        for idx, para in enumerate(non_empty):
            # ✅ Skip ignored prefixes at paragraph level
            if any(para.startswith(prefix) for prefix in self.IGNORE_PREFIXES):
                print(f"⏭️ Skipping paragraph due to IGNORE prefix: {para}")
                continue

            match = self.ENTRY_PATTERN.match(para)
            if match:
                digit_prefix = match.group(1).strip()
                expected_kannada = self.to_kannada(expected_number)
                expected_english = str(expected_number)

                if not started:
                    if digit_prefix == expected_kannada or digit_prefix == expected_english:
                        started = True
                    else:
                        continue

                if digit_prefix != expected_kannada and digit_prefix != expected_english:
                    print(f"⛔ Stopped: Expected {expected_kannada}/{expected_english}, found {digit_prefix}")
                    break

                if current_entry:
                    rows.append({
                        'tatvapadakosha': tatvapadakosha,
                        'samputa': samputa,
                        'sheershike': sheershike,
                        'tatvapadakarar_hesaru': tatvapadakarar_hesaru,
                        'mukhya_sheershike': current_mukhya_sheershike,
                        'tatvapada_sankya_hesaru': current_entry,
                        'tatvapada': '\n'.join(current_lines).strip()
                    })
                    print(f'📌 Mukhya Sheershike: {current_mukhya_sheershike} | Sankhya Hesaru: {current_entry}')

                current_entry = para
                current_lines = []
                expected_number += 1

                for j in range(idx - 1, -1, -1):
                    prev_line = non_empty[j].strip()
                    if not prev_line:
                        continue
                    if self.is_valid_mukhya_sheershike(prev_line):
                        current_mukhya_sheershike = prev_line
                        break
            else:
                if started:
                    current_lines.append(para)

        if started and current_entry:
            rows.append({
                'tatvapadakosha': tatvapadakosha,
                'samputa': samputa,
                'sheershike': sheershike,
                'tatvapadakarar_hesaru': tatvapadakarar_hesaru,
                'mukhya_sheershike': current_mukhya_sheershike,
                'tatvapada_sankya_hesaru': current_entry,
                'tatvapada': '\n'.join(current_lines).strip()
            })
            print(f'📌 Mukhya Sheershike: {current_mukhya_sheershike}  Sankhya Hesaru: {current_entry}')

        if not rows:
            print("⚠️ No tatvapadas extracted! Printing all checked paragraphs:")
            for i, p in enumerate(non_empty):
                print(f"{i + 1:02}: {p}")

        print(f"✅ Extracted {len(rows)} tatvapadas from {os.path.basename(file_path)}")
        return rows

    def save_to_docx_with_nudi_font(self, rows, output_path):
        doc = Document()
        for row in rows:
            para = doc.add_paragraph()
            run = para.add_run(f"{row['tatvapada_sankya_hesaru']}\n{row['tatvapada']}\n")
            run.font.name = 'NudiUni01k'
            run.font.size = Pt(14)
        doc.save(output_path)

    def process_single_file(self, filename):
        file_path = os.path.join(self.input_folder, filename)
        rows = self.extract_from_docx(file_path)
        self.all_rows.extend(rows)

        df = pd.DataFrame(rows, columns=self.COLUMNS)
        output_csv = os.path.join(self.output_folder, filename.replace('.docx', '.csv'))
        df.to_csv(output_csv, index=False, encoding='utf-8')

        output_docx = os.path.join(self.output_folder, filename.replace('.docx', '_nudi.docx'))
        self.save_to_docx_with_nudi_font(rows, output_docx)

    def process_all_files(self):
        print(f'\n📂 Scanning: {self.input_folder}\n')
        os.makedirs(self.output_folder, exist_ok=True)

        for filename in sorted(os.listdir(self.input_folder)):
            if filename.endswith('.docx'):
                self.process_single_file(filename)

        df_all = pd.DataFrame(self.all_rows, columns=self.COLUMNS)
        df_all.to_csv(self.consolidated_csv, index=False, encoding='utf-8')
        print(f"\n📦 All tatvapadas saved to {self.consolidated_csv} ({len(self.all_rows)} rows)\n")

if __name__ == '__main__':
    input_folder = './tatvapada_docs'
    output_folder = './tatvapada_output'
    consolidated_csv = 'tatvapada_extracted_all.csv'

    extractor = TatvapadaExtractor(input_folder, output_folder, consolidated_csv)
    extractor.process_all_files()
