"""
The root /public_html/.htaccess redirects ALL requests to /public_html/index.php.
But /public_html/index.php DOES have confirmToggleSubReport (232K).
The live HTTP response returns 197K without it - so something is still wrong.

Let me check: what does the HTTP response look like when we fetch a specific URL 
that can ONLY come from /public_html/index.php vs /public_html/kusum/Whatsapp_Rem/frontend/index.php?

Also let me check the frontend/index.php we're seeing from HTTP more carefully.
It's 197K but the FTP file is 239K - this is a 42K difference.
Let me download the HTTP response content and check what's in it vs what's missing.
"""
import urllib.request, sys, io, ftplib
sys.stdout.reconfigure(encoding='utf-8')

# Download via HTTP
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    http_content = resp.read().decode('utf-8', errors='ignore')

print(f"HTTP content size: {len(http_content)} chars")
print(f"HTTP has 'confirmToggleSubReport': {'YES' if 'confirmToggleSubReport' in http_content else 'NO'}")
print(f"HTTP has 'Undone': {'YES' if 'Undone' in http_content else 'NO'}")
print(f"HTTP has 'fetchFlocks': {'YES' if 'fetchFlocks' in http_content else 'NO'}")
print(f"HTTP has 'Flock': {'YES' if 'Flock' in http_content else 'NO'}")

# Get the last 500 chars of HTTP content to see if it's truncated
print(f"\nLast 500 chars of HTTP response:")
print(http_content[-500:])
