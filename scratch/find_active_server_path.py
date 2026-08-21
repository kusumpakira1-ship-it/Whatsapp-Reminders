"""
The CDN serves DYNAMIC status but returns old 197K file.
This means Hostinger hcdn is NOT caching the PHP - it's passing through to a backend that returns old content.

Root cause: The server at sunfragroup.com/kusum/Whatsapp_Rem/ is NOT pointing 
to /public_html/kusum/Whatsapp_Rem/. It may be pointing to a different path or 
there's a subdomain config issue.

Let's check ALL the index.php files on FTP and see which one the server is actually serving.
We'll do this by uploading a unique marker to each file and checking which one shows up via HTTP.
"""

import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

# Test all possible paths by uploading unique marker to each
test_files = [
    ('/public_html/kusum/Whatsapp_Rem/frontend', 'index.php'),
    ('/public_html/kusum/Whatsapp_Rem', 'index.php'),
    ('/public_html/frontend', 'index.php'),
    ('/public_html', 'index.php'),
    ('/public_html/kusum', 'index.php'),
    ('/public_html/Whatsapp_Rem', 'index.php'),
]

MARKER = f"UNIQUE_SERVER_MARKER_{int(time.time())}"
marker_php = f"<?php echo 'PATH_MARKER_{{PATH}}'; ?>".encode()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

for ftp_dir, fname in test_files:
    try:
        ftp.cwd(ftp_dir)
        test_content = f"<?php echo '{MARKER}_{ftp_dir.replace('/', '_')}'; ?>".encode()
        ftp.storbinary(f'STOR marker_test.php', io.BytesIO(test_content))
        print(f"Uploaded marker to {ftp_dir}/marker_test.php")
    except Exception as e:
        print(f"Error uploading to {ftp_dir}: {e}")

ftp.quit()

time.sleep(1)
# Now test the HTTP URLs to see which marker file serves content
urls_to_test = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/marker_test.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/marker_test.php',
    'https://sunfragroup.com/marker_test.php',
    'https://sunfragroup.com/kusum/marker_test.php',
    'https://sunfragroup.com/Whatsapp_Rem/marker_test.php',
]

print("\n--- Testing HTTP responses ---")
for url in urls_to_test:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read().decode('utf-8', errors='ignore')[:200]
            print(f"✅ {url}")
            print(f"   Content: {content}")
    except Exception as e:
        print(f"❌ {url}: {e}")
