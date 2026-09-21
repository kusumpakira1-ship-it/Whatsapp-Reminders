import sys
import sqlite3
import time

sys.path.append('backend')
from database import SessionLocal
from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ COPYING ALL RAW MESSAGES FROM MYSQL TO LOCAL SQLITE ================")

connected = False
for attempt in range(5):
    try:
        mysql_db = SessionLocal()
        rows = mysql_db.execute(text("SELECT id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path FROM sunfra_raw_messages WHERE timestamp >= '2026-09-01 00:00:00'")).fetchall()
        print(f"Connected to MySQL! Retreived {len(rows)} messages from Sept 1 onwards.")
        mysql_db.close()
        connected = True
        break
    except Exception as e:
        print(f"Attempt {attempt+1} - MySQL Error: {e}")
        time.sleep(2)

if connected:
    sqlite_conn = sqlite3.connect("whatsapp_reminders.sqlite")
    cursor = sqlite_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sunfra_raw_messages (
            id INTEGER PRIMARY KEY,
            message_id VARCHAR(255),
            sender VARCHAR(100),
            group_name VARCHAR(255),
            timestamp DATETIME,
            message_type VARCHAR(50),
            raw_text TEXT,
            media_path VARCHAR(500)
        );
    """)
    
    count = 0
    for r in rows:
        m_id, msg_id, sender, grp, ts, m_type, r_text, m_path = r
        cursor.execute("SELECT id FROM sunfra_raw_messages WHERE id = ?", (m_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO sunfra_raw_messages (id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (m_id, msg_id, sender, grp, str(ts), m_type, r_text, m_path))
            count += 1
            
    sqlite_conn.commit()
    print(f"Successfully copied {count} messages into local whatsapp_reminders.sqlite database!")
    sqlite_conn.close()

# Evaluate 16 Sep attendance
data_16 = evaluate_attendance_for_date("2026-09-16")
msg_16 = generate_attendance_summary_message(data_16)
print("\n================ EVALUATED 16 SEP ATTENDANCE REPORT ================")
print(msg_16)
