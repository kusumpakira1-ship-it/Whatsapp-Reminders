"""
Inspect headers and cookies when POSTing admin / Kusum@2026Bb!
"""
import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
})

login_url = "https://sunfra.com/farm/sunfra/"
resp = session.post(login_url, data={'username': 'admin', 'password': 'Kusum@2026Bb!', 'remember_me': '1'}, allow_redirects=False)

print("POST Status Code:", resp.status_code)
print("POST Response Headers:", dict(resp.headers))
print("Session Cookies:", session.cookies.get_dict())

if resp.status_code in [301, 302, 303, 307, 308]:
    target = resp.headers.get('Location')
    print("Redirecting to Location:", target)
    res2 = session.get(target, allow_redirects=False)
    print("Redirect Page Status Code:", res2.status_code)
    print("Redirect Page Headers:", dict(res2.headers))
    print("Redirect Page Content (first 300 chars):\n", res2.text[:300])

