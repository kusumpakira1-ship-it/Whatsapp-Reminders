import sys
sys.path.append('/app')
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE sunfra_unified_reminders SET status = 'sent' WHERE id = 233 OR id = 189 OR whatsapp_group_id LIKE '%120363427856964756%'"))
    conn.commit()
    print("Hostinger MySQL & local database updated status to SENT successfully!")
