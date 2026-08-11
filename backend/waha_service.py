import os
import requests
import logging
from config import settings

logger = logging.getLogger(__name__)

BLOCKED_PHONES = ['9346763549', '919346763549']

def send_waha_message(chat_id: str, text: str, session: str = None, mentions: list = None) -> bool:
    """Send a text message via WAHA."""
    clean_chat = "".join(filter(str.isdigit, str(chat_id or '')))
    if any(b in clean_chat for b in BLOCKED_PHONES):
        print(f"Blocked message sending to {chat_id} per user directive.")
        return False

    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us') and not chat_id.endswith('@lid'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": session if session else settings.WAHA_SESSION
    }
    if mentions:
        payload["mentions"] = mentions
    
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code not in (200, 201):
            print(f"WAHA sendText failed: {response.status_code} - {response.text}")
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send WAHA message: {e}")
        return False

def send_waha_file(chat_id: str, file_path: str, caption: str = "", session: str = None) -> bool:
    """Send a file (PDF/Image/Excel) via WAHA using public HTTPS URL hosted on Hostinger for 100% reliable WhatsApp delivery."""
    clean_chat = "".join(filter(str.isdigit, str(chat_id or '')))
    if any(b in clean_chat for b in BLOCKED_PHONES):
        logger.info(f"Blocked file sending to {chat_id} per user directive.")
        return False
    
    if not chat_id.endswith('@c.us') and not chat_id.endswith('@g.us') and not chat_id.endswith('@lid'):
        chat_id += '@c.us'

    url = f"{settings.WAHA_URL}/api/sendFile"
    
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
        
    try:
        filename = os.path.basename(file_path)
        
        # 1. Upload to Hostinger FTP for public HTTPS access
        file_url = f"http://fastapi_backend:8000/media/reports/{filename}"
        try:
            import ftplib
            host = "145.223.17.70"
            user = "u632391467.kusum12345"
            passwd = "Kusum@1234!"
            ftp = ftplib.FTP()
            ftp.connect(host, 21, timeout=10)
            ftp.login(user, passwd)
            try: ftp.cwd('Whatsapp_Rem')
            except Exception: pass
            try: ftp.mkd('reports')
            except Exception: pass
            try: ftp.cwd('reports')
            except Exception: pass
            
            with open(file_path, 'rb') as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()
            file_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/reports/{filename}"
            logger.info(f"Uploaded {filename} to Hostinger FTP public HTTPS URL: {file_url}")
        except Exception as ftperr:
            logger.error(f"Hostinger FTP upload error: {ftperr}, falling back to internal URL.")

        mimetype = "application/pdf"
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg']:
            mimetype = f"image/{ext.replace('.', '')}"
            if mimetype == "image/jpg":
                mimetype = "image/jpeg"
        elif ext in ['.xlsx', '.xls']:
            mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif ext == '.pdf':
            mimetype = "application/pdf"

        payload = {
            "chatId": chat_id,
            "file": {
                "mimetype": mimetype,
                "filename": filename,
                "url": file_url
            },
            "caption": caption,
            "session": session if session else settings.WAHA_SESSION
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code not in (200, 201):
            logger.error(f"WAHA sendFile failed: {response.status_code} - {response.text}")
        return response.status_code in (200, 201)
    except Exception as e:
        logger.error(f"Failed to send WAHA file: {e}")
        return False

def download_waha_media(message_id: str, media_url: str = None, mimetype: str = None, filename: str = None) -> str:
    """Download media from WAHA and save it locally."""
    import urllib.parse
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
        
    if media_url:
        try:
            # Replace localhost or external hostname in media_url with waha's internal container name
            parsed_media = urllib.parse.urlparse(media_url)
            parsed_waha = urllib.parse.urlparse(settings.WAHA_URL)
            url = parsed_media._replace(netloc=parsed_waha.netloc).geturl()
        except Exception as e:
            print(f"Failed to parse media URL {media_url}: {e}")
            url = media_url
    else:
        encoded_msg_id = urllib.parse.quote(message_id)
        url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/messages/{encoded_msg_id}/download"
        
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            # Determine extension using mimetype, Content-Type, or filename (case-insensitive)
            check_mime = (mimetype or response.headers.get("Content-Type", "")).lower()
            ext = ".bin"
            if "jpeg" in check_mime or "jpg" in check_mime:
                ext = ".jpg"
            elif "png" in check_mime:
                ext = ".png"
            elif "pdf" in check_mime:
                ext = ".pdf"
            elif filename and "." in filename:
                ext = f".{filename.split('.')[-1].lower()}"
            
            # Sniff magic bytes if extension is still generic
            if ext == ".bin" and response.content:
                header = response.content[:10]
                if header.startswith(b'\xff\xd8\xff'):
                    ext = ".jpg"
                elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                    ext = ".png"
                elif header.startswith(b'%PDF-'):
                    ext = ".pdf"
            
            os.makedirs("/app/media", exist_ok=True)
            file_path = f"/app/media/{message_id}{ext}"
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            print(f"WAHA media download returned status code {response.status_code} for URL: {url}")
    except Exception as e:
        print(f"Failed to download media for {message_id}: {e}")
    return ""

def get_waha_chat_name(chat_id: str) -> str:
    """Fetch chat/group name from WAHA API."""
    if not chat_id.endswith('@g.us') and not chat_id.endswith('@c.us') and not chat_id.endswith('@s.whatsapp.net') and not chat_id.endswith('@lid'):
        if '-' in chat_id or len(chat_id) > 15:
            chat_id += '@g.us'
        else:
            chat_id += '@c.us'

    # If it is a group, try fetching from the groups endpoint first (more reliable in NOWEB)
    if chat_id.endswith('@g.us'):
        url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/groups"
        headers = {"Accept": "application/json"}
        api_key = os.getenv("WAHA_API_KEY", "123")
        if api_key:
            headers["X-Api-Key"] = api_key
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                groups_dict = response.json()
                if isinstance(groups_dict, dict):
                    group_info = groups_dict.get(chat_id)
                    if group_info and group_info.get("subject"):
                        return group_info.get("subject")
                elif isinstance(groups_dict, list):
                    for g in groups_dict:
                        g_id = g.get("id")
                        if g_id == chat_id and g.get("subject"):
                            return g.get("subject")
        except Exception as e:
            print(f"Failed to fetch group name from groups API: {e}")

    # Fallback to the chats endpoint
    url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/chats"
    headers = {"Accept": "application/json"}
    
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

def get_session_status(session: str) -> str:
    """Fetch the status of a WAHA session."""
    url = f"{settings.WAHA_URL}/api/sessions/{session}"
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
    
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json().get('status', 'UNKNOWN')
        except Exception as e:
            logger.warning(f"Session status attempt {attempt+1} failed: {e}")
    
    # Fallback to GET /api/sessions list
    try:
        url_all = f"{settings.WAHA_URL}/api/sessions"
        resp = requests.get(url_all, headers=headers, timeout=5)
        if resp.status_code == 200:
            for s in resp.json():
                if s.get('name') == session:
                    return s.get('status', 'UNKNOWN')
    except Exception as e:
        logger.error(f"Failed to fetch session list fallback: {e}")
        
    return "WORKING" # Default fallback when WAHA service is responding

def get_session_qr(session: str) -> str:
    """Download the QR code image for a WAHA session and return the local file path."""
    url = f"{settings.WAHA_URL}/api/{session}/auth/qr?format=image"
    headers = {"Accept": "image/png"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key:
        headers["X-Api-Key"] = api_key
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            os.makedirs("/app/media", exist_ok=True)
            file_path = f"/app/media/qr_{session}.png"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        return ""
    except Exception as e:
        print(f"Failed to download session QR: {e}")
        return ""
