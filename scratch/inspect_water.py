import sys, os, pymysql, requests, re
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from water_monitoring import DB_CONFIG, IST
from water_flow_farm_monitoring import WATER_FLOW_FARM_URL, REQUEST_HEADERS

print("=== 1. Live Database Devices (Water Level & Telemetry) ===")
try:
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    query = """
        SELECT r1.*
        FROM device_readings r1
        INNER JOIN (
            SELECT mac_address, MAX(id) AS max_id
            FROM device_readings
            WHERE mac_address IN ('C4-4F-33-24-7C-59', '40-91-51-C8-0C-C8')
            GROUP BY mac_address
        ) r2 ON r1.id = r2.max_id
    """
    cur.execute(query)
    devs = cur.fetchall()
    conn.close()
    for d in devs:
        print(f"  MAC: {d.get('mac_address')} | Location: {d.get('location')} | Level: {d.get('water_level')}% | Status: {d.get('status')} | Last TS: {d.get('timestamp')}")
except Exception as e:
    print("  DB Error:", e)

print("\n=== 2. Live Webpage Telemetry (Water Flow Farm) ===")
try:
    resp = requests.get(WATER_FLOW_FARM_URL, headers=REQUEST_HEADERS, timeout=20)
    html = resp.text
    ind_match = re.search(r'Indicator\s*Last\s*Reading.*?class="v"[^>]*>([\d\-:\s]+)<.*?MAC:\s*([A-F0-9\-]{17})', html, re.S | re.I)
    if ind_match:
        print(f"  Indicator Device -> MAC: {ind_match.group(2)} | Last Reading: {ind_match.group(1).strip()}")
    else:
        print("  No Indicator Device match found in HTML.")

    rows = re.findall(r'<tr>\s*<td>.*?badge.*?>([\d\-:\s]+)<.*?<td>([A-F0-9\-]{17})</td>', html, re.S | re.I)
    print(f"  Found {len(rows)} Water Flow Devices in webpage table:")
    for ts_str, mac_str in rows:
        print(f"    Flow Device MAC: {mac_str} | Last Reading: {ts_str}")
except Exception as e:
    print("  Webpage Error:", e)
