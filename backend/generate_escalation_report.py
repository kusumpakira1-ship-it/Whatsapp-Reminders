import sys
sys.path.append('/app')

from database import SessionLocal
from models import Task, ReminderLog, UnifiedReminder, Group, RawMessage, ProcessedData, WhatsAppMessage
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
import re
import difflib

# Clean name function
def clean_name_string(name: str) -> str:
    if not name:
        return ""
    import unicodedata
    normalized = unicodedata.normalize('NFKD', name)
    cleaned = "".join(c for c in normalized if c.isalnum() or c.isspace())
    return cleaned.lower().strip()

# Helper for waha groups map (query live WAHA container)
def get_all_waha_groups_map() -> dict:
    import requests
    import os
    waha_groups_map = {}
    try:
        waha_url = "http://waha:3000/api/default/groups"
        headers = {"Accept": "application/json"}
        api_key = os.getenv("WAHA_API_KEY", "123")
        if api_key:
            headers["X-Api-Key"] = api_key
        response = requests.get(waha_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                for g in data:
                    jid = g.get("id")
                    if jid:
                        waha_groups_map[jid] = g.get("subject") or g.get("name")
            elif isinstance(data, dict):
                for k, v in data.items():
                    if k:
                        waha_groups_map[k] = v.get("subject") or v.get("name")
    except Exception as e:
        print("Waha query error:", e)
    return waha_groups_map

def get_company_category(display_name: str) -> str:
    name_lower = display_name.lower()
    if "jataayu" in name_lower:
        return "Jataayu Jewellers"
    elif "p&l" in name_lower or "p & l" in name_lower or "corporate" in name_lower or "hyperscale" in name_lower:
        return "Corporate Company (P&L)"
    else:
        return "Sunfra Farms"

IST = timezone(timedelta(hours=5, minutes=30))
import sys
if len(sys.argv) > 1:
    try:
        now_ist = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        print(f"Generating escalation report for custom date: {sys.argv[1]}")
    except Exception as e:
        print(f"Error parsing date argument: {e}")
        now_ist = datetime.now(IST).replace(tzinfo=None)
else:
    now_ist = datetime.now(IST).replace(tzinfo=None)

start_of_day = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)

db = SessionLocal()
waha_groups_map = get_all_waha_groups_map()

try:
    raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()
    processed_today_all = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == start_of_day.date()).all()
    msg_jids = {w.message_id: w.group_id for w in db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day).all()}
    
    # 1. Fetch ALL Tasks due today or overdue
    from sqlalchemy import or_, and_
    end_of_day = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    if len(sys.argv) > 1:
        tasks_today = db.query(Task).all()
    else:
        tasks_today = db.query(Task).filter(
            Task.due_time <= end_of_day,
            or_(
                Task.status != 'completed',
                and_(Task.status == 'completed', Task.due_time >= start_of_day)
            )
        ).order_by(Task.due_time).all()
    
    # Organize by company
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
                if clean_jid in waha_groups_map:
                    assignee = waha_groups_map[clean_jid]
                else:
                    grp = db.query(Group).filter(Group.whatsapp_group_id == clean_jid).first()
                    if grp:
                        assignee = grp.name
            if not assignee or assignee.lower() == 'team':
                if t.whatsapp_group_id:
                    clean_jid = t.whatsapp_group_id.replace('@g.us', '') + '@g.us'
                    if clean_jid in waha_groups_map:
                        assignee = waha_groups_map[clean_jid]
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
    
    # 2. Fetch today's scheduled and overdue reminders
    if len(sys.argv) > 1:
        reminders_today = db.query(UnifiedReminder).filter(
            UnifiedReminder.report_types != 'Monthly'
        ).all()
    else:
        reminders_today = db.query(UnifiedReminder).filter(
            UnifiedReminder.trigger_time <= end_of_day,
            or_(
                UnifiedReminder.status == 'pending',
                and_(UnifiedReminder.status.in_(['sent', 'skipped']), UnifiedReminder.trigger_time >= start_of_day)
            )
        ).all()
    
    # Fetch sent logs today
    sent_logs_today = db.query(ReminderLog).filter(
        ReminderLog.executed_at >= start_of_day,
        ReminderLog.status == 'sent'
    ).all()
    sent_reminder_ids = {log.reminder_id for log in sent_logs_today if log.reminder_id}

    # Build list of reminders to check
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
    
    for r in reminders_to_check:
        clean_group_jid = None
        group_name_display = None
        if r["whatsapp_group_id"]:
            clean_group_jid = r["whatsapp_group_id"]
            if not clean_group_jid.endswith('@g.us'):
                clean_group_jid += '@g.us'
            if clean_group_jid in waha_groups_map:
                group_name_display = waha_groups_map[clean_group_jid]
            else:
                group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
                if group:
                    group_name_display = group.name
                else:
                    group_name_display = clean_group_jid
        
        msgs_today = []
        for raw_msg in raw_messages_today:
            clean_phone = "".join(c for c in r["person_phone"] if c.isdigit())
            if clean_phone.startswith("0"):
                clean_phone = clean_phone[1:]
            alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
            
            match_sender_raw = clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender)
            match_group_raw = False
            if clean_group_jid:
                group_name = waha_groups_map.get(clean_group_jid)
                match_group_raw = (
                    raw_msg.group_name
                    and group_name
                    and str(raw_msg.group_name).lower() in str(group_name).lower()
                )
            
            match_name = False
            if not match_sender_raw and r["person_name"] and raw_msg.sender:
                sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                t_names = [clean_name_string(n) for n in r["person_name"].split(',')]
                for t_name in t_names:
                    if len(sender_name_part) >= 3 and len(t_name) >= 3:
                        ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                        if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                            match_name = True
                            break
            
            match_waha_sender_raw = False
            if raw_msg.sender and not r["whatsapp_group_id"]:
                sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                manager_name = clean_name_string("kusum")
                ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                    match_waha_sender_raw = True
                            
            raw_msg_jid = msg_jids.get(raw_msg.message_id) or ''
            clean_raw_jid = raw_msg_jid.replace('@g.us', '').strip()
            clean_target_jid_stripped = clean_group_jid.replace('@g.us', '').strip() if clean_group_jid else ''
            
            is_group_level = (r["person_phone"] == '1234567890' or 'team' in r["person_name"].lower())
            
            is_match = False
            if is_group_level:
                is_match = (clean_target_jid_stripped and clean_raw_jid == clean_target_jid_stripped)
            else:
                sender_matched = match_sender_raw or match_name or match_waha_sender_raw
                if not sender_matched and r["person_name"] and 'mahalakshmi' in r["person_name"].lower() and 'mahalakshmi' in str(raw_msg.sender).lower():
                    sender_matched = True
                    
                if sender_matched:
                    if not clean_raw_jid:
                        is_match = True
                    elif clean_target_jid_stripped and clean_raw_jid == clean_target_jid_stripped:
                        is_match = True
                        
            if is_match:
                msgs_today.append(raw_msg)
        
        update_keywords = [
            "update", "updates", "work report", "work update", "work updates",
            "daily update", "daily updates", "daily work update", "daily work updates",
            "eod", "eod update", "eod updates", "eod report", "eod reports",
            "today, i worked", "today i worked", "today's work", "today work",
            "today's work report", "today work report", "work day report",
            "daily report", "daily reports", "work done", "tasks completed",
            "task completed", "tasks done", "task done", "today's update", "today update"
        ]
        is_egg_pricing = "egg pricing" in r["report_types"].lower()
        is_ca_statement = "ca statement" in r["report_types"].lower() or "ca" in r["report_types"].lower()
        is_rule_book = "rule book" in r["report_types"].lower() or "rule" in r["report_types"].lower()
        is_update_report = any(w in r["report_types"].lower() for w in ["update", "eod", "daily report", "work"]) and not is_egg_pricing and not is_rule_book
        
        report_keywords = []
        for comma_part in r["report_types"].split(","):
            for slash_part in comma_part.split("/"):
                trimmed = slash_part.strip().lower()
                if trimmed:
                    report_keywords.append(trimmed)
                    
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
                
                if time_keyword == 'morning' and (msg_hour < 12 or 'morning' in text_lower or '7:' in text_lower or '8:' in text_lower or '9:' in text_lower or '10:' in text_lower or 'veh kol' in text_lower) and 'ppr rate' not in text_lower and 'closing' not in text_lower:
                    is_time_match = True
                elif time_keyword == 'afternoon' and (12 <= msg_hour < 17 or 'afternoon' in text_lower or 'ppr rate' in text_lower or '12:' in text_lower or '13:' in text_lower or '14:' in text_lower) and 'closing' not in text_lower:
                    is_time_match = True
                elif time_keyword == 'evening' and (msg_hour >= 17 or 'evening' in text_lower or 'closing' in text_lower or '18:' in text_lower or '19:' in text_lower):
                    is_time_match = True

                if is_time_match and has_price_number and any(w in text_lower for w in ["egg", "price", "pricing", "ppr rate", "closing", "veh kol", "papaak"]):
                    submitted = True
                    break
            elif is_ca_statement:
                if 'ca' in text_lower or 'statement' in text_lower:
                    submitted = True
                    break
            elif is_rule_book:
                rule_kws = ["rule book", "rule", "rules", "point", "points", "policy", "guideline", "godown rule", "farm rule", "addition"]
                if any(kw in text_lower for kw in rule_kws):
                    submitted = True
                    break
            elif is_update_report:
                if any(kw in text_lower for kw in update_keywords):
                    submitted = True
                    break
            else:
                if any(kw in text_lower for kw in report_keywords):
                    submitted = True
                    break
                
        if not submitted:
            processed_today = []
            for p in processed_today_all:
                clean_phone = "".join(c for c in r["person_phone"] if c.isdigit())
                if clean_phone.startswith("0"):
                    clean_phone = clean_phone[1:]
                alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                
                match_sender = clean_phone in str(p.sender) or alt_phone in str(p.sender)
                match_group = False
                if clean_group_jid:
                    group_name = waha_groups_map.get(clean_group_jid)
                    match_group = (
                        p.group_name
                        and group_name
                        and str(p.group_name).lower() == group_name.lower()
                    )
                    
                match_name = False
                if not match_sender and r["person_name"] and p.sender:
                    sender_name_part = clean_name_string(p.sender.split(' (')[0])
                    t_names = [clean_name_string(n) for n in r["person_name"].split(',')]
                    for t_name in t_names:
                        if len(sender_name_part) >= 3 and len(t_name) >= 3:
                            ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                            if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                                match_name = True
                                break
                
                match_waha_sender = False
                if p.sender and not r["whatsapp_group_id"]:
                    sender_name_part = clean_name_string(p.sender.split(' (')[0])
                    manager_name = clean_name_string("kusum")
                    ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                    if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                        match_waha_sender = True
                                
                p_msg_jid = msg_jids.get(p.message_id) or ''
                clean_p_jid = p_msg_jid.replace('@g.us', '').strip()
                clean_target_jid_stripped = clean_group_jid.replace('@g.us', '').strip() if clean_group_jid else ''
                
                is_group_level = (r["person_phone"] == '1234567890' or 'team' in r["person_name"].lower())
                
                is_match = False
                if is_group_level:
                    is_match = (clean_target_jid_stripped and clean_p_jid == clean_target_jid_stripped)
                else:
                    sender_matched = match_sender or match_name or match_waha_sender
                    if sender_matched:
                        if not clean_p_jid:
                            is_match = True
                        elif clean_target_jid_stripped and clean_p_jid == clean_target_jid_stripped:
                            is_match = True
                            
                if is_match:
                    processed_today.append(p)

            for p in processed_today:
                p_cat = (p.category or "").lower()
                p_notes = (p.notes or "").lower()
                if is_egg_pricing:
                    time_keyword = "morning" if "morning" in r["report_types"].lower() else "afternoon" if "afternoon" in r["report_types"].lower() else "evening" if "evening" in r["report_types"].lower() else None
                    if time_keyword and time_keyword in p_notes and any(w in p_notes for w in ["egg", "price", "pricing"]):
                        submitted = True
                        break
                else:
                    if any(kw in p_cat for kw in report_keywords) or any(kw in p_notes for kw in report_keywords):
                        submitted = True
                        break

        display_name = f"{group_name_display}" if group_name_display else r["person_name"]
        status_text = "Submitted" if submitted else "Not Submitted"
        status_emoji = "✅" if submitted else "❌"
        line = f"- {status_emoji} {display_name}: *{r['report_types']}* - {status_text}"
        
        comp = get_company_category(display_name)
        companies[comp]["reports"].append((submitted, line))

    # Assemble the Escalation Report
    report_msg_lines = ["🚨 *Daily Escalation Report*", "The following is the update on today's tasks and reports, organized by company:\n"]
    
    for comp in ["Jataayu Jewellers", "Corporate Company (P&L)", "Sunfra Farms"]:
        comp_tasks = companies[comp]["tasks"]
        comp_reports = companies[comp]["reports"]
        
        if not comp_tasks and not comp_reports:
            continue
            
        if comp_tasks and comp_reports:
            report_msg_lines.append(f"🏢 *{comp} Tasks:*")
            comp_tasks.sort(key=lambda x: x[0])
            for completed, line in comp_tasks:
                report_msg_lines.append(line)
            report_msg_lines.append("")
            report_msg_lines.append("*Reports:*")
            comp_reports.sort(key=lambda x: x[0])
            for submitted_flag, line in comp_reports:
                report_msg_lines.append(line)
            report_msg_lines.append("")
        elif comp_tasks:
            report_msg_lines.append(f"🏢 *{comp} Tasks:*")
            comp_tasks.sort(key=lambda x: x[0])
            for completed, line in comp_tasks:
                report_msg_lines.append(line)
            report_msg_lines.append("")
        elif comp_reports:
            report_msg_lines.append(f"🏢 *{comp} Reports:*")
            comp_reports.sort(key=lambda x: x[0])
            for submitted_flag, line in comp_reports:
                report_msg_lines.append(line)
            report_msg_lines.append("")
            
    final_msg = "\n".join(report_msg_lines).strip()
    
    with open("/app/escalation_report.txt", "w", encoding="utf-8") as f_out:
        f_out.write(final_msg)
    print("SUCCESS")

except Exception as e:
    import traceback
    print("Error:", e)
    traceback.print_exc()
finally:
    db.close()
