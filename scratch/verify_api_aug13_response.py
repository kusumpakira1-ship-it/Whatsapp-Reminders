"""
Verify API output for reminders on 2026-08-13.
"""
import urllib.request, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')

# Test direct PHP execution or Hostinger HTTP endpoint
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=reminders&date=2026-08-13&t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print("HTTP Status:", resp.status)
        if content.strip().startswith('['):
            data = json.loads(content)
            print(f"Total Reminders Returned: {len(data)}")
            for r in data:
                if r['id'] in [188, 185, 249, 263, 269]:
                    print(f"\nReminder #{r['id']} ({r['person_name']}):")
                    print("  is_submitted:", r.get('is_submitted'))
                    print("  sub_reports_status:", r.get('sub_reports_status'))
                    print("  report_types:", r.get('report_types'))
        else:
            print("Response is not JSON (likely cached HTML):", content[:200])
except Exception as e:
    print("API Test Error:", e)

