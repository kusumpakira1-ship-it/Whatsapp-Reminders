import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?route=reminders'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    data = json.loads(html)
    for r in data:
        p_name = str(r.get('person_name') or '').lower()
        if 'poornima' in p_name or r.get('id') == 288:
            print("=== LIVE VERIFICATION RESULT FOR POORNIMA ===")
            print(f"ID: {r.get('id')} | Person: {r.get('person_name')} | Submitted: {r.get('is_submitted')}")
            print(f"Details:\n{r.get('verification_details')}")
except Exception as e:
    print("API fetch error:", e)
