"""
Find exact corporate group JIDs in sunfra_groups and update reminder 295
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("--- GROUPS IN DATABASE ---")
    groups = db.execute(text("SELECT id, name, whatsapp_group_id FROM sunfra_groups WHERE name LIKE '%Corporate%' OR name LIKE '%P&L%' OR name LIKE '%Profit%' OR name LIKE '%Sunfra%'")).fetchall()
    for g in groups:
        print(f"  - ID: {g[0]} | Name: '{g[1]}' | JID: '{g[2]}'")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
