import os
import requests
from core.config import settings

def send_waha_message(chat_id: str, text: str) -> bool:
    """Send a text message via WAHA."""
    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": settings.WAHA_SESSION
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Accept": "application/json"})
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send WAHA message: {e}")
        return False

def send_waha_file(chat_id: str, file_path: str, caption: str = "") -> bool:
    """Send a file (PDF/Excel) via WAHA using multiform-data or file URL depending on WAHA config.
    WAHA Core supports sending files by URL or uploading them."""
    
    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendFile"
    
    try:
        with open(file_path, "rb") as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {
                "chatId": chat_id,
                "caption": caption,
                "session": settings.WAHA_SESSION
            }
            response = requests.post(url, data=data, files=files)
            return response.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send WAHA file: {e}")
        return False

def download_waha_media(message_id: str) -> str:
    """Download media from WAHA for a given message ID and save it locally."""
    url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/messages/{message_id}/download"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Check Content-Type to determine extension
            content_type = response.headers.get("Content-Type", "")
            ext = ".bin"
            if "jpeg" in content_type or "jpg" in content_type: ext = ".jpg"
            elif "png" in content_type: ext = ".png"
            elif "pdf" in content_type: ext = ".pdf"
            
            os.makedirs("/app/media", exist_ok=True)
            file_path = f"/app/media/{message_id}{ext}"
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        print(f"Failed to download media for {message_id}: {e}")
    return ""
