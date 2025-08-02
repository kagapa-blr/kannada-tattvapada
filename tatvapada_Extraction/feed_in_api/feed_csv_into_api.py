import pandas as pd
import requests
import time

# API endpoint
API_URL = "http://localhost:5000/api/tatvapada/add"

extracted_file = r"C:\Users\techk\Desktop\kagapa\kannada-tattvapada\tatvapada_Extraction\output_csv\ಕರ್ನಾಟಕ ಸಮಗ್ರ ತತ್ವಪದಗಳ ಜನಪ್ರಿಯ ಸಂಪುಟ ಮಾಲೆ ಸಂಪುಟ ೨.csv"
# Load extracted tatvapada data
df = pd.read_csv(extracted_file, encoding="utf-8-sig")

print(f"Total rows to upload: {len(df)}\n")

success_count = 0
fail_count = 0

for index, row in df.iterrows():
    payload = {
        "samputa_sankhye": str(row.get("samputa_sankhye", "")),
        "tatvapadakosha_sheershike": row.get("tatvapadakosha_sheershike", ""),
        "tatvapada_author_id": row.get("tatvapada_author_id", "-"),
        "tatvapadakarara_hesaru": row.get("tatvapadakarara_hesaru", ""),
        "vibhag": row.get("vibhag", "-"),
        "tatvapada_sheershike": row.get("tatvapada_sheershike", ""),
        "tatvapada_sankhye": str(row.get("tatvapada_sankhye", "")),
        "tatvapada_first_line": row.get("tatvapada_first_line", ""),
        "tatvapada": row.get("tatvapada", ""),
        "bhavanuvada": row.get("bhavanuvada", "-"),
        "klishta_padagalu_artha": row.get("klishta_padagalu_artha", "-"),
        "tippani": row.get("tippani", "-")
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code in (200, 201):
            print(f"Row {index + 1} uploaded.")
            success_count += 1
        else:
            print(f"Row {index + 1} failed. Status: {response.status_code}, Response: {response.text}")
            fail_count += 1

        # Optional delay
        # time.sleep(0.2)

    except Exception as e:
        print(f"Error uploading row {index + 1}: {e}")
        fail_count += 1

print("\nUpload complete!")
print(f"Success: {success_count}")
print(f"Failed: {fail_count}")
