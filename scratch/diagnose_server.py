import urllib.request, sys, time
sys.stdout.reconfigure(encoding='utf-8')

# Check what version the server is running by looking at the version string in the HTML
ts = int(time.time())
# Get the main page
req = urllib.request.Request(
    f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?_v={ts}',
    headers={'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'}
)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Find version string
import re
version_match = re.search(r'Version \d+\.\d+\.\d+\.BUILD\d+', html)
if version_match:
    print('Server version:', version_match.group(0))
else:
    print('Version string not found in HTML')
    
# Find guaranteed_groups keyword in HTML - it shouldn't be there (it's PHP not JS)
# but let's look for other markers
if 'guaranteed_groups' in html:
    print('guaranteed_groups found in HTML (unexpected)')
else:
    print('guaranteed_groups not in HTML output (expected - PHP not rendered)')
    
# Check file size in the response
print(f'HTML response size: {len(html)} chars')

# Check the groups API specifically
req2 = urllib.request.Request(
    f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=waha/groups&t={ts}',
    headers={'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'}
)
with urllib.request.urlopen(req2, timeout=15) as resp2:
    raw = resp2.read()
    
print(f'Groups API response size: {len(raw)} bytes')
print(f'Groups API response (first 200 chars): {raw.decode("utf-8","ignore")[:200]}')
