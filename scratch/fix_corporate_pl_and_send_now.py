"""
1. Update reminder 295 and dummy JIDs in sunfra_unified_reminders to real WhatsApp group JIDs:
   - 'group_sunfra_corporate_p&l' -> '120363425581380088@g.us'
   - 'group_sunfra_p&l' -> '120363427856964756@g.us'
   - 'group_sunfra_hyperscale' -> '120363428417403024@g.us'

2. Instantly send the 6:00 PM Corporate P&L reminder to the real WhatsApp group right now!
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from database import SessionLocal
from sqlalchemy import text
from waha_service import send_waha_message

db = SessionLocal()
try:
    print("--- 1. UPDATING DUMMY GROUP JIDs IN DATABASE ---")
    db.execute(text("UPDATE sunfra_unified_reminders SET whatsapp_group_id = '120363425581380088@g.us' WHERE whatsapp_group_id = 'group_sunfra_corporate_p&l' OR id = 295"))
    db.execute(text("UPDATE sunfra_unified_reminders SET whatsapp_group_id = '120363427856964756@g.us' WHERE whatsapp_group_id = 'group_sunfra_p&l'"))
    db.execute(text("UPDATE sunfra_unified_reminders SET whatsapp_group_id = '120363428417403024@g.us' WHERE whatsapp_group_id = 'group_sunfra_hyperscale'"))
    db.commit()
    print("  ✅ Updated DB dummy group JIDs to real WhatsApp JIDs!")

    print("\n--- 2. SENDING 6:00 PM REMINDER TO SUNFRA CORPORATE P&L NOW ---")
    target_jid = '120363425581380088@g.us'
    message = """Please submit the following pending reports for today:
• *Day Book*
• *Daily Sales*
• *Daily Purchases*
• *Total Payables*
• *Total Receivables*
• *Each Sales P&L*"""

    success = send_waha_message(target_jid, message)
    if success:
        print(f"  ✅ SUCCESS: Message sent to Sunfra Corporate P&L group ({target_jid})!")
    else:
        print(f"  ❌ FAILED: Could not send message via WAHA.")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
