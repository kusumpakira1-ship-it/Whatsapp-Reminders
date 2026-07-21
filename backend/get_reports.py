import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.append('/app')
from database import SessionLocal
from models import RawMessage, UnifiedReminder, Group
from egg_market_analyzer import parse_market_rates_from_messages, calculate_market_analysis

db = SessionLocal()
IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

yesterday_date = now_ist.date() - timedelta(days=1)
yesterday_start = datetime(yesterday_date.year, yesterday_date.month, yesterday_date.day, 0, 0, 0)
yesterday_end = datetime(yesterday_date.year, yesterday_date.month, yesterday_date.day, 23, 59, 59)
day_before_start = yesterday_start - timedelta(days=1)

print("=== 1. YESTERDAY EGG SUMMARY REPORT ===")
y_msgs = db.query(RawMessage).filter(
    (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
    RawMessage.timestamp >= yesterday_start,
    RawMessage.timestamp <= yesterday_end
).order_by(RawMessage.timestamp.asc()).all()

db_msgs = db.query(RawMessage).filter(
    (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
    RawMessage.timestamp >= day_before_start,
    RawMessage.timestamp < yesterday_start
).order_by(RawMessage.timestamp.asc()).all()

extracted = parse_market_rates_from_messages(y_msgs, db_msgs)
analysis = calculate_market_analysis(extracted)

print("\nEGG PRICE MOVEMENT (July 20):")
for r in analysis['egg_rows']:
    stat_clean = re.sub(r'<[^>]*>', '', r['status'])
    print(f"{r['market']:15s} | Morning: {r['morning']:5s} | Afternoon: {r['afternoon']:5s} | Evening: {r['evening']:5s} | Status: {stat_clean}")

print("\nLOADING RATES:")
for r in analysis['loading_rows']:
    stat_clean = re.sub(r'<[^>]*>', '', r['status'])
    print(f"{r['market']:15s} | Yesterday: {r['yesterday']:5s} | Today: {r['today']:5s} | Change: {r['change']:5s} | Status: {stat_clean}")

print("\nPAPER RATES:")
for r in analysis['paper_rows']:
    stat_clean = re.sub(r'<[^>]*>', '', r['status'])
    print(f"{r['market']:15s} | Yesterday: {r['yesterday']:5s} | Today: {r['today']:5s} | Change: {r['change']:5s} | Status: {stat_clean}")

print("\nOVERALL COMBINED:")
for r in analysis['combined_rows']:
    stat_clean = re.sub(r'<[^>]*>', '', r['overall_status'])
    print(f"{r['market']:15s} | Egg: {r['egg_price']:5s} | Loading: {r['loading']:10s} | Paper: {r['paper']:10s} | Overall: {stat_clean}")

print("\n=== 2. DAILY ESCALATION MESSAGE ===")
reminders = db.query(UnifiedReminder).filter(UnifiedReminder.status != 'deleted').all()
groups = db.query(Group).all()
waha_groups_map = {g.whatsapp_group_id: g.name for g in groups if g.whatsapp_group_id}

raw_messages_yesterday = db.query(RawMessage).filter(
    RawMessage.timestamp >= yesterday_start,
    RawMessage.timestamp <= yesterday_end
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

unsubmitted = {}
for r in reminders:
    clean_group_jid = r.whatsapp_group_id.strip() if r.whatsapp_group_id else None
    group_name_display = 'Personal / Direct'
    if clean_group_jid:
        group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
        if group: group_name_display = group.name
        elif clean_group_jid in waha_groups_map: group_name_display = waha_groups_map[clean_group_jid]
        else: group_name_display = clean_group_jid

    msgs_y = []
    for raw_msg in raw_messages_yesterday:
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

        match_waha_sender_raw = False
        if raw_msg.sender and not r.whatsapp_group_id:
            import difflib
            sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
            manager_name = clean_name_string('kusum')
            if difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio() > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                match_waha_sender_raw = True

        if match_sender_raw or match_group_raw or match_name or match_waha_sender_raw:
            msgs_y.append(raw_msg)

    is_egg_pricing = 'egg pricing' in r.report_types.lower()
    is_update_report = any(w in r.report_types.lower() for w in ['update', 'eod', 'daily report', 'work']) and not is_egg_pricing
    submitted = False
    for m in msgs_y:
        text_lower = (m.raw_text or '').lower()
        if is_egg_pricing:
            time_keyword = 'morning' if 'morning' in r.report_types.lower() else 'afternoon' if 'afternoon' in r.report_types.lower() else 'evening' if 'evening' in r.report_types.lower() else None
            if time_keyword and time_keyword in text_lower and any(w in text_lower for w in ['egg', 'price', 'pricing']):
                submitted = True
                break
        elif is_update_report:
            if any(kw in text_lower for kw in update_keywords) or len(text_lower.strip()) > 20:
                submitted = True
                break

    if not submitted:
        key = f"{r.person_name} ({group_name_display})"
        if key not in unsubmitted: unsubmitted[key] = []
        unsubmitted[key].append(r.report_types)

if unsubmitted:
    msg_lines = [f"🚨 *EOD Escalation Alert ({yesterday_date.strftime('%d %b %Y')})* 🚨\n", "The following team members have pending reports for yesterday:\n"]
    for person, reports in unsubmitted.items():
        unique_reports = list(set(reports))
        msg_lines.append(f"👤 *{person}*\n   ❌ Missing: {', '.join(unique_reports)}\n")
    msg_lines.append("Please ensure these reports are completed immediately.")
    escalation_text = '\n'.join(msg_lines)
else:
    escalation_text = f"🎉 *All reports were submitted on time for {yesterday_date.strftime('%d %b %Y')}!*"

print(escalation_text)
