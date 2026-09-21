import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ ATTENDANCE SUMMARY MESSAGES SENT TO KUSUM ON 16 SEP 2026 ================")

query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-16 00:00:00' AND timestamp <= '2026-09-16 23:59:59'
      AND (raw_text LIKE '%Daily Attendance Report%' OR raw_text LIKE '%OVERALL STATS%' OR raw_text LIKE '%Total Employees%')
    ORDER BY timestamp ASC
""")

try:
    res = db.execute(query).fetchall()
    print(f"Total attendance summary messages found on 16 Sep: {len(res)}\n")
    for r in res:
        clean = (r[3] or '').replace('\n', ' | ')
        print(f"[{r[4]}] ID: {r[0]} | Group: [{r[1]}] | Sender: {r[2]}")
        print(f"    Text: {clean[:200]}...\n" + "-"*60)
except Exception as e:
    print("Error querying messages:", e)

db.close()
