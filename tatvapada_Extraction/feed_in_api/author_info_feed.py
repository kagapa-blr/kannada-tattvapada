import os
import re
import requests
import mammoth   # pip install mammoth


class AuthorUploader:
    def __init__(self, api_url: str, folder_path: str):
        self.api_url = api_url
        self.folder_path = folder_path

    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Keep only Kannada letters from filename.
        """
        name = os.path.splitext(filename)[0]
        name = re.sub(r"[^ಀ-೿]+", "", name)
        return name.strip()

    @staticmethod
    def read_docx_content(filepath: str) -> str:
        """
        Read .docx file and convert it to clean HTML.
        """
        with open(filepath, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value  # The HTML string
            return html.strip()

    def upload_author(self, author_name: str, content: str):
        """
        Send POST request to API.
        """
        payload = {
            "author_name": author_name,
            "content": content
        }
        try:
            response = requests.post(self.api_url, json=payload)

            # Try parsing JSON safely
            try:
                resp_json = response.json()
            except ValueError:
                resp_json = {"raw_response": response.text}

            if response.status_code == 201:
                print(f"✅ Uploaded: {author_name}")
            elif response.status_code == 409:
                print(f"⚠️ Already exists: {author_name}")
            else:
                print(f"⚠️ Failed ({author_name}) -> {response.status_code}: {resp_json}")

        except Exception as e:
            print(f"❌ Error uploading {author_name}: {e}")

    def process_all(self):
        """
        Loop through all .docx files in folder and upload them.
        """
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".docx"):
                filepath = os.path.join(self.folder_path, filename)
                author_name = self.clean_filename(filename)
                content = self.read_docx_content(filepath)

                if not author_name or not content:
                    print(f"Skipping {filename} (empty name/content)")
                    continue

                self.upload_author(author_name, content)


if __name__ == "__main__":
    # ========== CONFIG ==========
    API_URL = "http://127.0.0.1:5000/api/v1/authors"
    #API_URL = "https://kagapa.com/kannada-tattvapada/api/v1/authors"
    DOCX_FOLDER = r"C:\Users\techk\Downloads\tattvapadakaararu\tattvapadakaararu"
    # ============================

    uploader = AuthorUploader(API_URL, DOCX_FOLDER)
    uploader.process_all()
