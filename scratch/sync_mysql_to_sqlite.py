import sys
import sqlite3

sys.path.append('backend')
from database import SessionLocal
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ TRYING MYSQL CONNECT & SYNC TO SQLITE ================")
try:
    mysql_db = SessionLocal()
    res = mysql_db.execute(text("SELECT id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path FROM sunfra_raw_messages WHERE timestamp >= '2026-09-16 00:00:00';")).fetchall()
    print(f"Successfully connected to MySQL! Found {len(res)} messages from 16 Sep onwards.")
    
    sqlite_conn = sqlite3.connect("whatsapp_reminders.sqlite")
    cursor = sqlite_conn.cursor()
    
    inserted = 0
    for r in res:
        m_id, msg_id, sender, grp, ts, m_type, r_text, m_path = r
        cursor.execute("SELECT id FROM sunfra_raw_messages WHERE id = ?", (m_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO sunfra_raw_messages (id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (m_id, msg_id, sender, grp, str(ts), m_type, r_text, m_path))
            inserted += 1
            
    sqlite_conn.commit()
    print(f"Synced {inserted} new raw messages into whatsapp_reminders.sqlite!")
    sqlite_conn.close()
    mysql_db.close()
except Exception as e:
    print("MySQL Error:", e)
