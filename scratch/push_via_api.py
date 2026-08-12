import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

# Read the local index.php
with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php', 'rb') as f:
    code = f.read()

print(f'Local file size: {len(code)} bytes')

# Try all known working endpoint paths
endpoints = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php',
]

for base_url in endpoints:
    url = base_url + '?api=update_code'
    req = urllib.request.Request(
        url,
        data=code,
        method='POST',
        headers={
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(code)),
            'Cache-Control': 'no-cache'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = resp.read().decode('utf-8', errors='ignore')
            print(f'{url} => {result[:200]}')
            break
    except Exception as e:
        print(f'{url} => ERROR: {e}')
