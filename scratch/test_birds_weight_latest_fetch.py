"""
Test fetching most recent birds weight data from sunfra_processed_data.
"""
import pymysql, sys, datetime, re
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT shead_name, quantity, notes, processed_time
    FROM sunfra_processed_data
    WHERE category = 'hen_weight'
    ORDER BY id DESC
""")
rows = cursor.fetchall()

latest_weights = {}
for r in rows:
    raw_sname = r['shead_name'] or ''
    # Normalize shed name e.g. "Shed 1" -> "Shead 1"
    s_match = re.search(r'([1-8])', raw_sname)
    if s_match:
        shed_key = f"Shead {s_match.group(1)}"
        if shed_key not in latest_weights:
            qty = float(r['quantity'] or 0)
            # If quantity is in kg (e.g. 1.52), convert to grams (1520g)
            weight_g = qty * 1000 if 0 < qty < 10 else qty
            latest_weights[shed_key] = {
                'weight_g': weight_g,
                'time': r['processed_time'],
                'notes': r['notes']
            }

print("=== LATEST PARSED BIRDS WEIGHT FOR ALL SHEDS ===")
for sname in [f"Shead {i}" for i in range(1, 9)]:
    w_info = latest_weights.get(sname)
    if w_info:
        print(f"  {sname}: {w_info['weight_g']:.2f}g (Date: {w_info['time']}) | Notes: {w_info['notes']}")
    else:
        print(f"  {sname}: No Recorded Weight Data")

conn.close()

