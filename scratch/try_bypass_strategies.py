"""
The .htaccess RewriteRule is redirecting ALL .php file requests to index.php.
Even clear_all_cache.php is being served as index.php content (197K old version).

This means the RewriteRule in frontend/.htaccess is:
RewriteCond %{REQUEST_FILENAME} !-f  -- file exists, so should NOT redirect
RewriteCond %{REQUEST_FILENAME} !-d  -- not a directory
RewriteRule ^(.*)$ index.php [L]

BUT the files DO exist (we can see them in FTP listing).
The issue might be that the REQUEST_FILENAME check uses the PHYSICAL path on disk,
and Hostinger's setup might map /public_html/kusum/Whatsapp_Rem/frontend/ 
to a different physical path.

MORE LIKELY: The parent .htaccess at /public_html/.htaccess is catching the request FIRST
with a rule that has NO conditions (just RewriteRule ^(.*)$ index.php [L])
and it's executing /public_html/index.php, not the subdirectory's index.php.

Wait, I re-read the /public_html/.htaccess:
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

This DOES have conditions. So the file HAS to physically not exist at the request path.

This means the server's document root might NOT be /public_html.
The URL https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php
might be mapping to /public_html/kusum/Whatsapp_Rem/frontend/index.php...

OR the domain sunfragroup.com may be mapping to /public_html/kusum/Whatsapp_Rem/frontend/
as its document root! Let me check by looking at what the "root" request returns.

If the document root IS /public_html/kusum/Whatsapp_Rem/frontend/:
- /kusum/Whatsapp_Rem/frontend/ in URL path would NOT exist
- So .htaccess would redirect to index.php which IS the correct file
- BUT then the HTTP content should be our new 239K file...

Unless OPcache is actually caching the OUTPUT of running index.php.
Let me try accessing index.php directly by bypassing the URL path.
"""

import urllib.request, sys, time, ftplib, io
sys.stdout.reconfigure(encoding='utf-8')

# Try accessing with different Accept headers to bypass any CDN content-type caching
for headers in [
    {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html'},
    {'User-Agent': 'curl/7.68.0', 'Accept': '*/*'},
    {'User-Agent': 'Wget/1.21.3', 'Accept': '*/*', 'Cache-Control': 'no-cache, max-age=0'},
]:
    url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?nocache={int(time.time())}'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            has_toggle = 'confirmToggleSubReport' in html
            hcdn = resp.headers.get('x-hcdn-cache-status', 'N/A')
            print(f"UA={headers['User-Agent'][:20]}: size={len(html)}, toggle={has_toggle}, hcdn={hcdn}")
    except Exception as e:
        print(f"Error: {e}")

# Now let me try with If-None-Match to force a different response
print("\n--- Trying with explicit no-store headers ---")
req = urllib.request.Request(
    f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    headers={
        'User-Agent': 'Mozilla/5.0',
        'Cache-Control': 'no-store, no-cache',
        'Pragma': 'no-cache',
        'If-Modified-Since': 'Thu, 01 Jan 1970 00:00:00 GMT'
    }
)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print(f"Size: {len(html)}, toggle: {'confirmToggleSubReport' in html}")
