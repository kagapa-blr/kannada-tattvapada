import pandas as pd
import requests
import os


# API endpoint
#API_URL = f"http://localhost:5000/api/tatvapada/add"
API_URL = f"https://kagapa.com/kannada-tattvapada/api/tatvapada/add"

# Ask for folder path
folder_path = input("Enter the folder path containing CSV files: ").strip()

# Check if folder exists
if not os.path.isdir(folder_path):
    print("Invalid folder path.")
    exit(1)

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

if not csv_files:
    print("No CSV files found in the folder.")
    exit(1)

total_success = 0
total_fail = 0

for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    print(f"\nProcessing file: {csv_file}")

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    except Exception as e:
        print(f"Failed to read {csv_file}: {e}")
        continue

    print(f"Total rows to upload in {csv_file}: {len(df)}\n")

    success_count = 0
    fail_count = 0

    for index, row in df.iterrows():
        payload = {
            "samputa_sankhye": str(row.get("samputa_sankhye", "")),
            "tatvapadakosha_sheershike": row.get("tatvapadakosha_sheershike", ""),
            "tatvapadakarara_hesaru": row.get("tatvapadakarara_hesaru", ""),
            "vibhag": row.get("vibhag", "-"),
            "tatvapada_sheershike": row.get("tatvapada_sheershike", ""),
            "tatvapada_sankhye": str(row.get("tatvapada_sankhye", "")),
            "tatvapada_first_line": row.get("tatvapada_first_line", ""),
            "tatvapada": row.get("tatvapada", ""),
            "bhavanuvada": row.get("bhavanuvada", "-"),
            "klishta_padagalu_artha": row.get("klishta_padagalu_artha", "-"),
            "tippani": row.get("tippani", "-"),
        }

        try:
            response = requests.post(API_URL, json=payload)

            if response.status_code in (200, 201):
                print(f"Row {index + 1} uploaded.")
                success_count += 1
            else:
                print(f"Row {index + 1} failed. Status: {response.status_code}, Response: {response.text}")
                fail_count += 1

        except Exception as e:
            print(f"Error uploading row {index + 1}: {e}")
            fail_count += 1

    print(f"\nFinished uploading {csv_file}: Success: {success_count}, Failed: {fail_count}")

    total_success += success_count
    total_fail += fail_count

print("\nAll files processed.")
print(f"Total Success: {total_success}")
print(f"Total Failed: {total_fail}")
