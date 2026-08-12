"""
Test Company-Wise Escalation Report formatting logic:
- Grouped by Company/Department
- Missing reports (❌) at TOP
- Submitted reports (🟢) at LAST
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import UnifiedReminder, ReminderLog, ProcessedData, RawMessage, Group, Task, WhatsAppMessage
from sqlalchemy import func, or_, and_
from scheduler import get_all_waha_groups_map, clean_name_string

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)
start_of_day = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_day = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

db = SessionLocal()
waha_groups_map = get_all_waha_groups_map()

# Fetch DB group map
all_groups = db.query(Group).all()
group_db_map = {g.whatsapp_group_id: g.name for g in all_groups if g.whatsapp_group_id}

# 1. Fetch Tasks
tasks_today = db.query(Task).filter(
    Task.due_time <= end_of_day,
    or_(Task.status != 'completed', and_(Task.status == 'completed', Task.due_time >= start_of_day))
).order_by(Task.due_time).all()

not_completed_tasks = []
completed_tasks = []
if tasks_today:
    for t in tasks_today:
        assignee = t.assigned_person_name or "Team"
        if t.status == 'completed':
            completed_tasks.append(f"  • 🟢 *{assignee}*: {t.task_name} - Completed")
        else:
            not_completed_tasks.append(f"  • ❌ *{assignee}*: {t.task_name} - Not Completed")

all_task_lines = not_completed_tasks + completed_tasks

# 2. Fetch Reminders
reminders_today = db.query(UnifiedReminder).filter(
    UnifiedReminder.trigger_time <= end_of_day,
    or_(UnifiedReminder.status == 'pending', and_(UnifiedReminder.status.in_(['sent', 'skipped']), UnifiedReminder.trigger_time >= start_of_day))
).all()

sent_logs_today = db.query(ReminderLog).filter(ReminderLog.executed_at >= start_of_day, ReminderLog.status == 'sent').all()
sent_reminder_ids = {log.reminder_id for log in sent_logs_today if log.reminder_id}
raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()
processed_today_all = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == start_of_day.date()).all()

# Build company categories dict
from collections import defaultdict
company_data = defaultdict(list)

def format_rep_title(r_str):
    words = r_str.strip().split()
    res = []
    for w in words:
        wl = w.lower()
        if wl in ['p&l', 'p/l', 'p-and-l']: res.append('P&L')
        elif wl in ['ca']: res.append('CA')
        elif wl in ['eod']: res.append('EOD')
        else: res.append(w.capitalize())
    return " ".join(res)

for r in reminders_today:
    grp_name = waha_groups_map.get(r.whatsapp_group_id) or group_db_map.get(r.whatsapp_group_id) or r.person_name or "General"
    clean_grp = grp_name.strip()
    
    # Normalize category names
    if "accounts" in clean_grp.lower(): clean_grp = "Accounts Poultry"
    elif "corporate" in clean_grp.lower(): clean_grp = "Sunfra Corporate P&L"
    elif "jataayu" in clean_grp.lower(): clean_grp = "Jataayu Updates"
    elif "feed plant" in clean_grp.lower() or "feed" in clean_grp.lower(): clean_grp = "Feed Plant"
    elif "hyperscale" in clean_grp.lower(): clean_grp = "Sunfra Hyperscale"
    
    reports = [rep.strip() for rep in (r.report_types or '').split(',') if rep.strip()]
    is_manually_done = (r.status == 'sent' and r.id not in sent_reminder_ids)
    is_all_skipped = (r.status == 'skipped' or is_manually_done)
    
    for rep in reports:
        rep_formatted = format_rep_title(rep)
        submitted = is_all_skipped
        
        # Check raw messages if not already skipped
        if not submitted:
            rep_lower = rep.lower()
            for m in raw_messages_today:
                txt = (m.raw_text or '').lower()
                if rep_lower in txt or (any(kw in txt for kw in ['update', 'eod', 'report', 'submitted', 'done']) and any(kw in rep_lower for kw in ['update', 'report', 'daily'])):
                    submitted = True
                    break
                    
        company_data[clean_grp].append({
            "name": rep_formatted,
            "submitted": submitted
        })

# Format report output by company
# Sort companies: companies with missing reports first!
sorted_companies = sorted(
    company_data.keys(),
    key=lambda c: (0 if any(not item["submitted"] for item in company_data[c]) else 1, c)
)

report_msg_lines = []

for comp in sorted_companies:
    items = company_data[comp]
    # Sort items within company: missing (submitted=False) first, submitted (submitted=True) last!
    sorted_items = sorted(items, key=lambda x: (1 if x["submitted"] else 0, x["name"]))
    
    if len(sorted_items) == 1:
        item = sorted_items[0]
        status_symbol = "🟢 Submitted" if item["submitted"] else "❌ Not Submitted"
        report_msg_lines.append(f"* {comp}: *{item['name']}* - {status_symbol}")
    else:
        report_msg_lines.append(f"* *{comp}:*")
        for item in sorted_items:
            status_symbol = "🟢" if item["submitted"] else "❌"
            report_msg_lines.append(f"  • {item['name']} - {status_symbol}")

# Assemble final report
date_str = now_ist.strftime("%d %b %Y")
final_lines = [
    "🚨 *Daily Escalation Report*",
    f"📅 *Date:* {date_str}\n",
    "The following is the update on today's tasks and reports:\n"
]

if all_task_lines:
    final_lines.append("*Tasks:*")
    final_lines.extend(all_task_lines)
    final_lines.append("")

if report_msg_lines:
    final_lines.append("*Reports:*")
    final_lines.extend(report_msg_lines)

final_text = "\n".join(final_lines)

print("=== PREVIEW OF COMPANY-WISE ESCALATION REPORT ===")
print(final_text)

db.close()
