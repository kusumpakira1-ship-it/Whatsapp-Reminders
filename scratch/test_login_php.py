"""
Test login to https://sunfra.com/farm/sunfra/login/login.php
"""
import requests, sys, json
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'
})

login_url = "https://sunfra.com/farm/sunfra/login/login.php"
post_data = {
    'username': 'kusum',
    'password': 'Kusum@2026Bb!',
    'remember_me': '1'
}

print("POSTing login to:", login_url)
resp = session.post(login_url, data=post_data)
print("Login Response Code:", resp.status_code)
print("Login Response Text:", resp.text)

print("\nTesting endpoint fetch after login:")
endpoints = {
    "Mortality (14 Aug)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14",
    "Production (14 Aug)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php?date=2026-08-14",
    "Birds Weight (14 Aug)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php?date=2026-08-14",
    "Batch / Live Birds": "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
}

for title, url in endpoints.items():
    print(f"\n--- {title} ---")
    r = session.get(url)
    print("Status:", r.status_code)
    print("Raw text:", r.text[:300])

