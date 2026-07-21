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

july20_date = datetime(2026, 7, 20).date()
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

print("=== 100% PRECISE ESCALATION CHECK FOR JULY 20 ===")
unsubmitted = {}
for r in reminders:
    # Exclude non-daily reminders (Monthly / Yearly) scheduled for future dates
    if 'monthly' in r.report_types.lower() or 'yearly' in r.report_types.lower():
        if r.trigger_time and r.trigger_time.date() > july20_date + timedelta(days=5):
            continue

    clean_group_jid = r.whatsapp_group_id.strip() if r.whatsapp_group_id else None
    group_name_display = 'Personal / Direct'
    if clean_group_jid:
        group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
        if group: group_name_display = group.name
        elif clean_group_jid in waha_groups_map: group_name_display = waha_groups_map[clean_group_jid]
        else: group_name_display = clean_group_jid

    matched_msgs = []
    clean_phone = ''.join(c for c in r.person_phone if c.isdigit()) if r.person_phone else ''
    if clean_phone.startswith('0'): clean_phone = clean_phone[1:]
    alt_phone = ('91' + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith('91') else clean_phone

    for raw_msg in raw_msgs_july20:
        match_sender_raw = clean_phone and (clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender))
        match_group_raw = False
        if clean_group_jid:
            group_name = waha_groups_map.get(clean_group_jid)
            match_group_raw = (raw_msg.group_name and group_name and (str(raw_msg.group_name).lower() in str(group_name).lower() or str(group_name).lower() in str(raw_msg.group_name).lower()))

        # For group reminders, MUST be sent in that group OR assigned to that person in that group
        if clean_group_jid:
            if match_group_raw or (match_sender_raw and raw_msg.group_name and group_name_display and str(raw_msg.group_name).lower() in str(group_name_display).lower()):
                matched_msgs.append(raw_msg)
        else:
            if match_sender_raw:
                matched_msgs.append(raw_msg)
            elif r.person_name and 'mahalakshmi' in r.person_name.lower() and 'mahalakshmi' in str(raw_msg.sender).lower():
                matched_msgs.append(raw_msg)

    is_egg_pricing = 'egg pricing' in r.report_types.lower()
    is_ca_statement = 'ca statement' in r.report_types.lower() or 'ca' in r.report_types.lower()
    is_pnl_report = 'p&l' in r.report_types.lower() or 'pnl' in r.report_types.lower() or 'profit' in r.report_types.lower()
    is_hyperscale = 'hyperscale' in r.report_types.lower()
    is_update_report = any(w in r.report_types.lower() for w in ['update', 'eod', 'daily report', 'work']) and not is_egg_pricing and not is_pnl_report and not is_hyperscale
    
    submitted = False
    sub_reason = ""
    for m in matched_msgs:
        text_lower = (m.raw_text or '').lower()
        msg_hour = m.timestamp.hour

        if is_egg_pricing:
            time_keyword = 'morning' if 'morning' in r.report_types.lower() else 'afternoon' if 'afternoon' in r.report_types.lower() else 'evening' if 'evening' in r.report_types.lower() else None
            has_price_number = bool(re.search(r'\d{3}', text_lower))
            is_time_match = False
            
            if time_keyword == 'morning':
                if (msg_hour < 12 or 'morning' in text_lower or '7:' in text_lower or '8:' in text_lower or '9:' in text_lower or '10:' in text_lower or 'veh kol' in text_lower) and 'ppr rate' not in text_lower and 'closing' not in text_lower:
                    is_time_match = True
            elif time_keyword == 'afternoon':
                if (12 <= msg_hour < 17 or 'afternoon' in text_lower or 'ppr rate' in text_lower or '12:' in text_lower or '13:' in text_lower or '14:' in text_lower) and 'closing' not in text_lower:
                    is_time_match = True
            elif time_keyword == 'evening':
                if msg_hour >= 17 or 'evening' in text_lower or 'closing' in text_lower or '18:' in text_lower or '19:' in text_lower:
                    is_time_match = True

            if is_time_match and has_price_number and any(w in text_lower for w in ['egg', 'price', 'pricing', 'ppr rate', 'closing', 'veh kol', 'papaak']):
                submitted = True
                sub_reason = f"Egg pricing match: {m.raw_text[:40]}"
                break

        elif is_ca_statement:
            if 'ca' in text_lower or 'statement' in text_lower:
                submitted = True
                sub_reason = f"CA Statement match: {m.raw_text[:40]}"
                break

        elif is_pnl_report:
            if any(w in text_lower for w in ['pnl', 'p&l', 'profit', 'loss', 'statement', 'financial', 'revenue', 'income']):
                submitted = True
                sub_reason = f"P&L report match: {m.raw_text[:40]}"
                break

        elif is_hyperscale:
            if any(w in text_lower for w in ['hyperscale', 'scale', 'update', 'report']) or len(text_lower.strip()) > 20:
                submitted = True
                sub_reason = f"Hyperscale match: {m.raw_text[:40]}"
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

print("\n=== PRECISE ESCALATION MESSAGE FOR JULY 20 ===")
if unsubmitted:
    msg_lines = [f"🚨 *EOD Escalation Alert ({july20_date.strftime('%d %b %Y')})* 🚨\n", "The following team members have pending reports for yesterday:\n"]
    for person, reports in unsubmitted.items():
        unique_reports = list(set(reports))
        msg_lines.append(f"👤 *{person}*\n   ❌ Missing: {', '.join(unique_reports)}\n")
    msg_lines.append("Please ensure these reports are completed immediately.")
    print('\n'.join(msg_lines))
else:
    print(f"🎉 *All reports were submitted on time for {july20_date.strftime('%d %b %Y')}!*")
