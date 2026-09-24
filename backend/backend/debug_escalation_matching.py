import sys, datetime
sys.path.append('/app')
from database import SessionLocal
from models import RawMessage, UnifiedReminder, Group, WhatsAppMessage
from scheduler import get_all_waha_groups_map

db = SessionLocal()
waha_groups_map = get_all_waha_groups_map()
today = datetime.datetime.now().date()

raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= f"{today} 00:00:00").all()
msg_jids = {w.message_id: w.group_id for w in db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= f"{today} 00:00:00").all()}

reminders = db.query(UnifiedReminder).filter(UnifiedReminder.trigger_time <= f"{today} 23:59:59").all()

print("=== CHECKING MATCHES FOR ALL REMINDERS TODAY ===")
for r in reminders:
    r_name = r.person_name or ""
    r_type = r.report_types or ""
    r_group = r.whatsapp_group_id or ""
    print(f"\nReminder ID {r.id}: Name='{r_name}' | Type='{r_type}' | Group='{r_group}'")
    
    # Check matching raw messages
    matched_msgs = []
    for m in raw_msgs:
        m_jid = msg_jids.get(m.message_id) or ""
        m_text = m.raw_text or ""
        
        # Check group match
        group_match = False
        if r_group:
            clean_r_group = r_group.replace('@g.us', '').strip()
            clean_m_jid = m_jid.replace('@g.us', '').strip()
            if clean_r_group and clean_m_jid and clean_r_group == clean_m_jid:
                group_match = True
        
        # Check text match
        text_match = False
        m_lower = m_text.lower()
        if "egg pricing" in r_type.lower():
            if "afternoon" in r_type.lower() and ("afternoon" in m_lower or "12:04" in m_lower or "papaak" in m_lower):
                text_match = True
            elif "evening" in r_type.lower() and ("evening" in m_lower or "closing" in m_lower):
                text_match = True
        elif "rule" in r_type.lower():
            if any(w in m_lower for w in ["rule", "rules", "point", "policy"]):
                text_match = True
        elif "stock" in r_type.lower() or "website" in r_type.lower():
            if any(w in m_lower for w in ["website update", "website updates", "stock update", "stock updates"]):
                text_match = True

        if group_match or text_match:
            print(f"   -> RawMsg {m.timestamp}: group_match={group_match}, text_match={text_match} | Text: '{m_text[:60]}'")

db.close()
