"""
Inspect login form and test authentication to sunfra.com farm portal.
"""
import requests, sys, re
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

login_page_url = "https://sunfra.com/farm/sunfra/"
resp = session.get(login_page_url)
print("Login Page Status Code:", resp.status_code)
print("Login Page Form Inputs:")
inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
print(inputs)

# Attempt login with form credentials
post_data = {
    'username': 'kusum',
    'password': 'Kusum@2026Bb!',
    'login': '1',
    'submit': '1'
}

# Try POSTing to login_page_url
post_resp = session.post(login_page_url, data=post_data)
print("\nPOST Response Code:", post_resp.status_code)
print("POST Response URL:", post_resp.url)
print("POST Response Snippet (first 400 chars):\n", post_resp.text[:400])

# Test fetching endpoint now
test_url = "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14"
ep_resp = session.get(test_url)
print("\nEndpoint Response Status Code:", ep_resp.status_code)
print("Endpoint Content Snippet:\n", ep_resp.text[:400])

