import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index1.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/app.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/trigger_reminder.php"
]

for u in urls:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode('utf-8', errors='ignore')
            has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
            print(f"URL: {u} -> len={len(html)}, Mon-Sat={has_mon_sat}")
    except Exception as e:
        print(f"URL: {u} -> Error: {e}")
