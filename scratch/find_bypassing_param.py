"""
Test which query parameters force Hostinger CDN to execute live PHP code instead of returning static cached HTML
"""
import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

base = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php"

params = [
    "?app=1",
    "?view=1",
    "?page=1",
    "?live=1",
    f"?ts={int(time.time())}",
    f"?reload={int(time.time())}",
    "?action=reminders_page",
    "?id=1"
]

for p in params:
    url = base + p
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        has_tracer = "EXECUTED_FILE" in r.text
        print(f"Param '{p}' => Status: {r.status_code} | Length: {len(r.text)} | HasTracer: {has_tracer}")
    except Exception as e:
        print(f"Error {p}: {e}")
