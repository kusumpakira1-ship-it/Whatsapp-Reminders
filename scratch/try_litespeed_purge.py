"""
LiteSpeed full page cache - try HTTP PURGE method and various purge approaches
"""
import urllib.request, urllib.parse, sys, time
import http.client, ssl
sys.stdout.reconfigure(encoding='utf-8')

# Method 1: HTTP PURGE method
print("=== Method 1: HTTP PURGE Request ===")
try:
    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection("sunfragroup.com", context=context, timeout=10)
    conn.request("PURGE", "/kusum/Whatsapp_Rem/frontend/index.php", headers={
        'Host': 'sunfragroup.com',
        'User-Agent': 'Mozilla/5.0',
    })
    resp = conn.getresponse()
    body = resp.read().decode('utf-8', errors='ignore')
    print(f"  PURGE response: {resp.status} {resp.reason}")
    print(f"  Body: {body[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# Method 2: Try purging via special LiteSpeed URL pattern
print("\n=== Method 2: LiteSpeed Admin Purge URL ===")
for purge_url in [
    'https://sunfragroup.com/__LSCACHE/PURGE',
    'https://sunfragroup.com/lscache_clear.php',
]:
    req = urllib.request.Request(purge_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            print(f"  {purge_url}: {resp.status}, size={len(body)}")
    except urllib.error.HTTPError as e:
        print(f"  {purge_url}: HTTP {e.code}")
    except Exception as e:
        print(f"  {purge_url}: {e}")

# Method 3: Try Hostinger API for cache clearing
print("\n=== Method 3: Hostinger API ===")
for api_url in [
    'https://api.hostinger.com/v1/cache/purge',
    'https://api.hostinger.com/cache/clear',
]:
    req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            print(f"  {api_url}: {resp.status}, body={body[:100]}")
    except urllib.error.HTTPError as e:
        print(f"  {api_url}: HTTP {e.code} {e.reason}")
        try:
            print(f"  Response: {e.read().decode('utf-8')[:100]}")
        except:
            pass
    except Exception as e:
        print(f"  {api_url}: {e}")

# Method 4: POST with X-LiteSpeed-Purge header
print("\n=== Method 4: X-LiteSpeed-Purge POST ===")
req = urllib.request.Request(
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    data=b'ls_cache_purge=*',
    headers={
        'User-Agent': 'Mozilla/5.0',
        'X-LiteSpeed-Purge': '*',
        'X-LiteSpeed-Cache-Control': 'no-cache',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        has_toggle = 'confirmToggleSubReport' in body
        print(f"  Size: {len(body)}, toggle={has_toggle}")
except Exception as e:
    print(f"  Error: {e}")
