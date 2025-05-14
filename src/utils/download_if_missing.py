import os
import requests

def download_file(url, local_path):
    """Download a file from a URL if it does not already exist."""
    if not os.path.exists(local_path):
        print(f"📥 Downloading: {local_path}")
        r = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(r.content)

def download_file_from_google_drive(file_id, dest_path):
    """
    Download a file from Google Drive given its file ID.
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    download_file(url, dest_path)
