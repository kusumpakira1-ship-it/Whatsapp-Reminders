import sys
import sqlite3

sys.path.append('backend')
from database import SessionLocal
from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ TESTING MYSQL CONNECTION & GENERATING ACCURATE 16 SEP REPORT ================")

try:
    db = SessionLocal()
    # Query count of raw messages in MySQL for 16 Sep
    cnt = db.execute(text("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-16'")).fetchone()[0]
    print(f"Connected to MySQL! Found {cnt} raw messages for 16 Sep.")
    
    # Also fetch all 16 Sep raw messages and populate whatsapp_reminders.sqlite
    res = db.execute(text("SELECT id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path FROM sunfra_raw_messages WHERE date(timestamp) >= '2026-09-16'")).fetchall()
    db.close()
    
    sqlite_conn = sqlite3.connect("whatsapp_reminders.sqlite")
    cursor = sqlite_conn.cursor()
    
    # Ensure table exists in sqlite
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
    
    synced = 0
    for r in res:
        m_id, msg_id, sender, grp, ts, m_type, r_text, m_path = r
        cursor.execute("SELECT id FROM sunfra_raw_messages WHERE id = ?", (m_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO sunfra_raw_messages (id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (m_id, msg_id, sender, grp, str(ts), m_type, r_text, m_path))
            synced += 1
            
    sqlite_conn.commit()
    print(f"Synced {synced} raw messages into local SQLite database!")
    sqlite_conn.close()
    
    # Now evaluate attendance for 16 Sep
    data_16 = evaluate_attendance_for_date("2026-09-16")
    msg_16 = generate_attendance_summary_message(data_16)
    
    print("\n================ GENERATED ACCURATE 16 SEP ATTENDANCE REPORT ================")
    print(msg_16)

except Exception as e:
    print("MySQL Error:", e)
