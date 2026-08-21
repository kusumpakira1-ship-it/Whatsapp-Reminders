"""
Test exact HTML content of live website https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v=123
"""
import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v={int(time.time())}"
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers)
html = r.text

print(f"URL: {url}")
print(f"Status Code: {r.status_code}")
print(f"HTML Length: {len(html)} bytes")
print(f"Has 'resetAllSubReports': {'resetAllSubReports' in html}")
print(f"Has 'confirmToggleSubReport': {'confirmToggleSubReport' in html}")
print(f"Has 'confirmToggleTaskSubReport': {'confirmToggleTaskSubReport' in html}")
print(f"Has 'button type=\"button\"': {'button type=\"button\"' in html}")

# Find lines containing resetAllSubReports or Undone
for line in html.splitlines():
    if 'resetAllSubReports' in line or 'Undone' in line:
        print(f"MATCH LINE: {line.strip()}")
