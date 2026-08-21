"""
Fetch real WAHA groups list from WAHA API or server settings.
"""
import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from config import settings

waha_url = f"{settings.WAHA_API_URL}/api/default/chats"
print(f"Connecting to WAHA API at: {waha_url}")

try:
    resp = requests.get(waha_url, headers={"X-Api-Key": settings.WAHA_API_KEY}, timeout=10)
    chats = resp.json()
    print(f"Found {len(chats)} chats in WAHA:")
    for c in chats:
        name = c.get('name', '')
        jid = c.get('id', '')
        if 'corporate' in name.lower() or 'p&l' in name.lower() or 'p & l' in name.lower() or 'sunfra' in name.lower():
            print(f"  ⭐ MATCH: Name='{name}' | JID='{jid}'")
except Exception as e:
    print(f"WAHA request failed: {e}")
