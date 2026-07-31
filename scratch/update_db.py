import sys
sys.path.append('/app')
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE sunfra_unified_reminders SET status = 'pending' WHERE id = 189 OR whatsapp_group_id LIKE '%120363427856964756%'"))
    conn.commit()
    print("Hostinger MySQL & local database updated to PENDING successfully!")
