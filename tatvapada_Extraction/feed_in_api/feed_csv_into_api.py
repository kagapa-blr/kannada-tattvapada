import time
import pandas as pd
import requests
import os
import sys

BASE_URL = "http://127.0.0.1:5000"

GENERATE_TOKEN_URL = f"{BASE_URL}/generate-token"
UPLOAD_URL = f"{BASE_URL}/api/tatvapada/add"

# ----------------------------
# Generate JWT Token
# ----------------------------
def generate_token(username, password):
    try:
        response = requests.post(
            GENERATE_TOKEN_URL,
            json={"username": username, "password": password}
        )

        if response.status_code != 200:
            print("Token generation failed:", response.text)
            return None

        data = response.json()
        return data.get("access_token")

    except Exception as e:
        print("Error generating token:", str(e))
        return None


# ----------------------------
# Upload CSV Folder
# ----------------------------
def upload_csv_folder(folder_path, token):

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

    if not csv_files:
        print("No CSV files found.")
        return

    total_success = 0
    total_fail = 0
    failed_rows_list = []

    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        print(f"\nProcessing file: {csv_file}")

        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        except Exception as e:
            print(f"Failed to read {csv_file}: {e}")
            continue

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
                response = session.post(UPLOAD_URL, json=payload)

                if response.status_code in (200, 201):
                    success_count += 1
                else:
                    fail_count += 1
                    failed_rows_list.append({
                        "file": csv_file,
                        "row": index + 1,
                        "status": response.status_code,
                        "response": response.text
                    })

            except Exception as e:
                fail_count += 1
                failed_rows_list.append({
                    "file": csv_file,
                    "row": index + 1,
                    "status": "Exception",
                    "response": str(e)
                })

        print(f"Finished {csv_file}: Success={success_count}, Failed={fail_count}")

        total_success += success_count
        total_fail += fail_count

        print("Waiting 5 seconds before next file...")
        time.sleep(5)

    print("\nUpload Summary")
    print("Total Success:", total_success)
    print("Total Failed:", total_fail)

    if failed_rows_list:
        failed_df = pd.DataFrame(failed_rows_list)
        failed_df.to_csv("failed_rows_report.csv", index=False)
        print("Failed rows saved to failed_rows_report.csv")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    token = generate_token(username, password)

    if not token:
        print("Unable to proceed without token.")
        sys.exit(1)

    print("Token generated successfully.\n")

    folder_path = input("Enter the folder path containing CSV files: ").strip()

    if not os.path.isdir(folder_path):
        print("Invalid folder path.")
        sys.exit(1)

    upload_csv_folder(folder_path, token)
