"""
Inspect exact function names present in the live server response
"""

import urllib.request, sys, re
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print("Total HTML length:", len(html))

# Find all JS function declarations in HTML
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)', html)
print("\nFunctions found in live HTML:")
for f in sorted(set(funcs)):
    print(" -", f)

# Find all async functions
async_funcs = re.findall(r'async\s+function\s+([a-zA-Z0-9_]+)', html)
print("\nAsync functions found in live HTML:")
for af in sorted(set(async_funcs)):
    print(" -", af)
