import os
import requests

def download_file(url, local_path):
    if not os.path.exists(local_path):
        print(f"📥 Downloading: {local_path}")
        r = requests.get(url, stream=True)
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def download_file_from_google_drive(file_id, dest_path):
    """
    Download a file from Google Drive, including large files with confirmation token.
    """
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value
        return None

    def save_response_content(response, destination):
        with open(destination, "wb") as f:
            for chunk in response.iter_content(32768):
                if chunk:
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    save_response_content(response, dest_path)
    print(f"✅ Downloaded: {dest_path}")
