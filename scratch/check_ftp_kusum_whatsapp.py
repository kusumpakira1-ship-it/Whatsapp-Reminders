"""
The FTP root's kusum/ has index.php (304K) and Whatsapp_Rem/ subdir.
The website might be served from ~/kusum/Whatsapp_Rem/frontend/ (NOT ~/public_html/kusum/...)!

Let's check ~/kusum/Whatsapp_Rem/ and specifically ~/kusum/Whatsapp_Rem/frontend/
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Walk FTP root's kusum/Whatsapp_Rem/ structure
for path in ['/kusum/Whatsapp_Rem', '/kusum/Whatsapp_Rem/frontend']:
    print(f"\n=== {path}/ ===")
    try:
        ftp.cwd(path)
        entries = []
        ftp.retrlines('LIST', entries.append)
        for e in entries:
            print(e)
    except Exception as e:
        print(f"Error: {e}")

# Read index.php from ~/kusum/Whatsapp_Rem/frontend/ if it exists
print("\n=== ~/kusum/Whatsapp_Rem/frontend/index.php ===")
try:
    ftp.cwd('/kusum/Whatsapp_Rem/frontend')
    buf = io.BytesIO()
    ftp.retrbinary('RETR index.php', buf.write)
    content = buf.getvalue().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in content
    print(f"Size: {len(content)} bytes")
    print(f"Has confirmToggleSubReport: {has_toggle}")
    # Check if this matches the HTTP response size
    print(f"Matches 197149 HTTP response: {len(content) == 197149}")
    # Show end of file
    print(f"Last 200 chars: {content[-200:]}")
except Exception as e:
    print(f"Error: {e}")

ftp.quit()
