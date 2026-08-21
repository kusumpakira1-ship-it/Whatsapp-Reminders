"""
Test index.php response with ?v=123 param (bypassing lines 3-6 302 redirect)
"""
import sys, requests
sys.stdout.reconfigure(encoding='utf-8')

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v=123"
r = requests.get(url, allow_redirects=False)

print(f"URL: {url}")
print(f"Status Code: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Content Length: {len(r.text)} bytes")
print(f"First 200 chars:\n{r.text[:200]}")
