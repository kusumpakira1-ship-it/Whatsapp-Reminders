"""
Daily Farm Summary Report generator & dispatcher for 9:30 PM IST job.
Pulling mortality, production, birds weight from sunfra.com supervisor endpoints and sunfra_book_standards DB table.
"""
import pymysql, sys, datetime, logging, json, urllib.request, urllib.parse, http.cookiejar

logger = logging.getLogger(__name__)

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

def fetch_supervisor_endpoint(endpoint_url):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Login session
    try:
        login_url = "https://sunfra.com/farm/sunfra/"
        post_data = urllib.parse.urlencode({'username': 'kusum', 'password': 'Kusum@2026Bb!', 'remember_me': '1'}).encode('utf-8')
        req = urllib.request.Request(login_url, data=post_data, headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded'})
        opener.open(req, timeout=10)
    except Exception as e:
        logger.warning(f"Login notice in fetch_supervisor_endpoint: {e}")

    try:
        req2 = urllib.request.Request(endpoint_url, headers=headers)
        with opener.open(req2, timeout=10) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
            return json.loads(raw)
    except Exception as e:
        logger.error(f"Error fetching {endpoint_url}: {e}")
        return None

def generate_daily_farm_summary_report(target_date=None):
    if target_date is None:
        target_date = datetime.date.today() - datetime.timedelta(days=1)
        
    date_str = target_date.strftime("%d/%m/%Y")

    conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    # Query active flocks
    cursor.execute("SELECT * FROM sunfra_flocks WHERE status = 'active'")
    flocks = {f['shed_name']: f for f in cursor.fetchall()}

    # Fetch live supervisor data from web endpoints first
    mort_data_raw = fetch_supervisor_endpoint(f"https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date={target_date.strftime('%Y-%m-%d')}")
    prod_data_raw = fetch_supervisor_endpoint(f"https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php?date={target_date.strftime('%Y-%m-%d')}")
    weight_data_raw = fetch_supervisor_endpoint(f"https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php?date={target_date.strftime('%Y-%m-%d')}")

    mortality_data = {}
    production_data = {}
    weight_data = {}

    # Parse live web data if available
    if mort_data_raw and isinstance(mort_data_raw, list):
        for item in mort_data_raw:
            sname = item.get('shed_name') or item.get('shead_name')
            if sname:
                mortality_data[sname] = int(item.get('mortality') or 0)
    
    if prod_data_raw and isinstance(prod_data_raw, list):
        for item in prod_data_raw:
            sname = item.get('shed_name') or item.get('shead_name')
            if sname:
                trays = int(item.get('trays') or 0)
                loose = int(item.get('loose') or 0)
                tot = int(item.get('total_eggs') or ((trays * 30) + loose))
                production_data[sname] = {'trays': trays, 'loose': loose, 'total_eggs': tot}

    if weight_data_raw and isinstance(weight_data_raw, list):
        for item in weight_data_raw:
            sname = item.get('shed_name') or item.get('shead_name')
            if sname and (item.get('average_weight') or item.get('weight')):
                weight_data[sname] = float(item.get('average_weight') or item.get('weight'))

    # Fallback to parsing live WhatsApp supervisor messages from DB for target_date if web data is missing
    if not mortality_data or not production_data:
        start_dt = datetime.datetime.combine(target_date, datetime.time.min)
        end_dt = datetime.datetime.combine(target_date, datetime.time.max)
        import re
        cursor.execute("""
            SELECT raw_text, timestamp FROM sunfra_raw_messages
            WHERE (group_name LIKE '%%120363407511560539%%' OR LOWER(group_name) LIKE '%%production%%' OR LOWER(group_name) LIKE '%%gowdown%%' OR LOWER(group_name) LIKE '%%supervisors%%')
              AND timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp ASC
        """, (start_dt, end_dt))
        wa_msgs = cursor.fetchall()

        for m in wa_msgs:
            text = m['raw_text'] or ''
            
            # Parse Mortality e.g. "1-5", "2-9", "Chick-"
            if 'mortality' in text.lower():
                lines = text.split('\n')
                for line in lines:
                    m_match = re.match(r'^\s*([1-8])\s*[-:_]\s*(\d+)', line)
                    if m_match:
                        snum = m_match.group(1)
                        mortality_data[f"Shead {snum}"] = int(m_match.group(2))
                    ch_match = re.match(r'^\s*chick\s*[-:_]\s*(\d+)', line, re.IGNORECASE)
                    if ch_match:
                        mortality_data['Chick 1'] = int(ch_match.group(1))

            # Parse Production e.g. "1._ 55_ 596.20_93%-93%" or "6_73_594.3_89%_87%"
            if 'production' in text.lower() or 'sed_age_production' in text.lower():
                lines = text.split('\n')
                for line in lines:
                    p_match = re.search(r'^\s*([1-8])[\._\s]*(\d+)[\._\s]+(\d+)(?:\.(\d+))?', line)
                    if p_match:
                        snum = p_match.group(1)
                        trays = int(p_match.group(3))
                        loose = int(p_match.group(4)) if p_match.group(4) else 0
                        tot = (trays * 30) + loose
                        production_data[f"Shead {snum}"] = {'trays': trays, 'loose': loose, 'total_eggs': tot}

    # Fetch most recent hen weight data from DB if weight_data is empty
    if not weight_data:
        cursor.execute("""
            SELECT shead_name, quantity, notes, processed_time
            FROM sunfra_processed_data
            WHERE category = 'hen_weight'
            ORDER BY id DESC
        """)
        w_rows = cursor.fetchall()
        for r in w_rows:
            raw_sname = r['shead_name'] or ''
            s_match = re.search(r'([1-8])', raw_sname)
            if s_match:
                shed_key = f"Shead {s_match.group(1)}"
                if shed_key not in weight_data:
                    qty = float(r['quantity'] or 0)
                    weight_g = qty * 1000 if 0 < qty < 10 else qty
                    if weight_g > 0:
                        weight_data[shed_key] = weight_g

    mortality_rows = []
    production_rows = []
    weight_rows = []

    for s_num in range(1, 9):
        sname = f"Shead {s_num}"
        fl = flocks.get(sname, {})
        hatch = fl.get('hatch_date')
        live_birds = fl.get('live_birds', 0)
        
        if hatch:
            age_days = (target_date - hatch).days
            age_weeks = max(1, age_days // 7)
        else:
            age_weeks = fl.get('running_weeks', 1)

        cursor.execute("SELECT AVG(expected_production_pct) as bp, AVG(expected_body_weight_g) as bw FROM sunfra_book_standards WHERE week = %s", (age_weeks,))
        b_std = cursor.fetchone() or {}
        book_pct = round(float(b_std.get('bp') or 0))
        book_weight = round(float(b_std.get('bw') or 0))

        # Mortality
        m_val = mortality_data.get(sname, 0)
        mortality_rows.append(f"{sname}: {m_val}")

        # Production
        p_info = production_data.get(sname, {'trays': 0, 'loose': 0, 'total_eggs': 0})
        trays = p_info['trays']
        loose = p_info['loose']
        total_eggs = p_info['total_eggs']
        
        if total_eggs > 0 and live_birds > 0:
            actual_pct_raw = round((total_eggs / live_birds * 100))
            actual_pct_str = "96+%" if actual_pct_raw > 96 else f"{actual_pct_raw}%"
            prod_icon = "🟢" if actual_pct_raw >= book_pct else "🔴"
            trays_fmt = f"{trays}.{loose:02d}"
            production_rows.append(f"{sname}: {age_weeks}w | {trays_fmt} Trays | {actual_pct_str} (Book: {book_pct}%) {prod_icon}")
        else:
            production_rows.append(f"{sname}: {age_weeks}w | No Production Data")

        # Weight
        act_weight = weight_data.get(sname)
        if act_weight:
            diff_weight = round(act_weight - book_weight)
            weight_icon = "🟢" if act_weight >= book_weight else "🔴"
            diff_str = f"+{diff_weight}g" if diff_weight > 0 else f"{diff_weight}g"
            weight_rows.append(f"{sname}: {act_weight:.2f}g (Book: {book_weight}g | {diff_str}) {weight_icon}")
        else:
            weight_rows.append(f"{sname}: {age_weeks}w | No Weight Data (Book: {book_weight}g)")

    mortality_rows.append(f"Chick 1: {mortality_data.get('Chick 1', 0)}")

    total_mort = sum(mortality_data.values())

    report = f"""📋 *DAILY FARM SUMMARY ({date_str})*

💀 *Shed-Wise Mortality*
```
""" + "\n".join(mortality_rows) + f"""
Total mortality: {sum(mortality_data.values())}
```

🥚 *Shed-Wise Production (Actual vs Book Standard)*
```
""" + "\n".join(production_rows) + """
```

⚖️ *Birds Weight Comparison (Actual vs Book Standard)*
```
""" + "\n".join(weight_rows) + """
```"""

    return report

def send_daily_farm_summary_930pm_job():
    logger.info("Executing 9:30 PM Daily Farm Summary Report job...")
    report_text = generate_daily_farm_summary_report()
    
    # Import WAHA message sender
    try:
        from scheduler import send_waha_message
        recipients = ["917259510983@c.us", "917975209680@c.us", "916364817749@c.us"]
        for recipient in recipients:
            send_waha_message(recipient, report_text)
            logger.info(f"Sent Daily Farm Summary report to {recipient}")
    except Exception as e:
        logger.error(f"Error dispatching WAHA text for Daily Farm Summary: {e}")

