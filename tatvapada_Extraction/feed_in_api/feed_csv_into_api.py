import pandas as pd
import requests
import time

# TODO: Replace this with your actual API endpoint URL
API_URL = "http://localhost:5000/api/tatvapada/add"

# Load extracted tatvapada data
df = pd.read_csv("tatvapada_extracted.csv", encoding="utf-8-sig")

print(f"📄 Total rows to upload: {len(df)}\n")

success_count = 0
fail_count = 0

for index, row in df.iterrows():
    payload = {
        "tatvapadakosha": row.get("tatvapadakosha", ""),
        "samputa_sankhye": str(row.get("samputa_sankhye", "")),
        "tatvapadakosha_sheershike": row.get("tatvapadakosha_sheershike", ""),
        "tatvapadakarara_hesaru": row.get("tatvapadakarara_hesaru", ""),
        "mukhya_sheershike": row.get("mukhya_sheershike", ""),
        "tatvapada_sankhye": str(row.get("tatvapada_sankhye", "")),
        "tatvapada_hesaru": row.get("tatvapada_hesaru", ""),
        "tatvapada_first_line": row.get("tatvapada_first_line", ""),
        "tatvapada": row.get("tatvapada", "")
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Row {index + 1} uploaded.")
            success_count += 1
        else:
            print(f"❌ Row {index + 1} failed. Status: {response.status_code}")
            fail_count += 1

        # Optional: wait between requests to avoid rate limiting
        # time.sleep(0.2)

    except Exception as e:
        print(f"❌ Error uploading row {index + 1}: {e}")
        fail_count += 1

print("\n📦 Upload complete!")
print(f"✅ Success: {success_count}")
print(f"❌ Failed: {fail_count}")
