# utils/download_if_missing.py
import os
import requests

def download_file(url, local_path):
    if not os.path.exists(local_path):
        print(f"📥 Downloading: {local_path}")
        r = requests.get(url)
        with open(local_path, "wb") as f:
            f.write(r.content)
