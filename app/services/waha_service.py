import os
import requests
from core.config import settings

def send_waha_message(chat_id: str, text: str) -> bool:
    """Send a text message via WAHA."""
    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us') and not chat_id.endswith('@lid'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": settings.WAHA_SESSION
    }
    
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in (200, 201):
            print(f"WAHA sendText failed: {response.status_code} - {response.text}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send WAHA message: {e}")
        return False

def send_waha_file(chat_id: str, file_path: str, caption: str = "") -> bool:
    """Send a file (PDF/Excel) via WAHA using multiform-data or file URL depending on WAHA config.
    WAHA Core supports sending files by URL or uploading them."""
    
    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us') and not chat_id.endswith('@lid'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendFile"
    
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
        
    try:
        # Hostinger/Docker backend URL (accessible by waha container)
        # file_path is like /app/media/reports/report.pdf
        # Since we mounted /media to /app/media in fastapi, the url is /media/...
        relative_path = file_path.replace('/app/', '')
        file_url = f"http://fastapi_backend:8000/{relative_path}"
        
        mimetype = "application/pdf" if file_path.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        payload = {
            "chatId": chat_id,
            "file": {
                "mimetype": mimetype,
                "filename": os.path.basename(file_path),
                "url": file_url
            },
            "caption": caption,
            "session": settings.WAHA_SESSION
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code not in (200, 201):
            print(f"WAHA sendFile failed: {response.status_code} - {response.text}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send WAHA file: {e}")
        return False

def download_waha_media(message_id: str) -> str:
    """Download media from WAHA for a given message ID and save it locally."""
    url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/messages/{message_id}/download"
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
        
    try:
        response = requests.get(url, headers=headers)
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

def get_waha_chat_name(chat_id: str) -> str:
    """Fetch chat/group name from WAHA API."""
    if not chat_id.endswith('@g.us') and not chat_id.endswith('@c.us'):
        if '-' in chat_id or len(chat_id) > 15:
            chat_id += '@g.us'
        else:
            chat_id += '@c.us'

    # The typical WAHA API for chats is /api/{session}/chats
    url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/chats"
    headers = {"Accept": "application/json"}
    
    # Check if we should pass API key
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
        
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            chats = response.json()
            for chat in chats:
                chat_id_val = chat.get('id')
                if isinstance(chat_id_val, dict):
                    chat_id_val = chat_id_val.get('_serialized')
                
                if chat_id_val == chat_id:
                    return chat.get('name', chat_id)
    except Exception as e:
        print(f"Failed to fetch chat name for {chat_id}: {e}")
    return chat_id
