import time
import pandas as pd
import requests
import os

# API endpoint
#API_URL = f"https://kagapa.com/kannada-tattvapada/api/tatvapada/add"
API_URL = f"http://localhost:5000/api/tatvapada/add"

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
failed_rows_list = []  # To store all failed rows

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

        # Print key info before inserting
        print(f"Inserting row {index + 1}: "
              f"samputa_sankhye={payload['samputa_sankhye']}, "
              f"tatvapadakarara_hesaru={payload['tatvapadakarara_hesaru']}, "
              f"tatvapada_sankhye={payload['tatvapada_sankhye']}")

        try:
            response = requests.post(API_URL, json=payload)

            if response.status_code in (200, 201):
                print(f"Row {index + 1} uploaded successfully.")
                success_count += 1
            else:
                print(f"Row {index + 1} failed. Status: {response.status_code}")
                fail_count += 1
                failed_rows_list.append({
                    "file": csv_file,
                    "row_index": index + 1,
                    "data": row.to_dict(),
                    "status": response.status_code,
                    "response": response.text
                })

        except Exception as e:
            print(f"Error uploading row {index + 1}: {e}")
            fail_count += 1
            failed_rows_list.append({
                "file": csv_file,
                "row_index": index + 1,
                "data": row.to_dict(),
                "status": "Exception",
                "response": str(e)
            })

    print(f"\nFinished uploading {csv_file}: Success: {success_count}, Failed: {fail_count}")

    total_success += success_count
    total_fail += fail_count

    # Wait for 1 minute before processing next CSV
    print("Waiting 15 seconds before processing next file...")
    time.sleep(15)

print("\nAll files processed.")
print(f"Total Success: {total_success}")
print(f"Total Failed: {total_fail}")

# Display failed rows as a table
if failed_rows_list:
    print("\nFailed Rows Table:")
    failed_df = pd.DataFrame(failed_rows_list)
    print(failed_df)
else:
    print("\nNo failed rows.")
