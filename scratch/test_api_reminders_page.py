"""
Add ?api=reminders_page handler to frontend/index.php, upload across all FTP locations, and test HTTP response!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

frontend_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
root_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'

with open(frontend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace API router check
old_router = "$route = $_GET['api'] ?? null;\nif ($route && !in_array($route, ['app', 'view', 'dashboard', 'live'])) {"
new_router = "$route = $_GET['api'] ?? null;\nif ($route && !in_array($route, ['app', 'view', 'dashboard', 'live', 'reminders_page', 'page'])) {"

if old_router in content:
    content = content.replace(old_router, new_router)
else:
    print("WARNING: Old router string not found, updating directly")

code = content.encode('utf-8')

with open(frontend_file, 'wb') as f:
    f.write(code)
with open(root_file, 'wb') as f:
    f.write(code)

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_paths = [
    '/',
    '/public',
    '/frontend',
    '/Whatsapp_Rem',
    '/Whatsapp_Rem/frontend',
    '/kusum',
    '/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend',
    '/cedad10937994543724efa30b6e53514',
    '/cedad10937994543724efa30b6e53514/public',
    '/cedad10937994543724efa30b6e53514/Whatsapp_Rem',
    '/public_html',
    '/public_html/public',
    '/public_html/frontend',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/Whatsapp_Rem'
]

for p in all_paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR index.php', io.BytesIO(code))
    except:
        pass

ftp.quit()
print("Uploaded updated ?api=reminders_page router to all directories! ✅")

time.sleep(1)

test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=reminders_page&t={int(time.time())}"
try:
    req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nLive HTTP Test {test_url}:")
        print(f"  Status: {resp.status}, Size: {len(html)} bytes")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print("Error:", e)

