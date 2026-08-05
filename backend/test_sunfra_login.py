import requests
import re

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

resp_get = session.get(url_login)
print("Login Page Status Code:", resp_get.status_code)
html = resp_get.text

# Find form action
action_match = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', html, re.IGNORECASE)
action_url = url_login
if action_match:
    act = action_match.group(1)
    if act.startswith('http'):
        action_url = act
    elif act.startswith('/'):
        action_url = "https://sunfra.com" + act
    else:
        action_url = "https://sunfra.com/farm/sunfra/login/" + act

print("Form Action URL:", action_url)

# Find input fields
inputs = re.findall(r'<input[^>]+>', html, re.IGNORECASE)
post_data = {}
for inp in inputs:
    name_m = re.search(r'name=["\']([^"\']+)["\']', inp, re.IGNORECASE)
    val_m = re.search(r'value=["\']([^"\']+)["\']', inp, re.IGNORECASE)
    type_m = re.search(r'type=["\']([^"\']+)["\']', inp, re.IGNORECASE)
    
    if not name_m:
        continue
    name = name_m.group(1)
    val = val_m.group(1) if val_m else ""
    t = type_m.group(1).lower() if type_m else "text"
    
    name_lower = name.lower()
    if 'user' in name_lower or 'email' in name_lower or 'id' in name_lower or 'log' in name_lower:
        post_data[name] = 'sunfra'
    elif 'pass' in name_lower or 'pwd' in name_lower:
        post_data[name] = 'Sunfra#321'
    else:
        post_data[name] = val

print("Constructed POST Data Payload:", post_data)
print("\n--- FULL FORM HTML ---")
print(html[:2000])

# Perform Login POST
resp_post = session.post(action_url, data=post_data, allow_redirects=True)
print("\nPost Response Final URL:", resp_post.url)
print("Post Response Code:", resp_post.status_code)
print("Post Response Snippet:\n", resp_post.text[:1500])

# Inspect navigation links on logged-in page
links = re.findall(r'href=["\']([^"\']+)["\']', resp_post.text, re.IGNORECASE)
print(f"\nFound {len(links)} links on the logged-in page:")
for l in links[:30]:
    print("  • Link:", l)
