import sys, os, datetime, re, difflib
sys.path.append('/app')

from database import SessionLocal
from models import RawMessage, ProcessedData, WhatsAppMessage, Task, UnifiedReminder, ReminderLog, Group
from scheduler import get_all_waha_groups_map, clean_name_string, get_company_category
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_, and_, func

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)
start_of_day = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_day = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

db = SessionLocal()
waha_groups_map = get_all_waha_groups_map()

raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()
msg_jids = {w.message_id: w.group_id for w in db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day).all()}

tasks_today = db.query(Task).filter(
    Task.due_time <= end_of_day,
    or_(
        Task.status != 'completed',
        and_(Task.status == 'completed', Task.due_time >= start_of_day)
    )
).order_by(Task.due_time).all()

reminders_today = db.query(UnifiedReminder).filter(
    UnifiedReminder.trigger_time <= end_of_day,
    or_(
        UnifiedReminder.status == 'pending',
        and_(UnifiedReminder.status.in_(['sent', 'skipped']), UnifiedReminder.trigger_time >= start_of_day)
    )
).all()

sent_logs_today = db.query(ReminderLog).filter(
    ReminderLog.executed_at >= start_of_day,
    ReminderLog.status == 'sent'
).all()
sent_reminder_ids = {log.reminder_id for log in sent_logs_today if log.reminder_id}

reminders_to_check = []
for r in reminders_today:
    reminders_to_check.append({
        "id": r.id,
        "person_name": r.person_name,
        "person_phone": r.person_phone,
        "whatsapp_group_id": r.whatsapp_group_id,
        "report_types": r.report_types,
        "status": r.status
    })

companies = {
    "Jataayu Jewellers": {"tasks": [], "reports": []},
    "Corporate Company (P&L)": {"tasks": [], "reports": []},
    "Sunfra Farms": {"tasks": [], "reports": []}
}

if tasks_today:
    for t in tasks_today:
        assignee = None
        if t.whatsapp_group_id:
            clean_jid = t.whatsapp_group_id.replace('@g.us', '') + '@g.us'
            if clean_jid in waha_groups_map: assignee = waha_groups_map[clean_jid]
            else:
                grp = db.query(Group).filter(Group.whatsapp_group_id == clean_jid).first()
                if grp: assignee = grp.name
        if not assignee or assignee.lower() == 'team':
            assignee = t.assigned_person_name or t.assigned_person_phone or "Unknown"
        status_text = "Completed" if t.status == 'completed' else "Not Completed"
        status_emoji = "✅" if t.status == 'completed' else "❌"
        line = f"- {status_emoji} {assignee}: *{t.task_name}* - {status_text}"
        comp = get_company_category(assignee)
        companies[comp]["tasks"].append((t.status == 'completed', line))

update_keywords = [
    "update", "updates", "work report", "work update", "work updates",
    "daily update", "daily updates", "daily work update", "daily work updates",
    "eod", "eod update", "eod updates", "eod report", "eod reports",
    "today, i worked", "today i worked", "today's work", "today work",
    "today's work report", "today work report", "work day report",
    "daily report", "daily reports", "work done", "tasks completed",
    "task completed", "tasks done", "task done", "today's update", "today update",
    "profit summary", "profit update", "p&l summary", "p&l update", "summary",
    "website update", "website updates", "stock update", "stock updates", "feed materials to shed"
]

for r in reminders_to_check:
    clean_group_jid = None
    group_name_display = None
    if r["whatsapp_group_id"]:
        clean_group_jid = r["whatsapp_group_id"]
        if not clean_group_jid.endswith('@g.us'): clean_group_jid += '@g.us'
        if clean_group_jid in waha_groups_map: group_name_display = waha_groups_map[clean_group_jid]
        else:
            group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
            if group: group_name_display = group.name
            else: group_name_display = clean_group_jid

    msgs_today = []
    clean_target_jid_stripped = clean_group_jid.replace('@g.us', '').strip() if clean_group_jid else ''
    grp_obj = db.query(Group).filter(Group.whatsapp_group_id.like(f"%{clean_target_jid_stripped}%")).first() if clean_target_jid_stripped else None
    target_group_name = waha_groups_map.get(clean_group_jid) or (grp_obj.name if grp_obj else "")

    for raw_msg in raw_messages_today:
        clean_phone = "".join(c for c in r["person_phone"] if c.isdigit())
        if clean_phone.startswith("0"): clean_phone = clean_phone[1:]
        alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
        raw_msg_jid = msg_jids.get(raw_msg.message_id) or ''
        clean_raw_jid = raw_msg_jid.replace('@g.us', '').strip()

        match_group_raw = (
            raw_msg.group_name
            and target_group_name
            and (str(raw_msg.group_name).lower() in str(target_group_name).lower() or str(target_group_name).lower() in str(raw_msg.group_name).lower())
        )

        keyword_group_match = False
        if raw_msg.group_name and r["report_types"]:
            gn_lower = raw_msg.group_name.lower()
            rt_lower = r["report_types"].lower()
            if ("egg pricing" in gn_lower and "egg pricing" in rt_lower) or \
               ("rule book" in gn_lower and "rule" in rt_lower) or \
               ("raw material" in gn_lower and ("stock" in rt_lower or "website" in rt_lower)) or \
               ("p&l" in gn_lower and ("p&l" in rt_lower or "profit" in rt_lower)) or \
               ("hyperscale" in gn_lower and "hyperscale" in rt_lower) or \
               ("jataayu" in gn_lower and "jataayu" in rt_lower):
                keyword_group_match = True

        is_match = False
        if clean_target_jid_stripped:
            is_match = (clean_raw_jid and clean_raw_jid == clean_target_jid_stripped) or match_group_raw or keyword_group_match
        else:
            sender_matched = (clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender))
            is_match = sender_matched or keyword_group_match

        if is_match: msgs_today.append(raw_msg)

    is_egg_pricing = "egg pricing" in r["report_types"].lower()
    is_ca_statement = "ca statement" in r["report_types"].lower() or "ca" in r["report_types"].lower()
    is_rule_book = "rule book" in r["report_types"].lower() or "rule" in r["report_types"].lower()
    is_profit_report = any(w in r["report_types"].lower() for w in ["profit", "p&l", "p and l", "p/l", "loss"])
    is_update_report = any(w in r["report_types"].lower() for w in ["update", "eod", "daily report", "work", "stock", "website"]) and not is_egg_pricing and not is_rule_book and not is_profit_report

    report_keywords = []
    for comma_part in r["report_types"].split(","):
        for slash_part in comma_part.split("/"):
            trimmed = slash_part.strip().lower()
            if trimmed: report_keywords.append(trimmed)

    is_manually_done = (r.get("status") == 'sent' and r.get("id") not in sent_reminder_ids)
    submitted = (r.get("status") == 'skipped' or is_manually_done)
    msgs_to_check = msgs_today if not submitted else []
    for m in msgs_to_check:
        text_lower = (m.raw_text or "").lower()
        msg_hour = m.timestamp.hour
        if is_egg_pricing:
            time_keyword = "morning" if "morning" in r["report_types"].lower() else "afternoon" if "afternoon" in r["report_types"].lower() else "evening" if "evening" in r["report_types"].lower() else None
            has_price_number = bool(re.search(r'\d{3}', text_lower))
            is_time_match = False
            msg_hour_to_use = msg_hour
            match_time = re.search(r'\b(\d{1,2}):(\d{2})\b', text_lower)
            if match_time:
                try: msg_hour_to_use = int(match_time.group(1))
                except Exception: pass

            if time_keyword == 'morning' and (msg_hour_to_use < 12 or 'morning' in text_lower or 'veh kol' in text_lower) and 'ppr rate' not in text_lower and 'closing' not in text_lower:
                is_time_match = True
            elif time_keyword == 'afternoon' and (12 <= msg_hour_to_use < 17 or 'afternoon' in text_lower or 'ppr rate' in text_lower or 'paper rate' in text_lower) and 'closing' not in text_lower:
                is_time_match = True
            elif time_keyword == 'evening' and (msg_hour_to_use >= 17 or 'evening' in text_lower or 'closing' in text_lower or '18:' in text_lower or '19:' in text_lower):
                is_time_match = True

            if is_time_match and has_price_number and any(w in text_lower for w in ["egg", "price", "pricing", "ppr rate", "paper rate", "closing", "veh kol", "papaak"]):
                submitted = True
                break
        elif is_profit_report:
            profit_kws = ["profit", "p&l", "p and l", "p/l", "loss", "profit summary", "p&l summary", "summary", "profit update", "p&l report", "p&l statement"]
            if any(kw in text_lower for kw in profit_kws) and "yesterday" not in text_lower:
                submitted = True
                break
        elif is_ca_statement:
            if 'ca' in text_lower or 'statement' in text_lower:
                submitted = True
                break
        elif is_rule_book:
            rule_kws = ["rule book", "rules book", "rule", "rules", "point", "points", "policy", "guideline", "godown rule", "farm rule", "addition"]
            if any(kw in text_lower for kw in rule_kws):
                submitted = True
                break
        elif is_update_report:
            if any(kw in text_lower for kw in update_keywords) or any(kw in text_lower for kw in report_keywords):
                submitted = True
                break
        else:
            if any(kw in text_lower for kw in report_keywords):
                submitted = True
                break

    display_name = f"{group_name_display}" if group_name_display else r["person_name"]
    status_text = "Submitted" if submitted else "Not Submitted"
    status_emoji = "✅" if submitted else "❌"
    line = f"- {status_emoji} {display_name}: *{r['report_types']}* - {status_text}"
    comp = get_company_category(display_name if group_name_display else r["whatsapp_group_id"] or r["person_name"])
    companies[comp]["reports"].append((submitted, line))

print("\n=== UPDATED 11:59 PM COMPANY-WISE ESCALATION REPORT ===")
print("🚨 *Daily Escalation Report*")
print("The following is the update on today's tasks and reports, organized by company:\n")
for comp in ["Jataayu Jewellers", "Corporate Company (P&L)", "Sunfra Farms"]:
    comp_tasks = companies[comp]["tasks"]
    comp_reports = companies[comp]["reports"]
    if not comp_tasks and not comp_reports: continue
    if comp_tasks and comp_reports:
        print(f"🏢 *{comp} Tasks:*")
        for completed, line in sorted(comp_tasks, key=lambda x: x[0]): print(line)
        print("\n*Reports:*")
        for submitted_flag, line in sorted(comp_reports, key=lambda x: x[0]): print(line)
        print()
    elif comp_tasks:
        print(f"🏢 *{comp} Tasks:*")
        for completed, line in sorted(comp_tasks, key=lambda x: x[0]): print(line)
        print()
    elif comp_reports:
        print(f"🏢 *{comp} Reports:*")
        for submitted_flag, line in sorted(comp_reports, key=lambda x: x[0]): print(line)
        print()

db.close()
