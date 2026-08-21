"""
Find real WhatsApp group JID for Sunfra Corporate P&L from sunfra_groups and recent chats.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("--- 1. SEARCHING sunfra_groups FOR CORPORATE P&L ---")
    groups = db.execute(text("SELECT id, name, whatsapp_group_id FROM sunfra_groups")).fetchall()
    for g in groups:
        print(f"  - Group ID {g[0]}: Name='{g[1]}' | JID='{g[2]}'")

    print("\n--- 2. REMINDER ID 295 DETAILS ---")
    rem = db.execute(text("SELECT id, person_name, person_phone, whatsapp_group_id, report_types FROM sunfra_unified_reminders WHERE id = 295")).fetchone()
    if rem:
        print(f"  - Rem 295: Name='{rem[1]}' | Phone='{rem[2]}' | GroupJID='{rem[3]}' | Reports='{rem[4]}'")

    print("\n--- 3. SEARCHING WAHA CHATS / GROUPS IN DB ---")
    chats = db.execute(text("SELECT DISTINCT group_id FROM sunfra_whatsapp_messages ORDER BY timestamp DESC LIMIT 30")).fetchall()
    for c in chats:
        print(f"  - WA Message Group JID: {c[0]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
