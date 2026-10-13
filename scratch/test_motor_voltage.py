import requests
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*'
}
r = requests.get('https://sunfra.com/farm/voltage_sensor/api.php?endpoint=voltage-logs', headers=headers, timeout=15)
data = r.json()
logs = data.get('logs', [])
print('Total logs:', len(logs))
latest_per_motor = {}
for log in logs:
    m_id = str(log.get('motorId', '')).strip()
    if m_id and m_id not in latest_per_motor:
        latest_per_motor[m_id] = log

for m_id, l in sorted(latest_per_motor.items()):
    status = str(l.get('status', '')).upper()
    volt = float(l.get('voltage', 0))
    is_off = 'OFF' in status or volt < 80.0
    ts_str = str(l.get('timestamp', '')).strip()
    # Format timestamp nicely
    try:
        dt = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
        formatted_ts = dt.strftime('%d %b %Y, %I:%M %p')
    except Exception:
        formatted_ts = ts_str
    print(f"Motor {m_id}: Loc={l.get('location')} | MAC={l.get('macAddress')} | Volt={volt:.1f}V | Stat={status} | Time={formatted_ts} | IS_OFF={is_off}")
