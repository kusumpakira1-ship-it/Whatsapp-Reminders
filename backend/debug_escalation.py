import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.append('/app')
from database import SessionLocal
from models import RawMessage, UnifiedReminder, Group

db = SessionLocal()
IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

july20_start = datetime(2026, 7, 20, 0, 0, 0)
july20_end = datetime(2026, 7, 20, 23, 59, 59)

reminders = db.query(UnifiedReminder).filter(UnifiedReminder.status != 'deleted').all()
groups = db.query(Group).all()
waha_groups_map = {g.whatsapp_group_id: g.name for g in groups if g.whatsapp_group_id}

raw_msgs_july20 = db.query(RawMessage).filter(
    RawMessage.timestamp >= july20_start,
    RawMessage.timestamp <= july20_end
).all()

def clean_name_string(s):
    if not s: return ''
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s)).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

update_keywords = [
    'update', 'updates', 'eod', 'work update', 'daily update', 'daily work update',
    'eod update', 'daily report', 'report', 'reports', 'work report', 'work day report',
    "today's work report", "today work report", "today's work", "today work",
    'done', 'completed', 'submitted', 'edited', 'posted', 'shared', 'added',
    'checked', 'fixed', 'working', 'tasks', 'work'
]

print("=== CHECKING ALL REMINDERS FOR JULY 20 ===")
unsubmitted = {}
for r in reminders:
    clean_group_jid = r.whatsapp_group_id.strip() if r.whatsapp_group_id else None
    group_name_display = 'Personal / Direct'
    if clean_group_jid:
        group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
        if group: group_name_display = group.name
        elif clean_group_jid in waha_groups_map: group_name_display = waha_groups_map[clean_group_jid]
        else: group_name_display = clean_group_jid

    matched_msgs = []
    for raw_msg in raw_msgs_july20:
        clean_phone = ''.join(c for c in r.person_phone if c.isdigit())
        if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
        alt_phone = ('91' + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith('91') else clean_phone

        match_sender_raw = clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender)
        match_group_raw = False
        if clean_group_jid:
            group_name = waha_groups_map.get(clean_group_jid)
            match_group_raw = (raw_msg.group_name and group_name and str(raw_msg.group_name).lower() == group_name.lower())

        match_name = False
        if not match_sender_raw and r.person_name and raw_msg.sender:
            import difflib
            sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
            t_names = [clean_name_string(n) for n in r.person_name.split(',')]
            for t_name in t_names:
                if len(sender_name_part) >= 3 and len(t_name) >= 3:
                    if difflib.SequenceMatcher(None, sender_name_part, t_name).ratio() > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                        match_name = True
                        break

        if match_sender_raw or match_group_raw or match_name:
            matched_msgs.append(raw_msg)

    is_egg_pricing = 'egg pricing' in r.report_types.lower()
    is_update_report = any(w in r.report_types.lower() for w in ['update', 'eod', 'daily report', 'work']) and not is_egg_pricing
    submitted = False
    sub_reason = ""
    for m in matched_msgs:
        text_lower = (m.raw_text or '').lower()
        if is_egg_pricing:
            time_keyword = 'morning' if 'morning' in r.report_types.lower() else 'afternoon' if 'afternoon' in r.report_types.lower() else 'evening' if 'evening' in r.report_types.lower() else None
            if time_keyword and time_keyword in text_lower and any(w in text_lower for w in ['egg', 'price', 'pricing']):
                submitted = True
                sub_reason = f"Egg pricing match: {m.raw_text[:40]}"
                break
        elif is_update_report:
            if any(kw in text_lower for kw in update_keywords) or len(text_lower.strip()) > 20:
                submitted = True
                sub_reason = f"Work update match: {m.raw_text[:40]}"
                break

    status_str = f"SUBMITTED ({sub_reason})" if submitted else "MISSING"
    print(f"Reminder ID: {r.id:3d} | Group: {group_name_display:30s} | Person: {r.person_name:15s} | Report: {r.report_types:35s} | Status: {status_str}")

    if not submitted:
        key = f"{r.person_name} ({group_name_display})"
        if key not in unsubmitted: unsubmitted[key] = []
        unsubmitted[key].append(r.report_types)

print("\n=== ACCURATE ESCALATION ALERT FOR JULY 20 ===")
if unsubmitted:
    msg_lines = [f"🚨 *EOD Escalation Alert (20 Jul 2026)* 🚨\n", "The following team members have pending reports for yesterday:\n"]
    for person, reports in unsubmitted.items():
        unique_reports = list(set(reports))
        msg_lines.append(f"👤 *{person}*\n   ❌ Missing: {', '.join(unique_reports)}\n")
    msg_lines.append("Please ensure these reports are completed immediately.")
    print('\n'.join(msg_lines))
else:
    print("🎉 All reports were submitted on time for 20 Jul 2026!")
