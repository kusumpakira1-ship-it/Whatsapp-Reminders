"""
Inspect login redirect flow for username='admin', password='Kusum@2026Bb!'
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
})

login_url = "https://sunfra.com/farm/sunfra/"
resp = session.post(login_url, data={'username': 'admin', 'password': 'Kusum@2026Bb!', 'remember_me': '1'}, allow_redirects=True)

print("Final URL after login POST:", resp.url)
print("Session Cookies:", session.cookies.get_dict())
print("Response text snippet:\n", resp.text[:400])

# Fetch batch_json_to_web.php
r = session.get("https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php")
print("\n--- batch_json_to_web.php ---")
print("Status:", r.status_code)
print("Snippet:\n", r.text[:400])

# Fetch mortality
r_mort = session.get("https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14")
print("\n--- supervisor_shead_mortality_json_to_web.php ---")
print("Status:", r_mort.status_code)
print("Snippet:\n", r_mort.text[:400])

