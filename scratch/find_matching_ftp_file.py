"""
The HTTP response has 'fetchFlocks' (it's from after our Flocks feature), 
but missing 'confirmToggleSubReport' (added even later).

This is a DIFFERENT older version of index.php being served.
The HTTP version ends right before our new confirmToggleSubReport functions would appear.

Let me find EXACTLY where in our current file the confirmToggleSubReport appears vs where HTTP ends.
We need to find which older version this is and where it's stored.
"""
import urllib.request, sys, ftplib, io
sys.stdout.reconfigure(encoding='utf-8')

# Download via HTTP
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    http_content = resp.read().decode('utf-8', errors='ignore')

# Let's search for the exact end signature of the HTTP content 
end_sig = http_content[-200:].strip()
print("End of HTTP content (last 200 chars):")
print(repr(end_sig))

# Now look at ALL FTP index.php files and check which one matches
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp_files = [
    '/public_html/index.php',
    '/public_html/kusum/index.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/frontend/index.php',
    '/public_html/Whatsapp_Rem/index.php',
    '/public_html/public/index.php',
]

for fpath in ftp_files:
    try:
        ftp.cwd('/')
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {fpath}', buf.write)
        content = buf.getvalue().decode('utf-8', errors='ignore')
        has_toggle = 'confirmToggleSubReport' in content
        has_undone = 'Undone' in content
        matches_http = content.strip() == http_content.strip()
        size_match = len(content) == len(http_content)
        print(f"{fpath}:")
        print(f"  size={len(content)}, has_toggle={has_toggle}, has_undone={has_undone}, matches_http={matches_http}, size_match={size_match}")
    except Exception as e:
        print(f"{fpath}: ERROR - {e}")

ftp.quit()
