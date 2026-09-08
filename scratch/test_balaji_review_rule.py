from database import SessionLocal
from models import WhatsAppMessage
from datetime import datetime, date

db = SessionLocal()
msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.group_id == '120363406924564250@g.us').all()

def evaluate_day(d_str, label):
    day_msgs = [m for m in msgs if m.timestamp.strftime('%Y-%m-%d') == d_str]
    approval_kws = ['reviewed', 'review completed', 'reviewed and approved', 'approved', 'approve', 'report approved', 'review done', 'reviewed done']
    
    submitted = False
    match_detail = ''
    for m in day_msgs:
        # Check only before 11:00 PM (23:00)
        if m.timestamp.hour >= 23 and m.timestamp.minute > 0:
            continue
        text_lower = (m.message_text or '').lower()
        sender_id = str(m.sender_id or '')
        is_approver = ('balaji' in sender_id.lower() or '9493928388' in sender_id or '242695733772318' in sender_id)
        has_approval_word = any(akw in text_lower.split() or akw in text_lower for akw in approval_kws)
        if is_approver and has_approval_word and 'why' not in text_lower and '?' not in text_lower:
            submitted = True
            match_detail = f"{m.timestamp.strftime('%H:%M:%S')} - '{m.message_text}'"
            break
            
    print(f"[{label} - {d_str}] Submitted before 11:00 PM: {submitted}")
    if submitted:
        print(f"   -> Match: {match_detail}")
        print(f"   -> Action: SKIP reminder at 11:00 PM (Balaji already reviewed)")
    else:
        print(f"   -> Action: SEND REMINDER at 11:00 PM (Balaji has not reviewed yet)")

# Case 1: Sep 3 (Balaji sent Reviewed at 22:18)
evaluate_day('2026-09-03', 'Case 1: Balaji reviewed before 11 PM')

# Case 2: Sep 7 (Balaji did NOT review before 11 PM)
evaluate_day('2026-09-07', 'Case 2: Balaji did NOT review before 11 PM')

# Case 3: Today
evaluate_day(date.today().strftime('%Y-%m-%d'), 'Case 3: Today')

db.close()
