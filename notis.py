import requests
from dotenv import load_dotenv
import os

load_dotenv()

NTFY_URL = os.getenv("NTFY_URL")

def notify(message, title="homeserver1", priority="default", tags=None):
    headers = {
        "Title": title.encode('utf-8').decode('latin-1'),
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = tags
    
    try:
        requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers=headers,
            timeout=5
        )
    except Exception as e:
        print(f"Notifikation misslyckades: {e}")