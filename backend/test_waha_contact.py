import requests
from config import settings

headers = {"X-Api-Key": getattr(settings, 'WAHA_API_KEY', "123")}
try:
    res = requests.get(f"{settings.WAHA_URL}/api/contacts/82798413090865@c.us?session={settings.WAHA_SESSION}", headers=headers)
    print("c.us:", res.json())
except Exception as e:
    print(e)
    
try:
    res = requests.get(f"{settings.WAHA_URL}/api/contacts/82798413090865@lid?session={settings.WAHA_SESSION}", headers=headers)
    print("lid:", res.json())
except Exception as e:
    print(e)

try:
    res = requests.get(f"{settings.WAHA_URL}/api/contacts/917259510983@c.us?session={settings.WAHA_SESSION}", headers=headers)
    print("917259510983:", res.json())
except Exception as e:
    print(e)
