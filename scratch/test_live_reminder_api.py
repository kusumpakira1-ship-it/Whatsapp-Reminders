import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

req = urllib.request.Request('https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?route=reminders', headers={'User-Agent': 'Mozilla/5.0'})
try:
    data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    print(f"Total Reminders fetched from live website API: {len(data)}\n")
    for r in data:
        p_name = str(r.get('person_name') or '').lower()
        g_name = str(r.get('group_name') or '').lower()
        if 'poornima' in p_name or 'aiot' in g_name or 'alliance' in g_name:
            print("Live Reminder Verification Result:")
            print(f"  ID: {r.get('id')} | Person: {r.get('person_name')} | Group: {r.get('group_name')}")
            print(f"  Status: {r.get('status')} | Submitted: {r.get('is_submitted')} | Badge: {r.get('submission_badge')}")
            print(f"  Verification Details: {r.get('verification_details')}")
            print("-" * 60)
except Exception as e:
    print('API Fetch error:', e)
