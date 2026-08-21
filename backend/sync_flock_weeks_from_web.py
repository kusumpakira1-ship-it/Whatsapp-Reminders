"""
Daily Flock Weeks Auto-Sync script from batch_json_to_web.php to MySQL sunfra_flocks.
"""
import urllib.request, urllib.parse, http.cookiejar, json, sys, datetime
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

def sync_flocks_from_web():
    print(f"[{datetime.datetime.now()}] Starting flock weeks sync from web endpoint...")
    
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    # 1. Login to web app
    login_url = "https://sunfra.com/farm/sunfra/"
    post_data = urllib.parse.urlencode({
        'username': 'kusum',
        'password': 'Kusum@2026Bb!',
        'remember_me': '1'
    }).encode('utf-8')

    login_headers = headers.copy()
    login_headers['Content-Type'] = 'application/x-www-form-urlencoded'

    try:
        req = urllib.request.Request(login_url, data=post_data, headers=login_headers)
        opener.open(req, timeout=10)
    except Exception as e:
        print("Login attempt notice:", e)

    # 2. Fetch batch JSON endpoint
    batch_url = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
    flock_data = []
    
    try:
        req2 = urllib.request.Request(batch_url, headers=headers)
        with opener.open(req2, timeout=10) as resp2:
            raw = resp2.read().decode('utf-8', errors='ignore')
            if len(raw) > 10:
                try:
                    data = json.loads(raw)
                    if isinstance(data, list):
                        flock_data = data
                    elif isinstance(data, dict) and 'data' in data:
                        flock_data = data['data']
                except Exception as je:
                    print("JSON parse error:", je)
    except Exception as e:
        print("Error fetching batch endpoint:", e)

    # 3. Update MySQL DB sunfra_flocks
    conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    if flock_data:
        print(f"Successfully fetched {len(flock_data)} flock items from web endpoint:")
        for item in flock_data:
            shed_name = item.get('shed_name') or item.get('shed') or item.get('name')
            weeks = item.get('running_weeks') or item.get('weeks') or item.get('age_weeks')
            days = item.get('running_days') or item.get('days') or item.get('age_days')
            live_birds = item.get('live_birds') or item.get('birds')
            
            if shed_name and weeks is not None:
                cursor.execute("""
                    UPDATE sunfra_flocks 
                    SET running_weeks = %s, 
                        running_days = COALESCE(%s, running_days),
                        live_birds = COALESCE(%s, live_birds),
                        updated_at = NOW()
                    WHERE LOWER(shed_name) = LOWER(%s)
                """, (weeks, days, live_birds, shed_name))
                print(f"  -> Updated DB for '{shed_name}': {weeks} weeks, {days} days, {live_birds} live birds")
        conn.commit()
    else:
        print("Web endpoint check complete. Calculating exact weeks from hatch_date in DB...")
        # Auto-update running_weeks from hatch_date in DB if web endpoint is static
        today = datetime.date.today()
        cursor.execute("SELECT id, shed_name, hatch_date FROM sunfra_flocks WHERE hatch_date IS NOT NULL")
        rows = cursor.fetchall()
        for r in rows:
            hatch = r['hatch_date']
            age_days = (today - hatch).days
            age_weeks = age_days // 7
            cursor.execute("""
                UPDATE sunfra_flocks 
                SET running_days = %s, running_weeks = %s, updated_at = NOW() 
                WHERE id = %s
            """, (age_days, age_weeks, r['id']))
            print(f"  -> Synced '{r['shed_name']}': {age_weeks} weeks ({age_days} days)")
        conn.commit()

    conn.close()

if __name__ == '__main__':
    sync_flocks_from_web()

