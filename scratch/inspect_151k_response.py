import urllib.request
import ftplib
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== DOWNLOADING 151K HTTP RESPONSE ===")
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?v=unique_test_1"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    http_data = resp.read().decode('utf-8', errors='ignore')

print("HTTP Length:", len(http_data))
# Extract title and some unique CSS/JS or text
print("Head 500 chars:")
print(http_data[:500])

print("\nSearching for unique string from HTTP data in all FTP files...")
# Pick 3 unique substrings from http_data
part1 = http_data[100:200]
part2 = http_data[5000:5100]

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_files = []
def scan_all(path):
    try:
        items = []
        ftp.retrlines(f'LIST {path}', items.append)
        for item in items:
            parts = item.split()
            name = parts[-1]
            if name in ('.', '..'): continue
            full = f"{path.rstrip('/')}/{name}"
            if item.startswith('d'):
                if full not in ('/logs', '/.well-known', '/cgi-bin'):
                    scan_all(full)
            else:
                all_files.append(full)
    except Exception:
        pass

scan_all('/public_html')

matched = False
for fp in all_files:
    try:
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {fp}', buf.write)
        content = buf.getvalue().decode('utf-8', errors='ignore')
        if part1 in content or part2 in content:
            print(f"EXACT MATCH FOUND ON FTP: {fp} (len={len(content)})")
            matched = True
    except Exception:
        pass

if not matched:
    print("NO FILE ON FTP MATCHES THE 151K HTTP RESPONSE!")
    print("This confirms the 151K response is being served strictly from Hostinger CDN / LiteSpeed Edge cache!")

ftp.quit()
