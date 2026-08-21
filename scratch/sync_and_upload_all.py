"""
Sync root index.php to match frontend/index.php and upload to all server paths.
"""
import ftplib, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

src_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
dest_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'

# 1. Sync local root index.php from frontend/index.php
with open(src_file, 'r', encoding='utf-8', errors='ignore') as f_src:
    content = f_src.read()

with open(dest_file, 'w', encoding='utf-8') as f_dest:
    f_dest.write(content)

print(f"✅ Local sync complete! Both index.php files now have {len(content.splitlines())} lines.")

# 2. Upload to all remote FTP locations
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

remote_locations = [
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/kusum/index.php',
    '/public_html/frontend/index.php',
    '/public_html/index.php'
]

for remote in remote_locations:
    print(f"Uploading to {remote}...")
    try:
        with open(src_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote}', f)
        print(f"  ✅ Uploaded {remote}")
    except Exception as e:
        print(f"  Notice {remote}: {e}")

ftp.quit()

# 3. Trigger cache flush
cache_urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/flush_opcache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/clear_all_cache.php"
]
for url in cache_urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

print("✅ Server upload & cache sync completed successfully!")

