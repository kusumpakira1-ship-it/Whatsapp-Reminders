"""
Inject unique build tag into index.php and test URL response
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

# Read local file
with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'r', encoding='utf-8') as f:
    text = f.read()

unique_tag = f"BUILD_TAG_{int(time.time())}"
text = text.replace('<title>Reminders</title>', f'<title>Reminders - {unique_tag}</title>')

print(f"Injecting unique tag: {unique_tag}")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Storing in /public_html/kusum/Whatsapp_Rem/frontend/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR index.php', io.BytesIO(text.encode('utf-8')))

# Storing in /public_html/kusum/Whatsapp_Rem/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR index.php', io.BytesIO(text.encode('utf-8')))

ftp.quit()

time.sleep(1)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?cache_bust={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    found_tag = unique_tag in html
    print(f"URL: {url}")
    print(f"• Tag {unique_tag} found? {'YES ✅' if found_tag else 'NO ❌'}")
    if not found_tag:
        # Print title line from html
        for line in html.splitlines():
            if '<title>' in line:
                print("• Actual title in HTML:", line.strip())
