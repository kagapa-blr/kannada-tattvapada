import os
import requests
import mammoth
import base64
from bs4 import BeautifulSoup


class DocumentUploader:
    def __init__(self, api_url: str, folder_path: str):
        self.api_url = api_url
        self.folder_path = folder_path

    @staticmethod
    def read_docx_content(filepath: str) -> str:
        """
        Read .docx file and convert it to HTML fragment (with formatting).
        Inline images as base64.
        """
        def inline_image(image):
            with image.open() as img_bytes:
                encoded = base64.b64encode(img_bytes.read()).decode("utf-8")
                return {"src": f"data:{image.content_type};base64,{encoded}"}

        with open(filepath, "rb") as docx_file:
            result = mammoth.convert_to_html(
                docx_file, convert_image=mammoth.images.inline(inline_image)
            )
            html = result.value
            soup = BeautifulSoup(html, "html.parser")
            return str(soup).strip()

    @staticmethod
    def extract_title_description(html: str):
        """
        Extract:
        - title: first non-empty line (usually 'ಸಂಪುಟ - ೩೮')
        - description: first line that contains 'ತತ್ವಪದ' or 'ತತ್ತ್ವಪದ'
        """
        soup = BeautifulSoup(html, "html.parser")

        # Get plain text lines
        lines = [line.strip() for line in soup.get_text(separator="\n").split("\n") if line.strip()]

        title = lines[0] if lines else "Untitled"

        description = None
        for line in lines[1:]:
            if "ತತ್ವಪದ" in line or "ತತ್ತ್ವಪದ" in line:
                description = line
                break

        return title, description

    def upload_document(self, title: str, description: str, content: str):
        """
        Send POST request to API.
        """
        payload = {
            "title": title,
            "content": content
        }
        if description:
            payload["description"] = description

        try:
            response = requests.post(self.api_url, json=payload)

            try:
                resp_json = response.json()
            except ValueError:
                resp_json = {"raw_response": response.text}

            if response.status_code == 201:
                print(f"✅ Uploaded: {title}")
            elif response.status_code == 409:
                print(f"⚠️ Already exists: {title}")
            else:
                print(f"⚠️ Failed ({title}) -> {response.status_code}: {resp_json}")

        except Exception as e:
            print(f"❌ Error uploading {title}: {e}")

    def process_all(self):
        """
        Loop through all .docx files in folder and upload them.
        """
        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith(".docx"):
                filepath = os.path.join(self.folder_path, filename)
                try:
                    content = self.read_docx_content(filepath)
                    if not content:
                        print(f"⚠️ Skipping {filename} (empty content)")
                        continue

                    title, description = self.extract_title_description(content)

                    self.upload_document(title, description, content)
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")


if __name__ == "__main__":
    # ========== CONFIG ==========
    API_URL = "http://127.0.0.1:5000/api/documents/"
    folder_path = input("Enter DOCX folder path: ").strip()
    # ============================

    uploader = DocumentUploader(API_URL, folder_path)
    uploader.process_all()
