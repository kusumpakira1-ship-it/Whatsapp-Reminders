import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from report_generator import generate_daily_reports, generate_custom_report
from waha_service import send_waha_message, send_waha_file, get_session_status, get_session_qr
from config import settings
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models import ReportRecipient, Group, Employee, ProcessedData, SystemSetting, CustomAlarm, UnifiedReminder
from sqlalchemy import func

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def _get_recipient_list():
    import os
    db = SessionLocal()
    try:
        recipients = db.query(ReportRecipient).filter(ReportRecipient.is_active == True).all()
        phones = [r.phone_number for r in recipients]
    except Exception as e:
        logger.error(f"Error fetching report recipients: {e}")
        phones = []
    finally:
        db.close()

    # Append Manager Phone from config
    manager_phone = settings.MANAGER_PHONE
    if manager_phone:
        manager_jid = manager_phone
        if not manager_jid.endswith('@c.us') and not manager_jid.endswith('@g.us') and not manager_jid.endswith('@lid'):
            manager_jid += '@c.us'
        if manager_jid not in phones:
            phones.append(manager_jid)
    return phones

async def _send_reports_to_all(pdf_path, summary_text):
    phones = _get_recipient_list()
    if not phones:
        logger.warning("No active recipients or manager configured to send reports to.")
        return
        
    for phone in phones:
        if summary_text:
            send_waha_message(phone, summary_text)
        if pdf_path:
            send_waha_file(phone, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")

async def scheduled_report_job():
    logger.info("Starting scheduled 10 PM daily report generation...")
    pdf_path, summary_text = generate_daily_reports()
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_weekly_report_job():
    logger.info("Starting scheduled weekly report generation...")
    pdf_path, summary_text = generate_custom_report('weekly')
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_monthly_report_job():
    logger.info("Starting scheduled monthly report generation...")
    pdf_path, summary_text = generate_custom_report('monthly')
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_yearly_report_job():
    logger.info("Starting scheduled yearly report generation...")
    pdf_path, summary_text = generate_custom_report('yearly')
    await _send_reports_to_all(pdf_path, summary_text)

def check_missing_reports_for_today() -> dict:
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date()
    
    db = SessionLocal()
    try:
        data = db.query(ProcessedData).filter(
            func.date(ProcessedData.processed_time) == today
        ).all()
        
        received = set()
        for d in data:
            shead = str(d.shead_name or '').replace('Shead', 'Shed').strip()
            if not shead:
                continue
            cat = d.category
            if cat in ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']:
                received.add((shead, 'Production'))
            elif cat in ['feed', 'raw_material']:
                received.add((shead, 'Feed'))
            elif cat in ['medicine', 'expense']:
                received.add((shead, 'Expenditure'))
                
        missing = {}
        for shed in ["Shed 1", "Shed 2", "Shed 3"]:
            shed_missing = []
            if (shed, 'Production') not in received:
                shed_missing.append('Egg Collection')
            if (shed, 'Feed') not in received:
                shed_missing.append('Feed Consumption')
            if (shed, 'Expenditure') not in received:
                shed_missing.append('Shed Expenditure')
            if shed_missing:
                missing[shed] = shed_missing
                
        return missing
    except Exception as e:
        logger.error(f"Error checking missing reports: {e}")
        return {}
    finally:
        db.close()

async def scheduled_reminder_job():
    logger.info("Starting scheduled 6 PM data entry reminder...")
    missing = check_missing_reports_for_today()
    if not missing:
        logger.info("All data submitted successfully. No reminders needed.")
        return
        
    # Format message
    msg_lines = []
    msg_lines.append("⏰ *Daily Data Entry Alert (6:00 PM)*")
    msg_lines.append("The following data is missing for today:")
    for shed, items in missing.items():
        msg_lines.append(f"- *{shed}*: {', '.join(items)}")
    msg_lines.append("")
    msg_lines.append("Please submit today's missing reports in the group as soon as possible so that the 11:00 PM Daily Farm Summary report is accurate!")
    
    reminder_text = "\n".join(msg_lines)
    phones = _get_recipient_list()
    
    for phone in phones:
        send_waha_message(phone, reminder_text)

async def scheduled_targeted_reminder_job():
    logger.info("Starting targeted 5:00 PM missed report reminder...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date()
    
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        for emp in employees:
            # Check if this employee submitted their assigned report today
            submitted = db.query(ProcessedData).filter(
                func.date(ProcessedData.processed_time) == today,
                ProcessedData.sender.contains(emp.phone_number),
                ProcessedData.category == emp.report_responsibility
            ).first()
            
            if not submitted:
                # Employee missed the report
                group = db.query(Group).filter(Group.id == emp.group_id).first()
                report_friendly_name = emp.report_responsibility.replace('_', ' ').title()
                
                # 1. Send to Employee directly
                emp_phone = emp.phone_number
                if len(emp_phone) == 10 and emp_phone.isdigit():
                    emp_phone = "91" + emp_phone
                    
                emp_msg = f"⏰ *Reminder from Farm Auto*\nHi {emp.name},\nYou have missed submitting the *{report_friendly_name}* report today. Please submit it to the group as soon as possible!"
                send_waha_message(emp_phone + "@c.us", emp_msg)
                
                # 2. Send to Group
                if group:
                    grp_msg = f"⚠️ *Missed Report Alert*\nEmployee *{emp.name}* has not yet submitted the *{report_friendly_name}* report for today."
                    send_waha_message(group.whatsapp_group_id, grp_msg)
    except Exception as e:
        logger.error(f"Error in targeted reminder job: {e}")
    finally:
        db.close()

# Global state to prevent alert spamming
alert_state = {"is_alerted": False}

async def health_monitor_job():
    logger.info("Running WAHA Health Monitor...")
    primary_session = settings.WAHA_SESSION
    status = get_session_status(primary_session)
    
    # If the session is disconnected or scanning
    if status in ("STOPPED", "FAILED", "SCAN_QR_CODE"):
        if not alert_state["is_alerted"]:
            logger.warning(f"Primary WAHA Session '{primary_session}' is {status}! Fetching QR...")
            qr_path = get_session_qr(primary_session)
            
            admin_phone = "917259510983@c.us"
            alert_msg = f"🚨 *URGENT ALERT*\nYour Primary Farm Auto Bot (Session: {primary_session}) is currently logged out (Status: {status}).\n\nPlease scan the QR code below from your primary phone to reconnect!"
            
            # Send message using the 'backup' session
            send_waha_message(admin_phone, alert_msg, session="backup")
            if qr_path:
                send_waha_file(admin_phone, qr_path, caption="Scan this QR code to login", session="backup")
                
            alert_state["is_alerted"] = True
    else:
        # If it recovers, reset the alert state
        if alert_state["is_alerted"] and status == "WORKING":
            logger.info(f"Primary WAHA Session '{primary_session}' is back online!")
            admin_phone = "917259510983@c.us"
            recovery_msg = f"✅ *RECOVERY ALERT*\nYour Primary Farm Auto Bot is back online and working perfectly!"
            send_waha_message(admin_phone, recovery_msg, session="backup")
            alert_state["is_alerted"] = False

def _check_if_report_submitted(db, alarm, today) -> bool:
    report_type = alarm.report_type
    if not report_type:
        return False
        
    sender_phone = None
    group_name = None
    
    if alarm.target_type == 'employee':
        emp = db.query(Employee).filter(Employee.id == alarm.target_id).first()
        if emp:
            sender_phone = emp.phone_number
    elif alarm.target_type == 'group':
        if alarm.target_id:
            grp = db.query(Group).filter(Group.id == alarm.target_id).first()
            if grp:
                group_name = grp.name
        elif alarm.whatsapp_target_id:
            grp = db.query(Group).filter(Group.whatsapp_group_id == alarm.whatsapp_target_id).first()
            if grp:
                group_name = grp.name
                
    # Determine categories
    r_lower = report_type.lower()
    categories = []
    if "production" in r_lower:
        categories = ['production', 'egg_collection', 'egg_collection_1', 'egg_collection_2', 'egg']
    elif "feed" in r_lower:
        categories = ['feed']
    elif "expense" in r_lower:
        categories = ['expense', 'purchase']
    elif "sale" in r_lower:
        categories = ['sales']
    elif "profit" in r_lower or "p&l" in r_lower or "p and l" in r_lower:
        categories = ['sales', 'expense', 'purchase']
        
    # Check ProcessedData
    proc_query = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == today)
    if sender_phone:
        proc_query = proc_query.filter(ProcessedData.sender.contains(sender_phone))
    if group_name:
        proc_query = proc_query.filter(ProcessedData.group_name == group_name)
        
    if categories:
        if proc_query.filter(ProcessedData.category.in_(categories)).first():
            return True
    else:
        # Custom report types match inside notes (processed) or raw message text
        if proc_query.filter(ProcessedData.notes.ilike(f"%{report_type}%")).first():
            return True
            
        raw_query = db.query(RawMessage).filter(func.date(RawMessage.timestamp) == today)
        if sender_phone:
            raw_query = raw_query.filter(RawMessage.sender.contains(sender_phone))
        if group_name:
            raw_query = raw_query.filter(RawMessage.group_name == group_name)
            
        if raw_query.filter(RawMessage.raw_text.ilike(f"%{report_type}%")).first():
            return True
            
    return False

def execute_custom_alarm(alarm_id: int):
    db = SessionLocal()
    try:
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.now(IST).date()
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if not alarm or alarm.status != 'pending':
            return
            
        # Check if the report has already been submitted today
        if alarm.report_type:
            if _check_if_report_submitted(db, alarm, today):
                logger.info(f"Custom Alarm {alarm_id}: Report '{alarm.report_type}' already submitted today. Skipping WhatsApp reminder.")
                if alarm.frequency in ('once', 'timer') or not alarm.frequency:
                    alarm.status = 'sent'
                
                # Remove active nagging job if it exists
                nag_job_id = f"custom_alarm_{alarm_id}_nag"
                try:
                    scheduler.remove_job(nag_job_id)
                except Exception:
                    pass
                    
                db.commit()
                return
            
        target_whatsapp_id = None
        target_name = "Member"
        if alarm.target_type == 'employee':
            emp = db.query(Employee).filter(Employee.id == alarm.target_id).first()
            if emp:
                target_whatsapp_id = f"{emp.phone_number}@c.us"
                target_name = emp.name
        elif alarm.target_type == 'group':
            if alarm.target_id:
                grp = db.query(Group).filter(Group.id == alarm.target_id).first()
                if grp:
                    target_whatsapp_id = grp.whatsapp_group_id
                    target_name = grp.name
            elif alarm.whatsapp_target_id:
                target_whatsapp_id = alarm.whatsapp_target_id
                target_name = "Group"
                
        if target_whatsapp_id:
            if alarm.report_type:
                msg = f"⏰ *Reminder from Farm Auto*\nHi {target_name},\nYou have forgotten to send the *{alarm.report_type}* report today."
                if alarm.task_notes:
                    msg += f"\n\nNotes: {alarm.task_notes}"
            else:
                msg = f"🔔 *Custom Alarm / Task Reminder*\n\n{alarm.task_notes}"
                
            send_waha_message(target_whatsapp_id, msg)
            
        if alarm.frequency in ('once', 'timer') or not alarm.frequency:
            alarm.status = 'sent'
            
        # Schedule next nagging reminder if report is assigned and repeat_interval is set
        if alarm.report_type and alarm.repeat_interval and alarm.repeat_interval != 'none':
            nag_minutes = 0
            if alarm.repeat_interval == '5m': nag_minutes = 5
            elif alarm.repeat_interval == '10m': nag_minutes = 10
            elif alarm.repeat_interval == '15m': nag_minutes = 15
            elif alarm.repeat_interval == '30m': nag_minutes = 30
            elif alarm.repeat_interval == '1h': nag_minutes = 60
            
            if nag_minutes > 0:
                now_ist = datetime.now(IST)
                # Nag between 6 AM and 11 PM IST only
                if now_ist.hour < 23 and now_ist.hour >= 6:
                    next_nag_time = now_ist + timedelta(minutes=nag_minutes)
                    nag_job_id = f"custom_alarm_{alarm_id}_nag"
                    scheduler.add_job(
                        execute_custom_alarm,
                        DateTrigger(run_date=next_nag_time, timezone="Asia/Kolkata"),
                        args=[alarm_id],
                        id=nag_job_id,
                        replace_existing=True,
                        misfire_grace_time=None
                    )
                    logger.info(f"Scheduled nagging reminder for custom alarm {alarm_id} at {next_nag_time} (every {alarm.repeat_interval})")
                else:
                    logger.info(f"Custom Alarm {alarm_id}: Late night reached (11 PM - 6 AM). Stopping nagging reminders for today.")
                    
        db.commit()
    except Exception as e:
        logger.error(f"Error executing custom alarm {alarm_id}: {e}")
    finally:
        db.close()

def schedule_custom_alarm(alarm_id: int, trigger_time):
    global scheduler
    db = SessionLocal()
    try:
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if not alarm:
            return
            
        job_id = f"custom_alarm_{alarm_id}"
        freq = alarm.frequency or 'once'
        
        if freq == 'once':
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_5m':
            trigger = IntervalTrigger(minutes=5, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_10m':
            trigger = IntervalTrigger(minutes=10, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_15m':
            trigger = IntervalTrigger(minutes=15, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_30m':
            trigger = IntervalTrigger(minutes=30, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_1h':
            trigger = IntervalTrigger(hours=1, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'daily':
            trigger = CronTrigger(hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'weekly':
            # trigger_time.weekday() returns 0 (Mon) - 6 (Sun)
            trigger = CronTrigger(day_of_week=trigger_time.weekday(), hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'monthly':
            trigger = CronTrigger(day=trigger_time.day, hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'yearly':
            trigger = CronTrigger(month=trigger_time.month, day=trigger_time.day, hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'timer':
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        else:
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        scheduler.add_job(
            execute_custom_alarm,
            trigger,
            args=[alarm_id],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=None
        )
    except Exception as e:
        logger.error(f"Error scheduling custom alarm {alarm_id}: {e}")
    finally:
        db.close()

def get_next_occurrence(base_time, frequency):
    from datetime import timedelta, datetime
    next_time = base_time
    from datetime import timezone
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    while next_time <= now_ist:
        if frequency == 'weekly':
            next_time += timedelta(days=7)
        elif frequency == 'monthly':
            import calendar
            month = next_time.month - 1 + 1
            year = next_time.year + month // 12
            month = month % 12 + 1
            day = min(next_time.day, calendar.monthrange(year, month)[1])
            next_time = next_time.replace(year=year, month=month, day=day)
        elif frequency == 'yearly':
            try:
                next_time = next_time.replace(year=next_time.year + 1)
            except ValueError:
                next_time += timedelta(days=365)
        else:
            next_time += timedelta(days=1)
    return next_time

def format_report_list(reports):
    if not reports:
        return ""
    cleaned = []
    for r in reports:
        rl = r.lower()
        if "production" in rl:
            cleaned.append("production")
        elif "feed" in rl:
            cleaned.append("feed")
        elif "expense" in rl or "expenditure" in rl:
            cleaned.append("expense")
        elif "sale" in rl:
            cleaned.append("sales")
        elif "profit" in rl or "p&l" in rl or "p and l" in rl:
            cleaned.append("Profit & Loss")
        else:
            cleaned.append(r)
            
    if len(cleaned) == 1:
        return cleaned[0]
    elif len(cleaned) == 2:
        return f"{cleaned[0]} & {cleaned[1]}"
    else:
        return ", ".join(cleaned[:-1]) + f" & {cleaned[-1]}"

def format_name_list(names):
    if not names:
        return ""
    bold_names = [f"*{n}*" for n in names]
    if len(bold_names) == 1:
        return bold_names[0]
    elif len(bold_names) == 2:
        return f"{bold_names[0]} & {bold_names[1]}"
    else:
        return ", ".join(bold_names[:-1]) + f" & {bold_names[-1]}"

def poll_and_execute_unified_reminders():
    logger.info("Polling database for pending unified reminders...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    today = now_ist.date()
    
    db = SessionLocal()
    try:
        # Auto-reset sent recurring reminders back to pending once their next trigger time is reached
        db.query(UnifiedReminder).filter(
            UnifiedReminder.status == 'sent',
            UnifiedReminder.frequency != 'once',
            UnifiedReminder.trigger_time <= now_ist
        ).update({"status": "pending"})
        db.commit()

        pending = db.query(UnifiedReminder).filter(
            UnifiedReminder.status == 'pending',
            UnifiedReminder.trigger_time <= now_ist
        ).all()
        
        if not pending:
            return
            
        submissions = db.query(ProcessedData).filter(
            func.date(ProcessedData.processed_time) == today
        ).all()
        
        groups = db.query(Group).all()
        group_names_by_id = {g.whatsapp_group_id: g.name for g in groups}
        
        for r in pending:
            phones = [p.strip() for p in str(r.person_phone or '').split(',') if p.strip()]
            names = [n.strip() for n in str(r.person_name or '').split(',') if n.strip()]
            
            # Map of phone -> name
            assignees = {}
            for idx, phone in enumerate(phones):
                name = names[idx] if idx < len(names) else phone
                assignees[phone] = name
                
            assigned_reports = [s.strip().lower() for s in str(r.report_types or '').split(',') if s.strip()]
            
            pending_assignees = []
            
            # Check submissions for each assignee individually
            for phone, name in assignees.items():
                # Clean phone number by keeping only digits
                clean_phone = "".join(c for c in phone if c.isdigit())
                if clean_phone.startswith("0"):
                    clean_phone = clean_phone[1:]
                
                if len(clean_phone) == 10:
                    target_jid = "91" + clean_phone
                else:
                    target_jid = clean_phone
                    
                if not target_jid.endswith('@c.us') and not target_jid.endswith('@g.us') and not target_jid.endswith('@lid'):
                    target_jid += '@c.us'
                
                missing_reports = []
                for report in assigned_reports:
                    submitted = False
                    categories = []
                    if "production" in report:
                        categories = ['production', 'egg_collection', 'egg_collection_1', 'egg_collection_2', 'egg']
                    elif "feed" in report:
                        categories = ['feed']
                    elif "expense" in report or "expenditure" in report:
                        categories = ['expense', 'purchase']
                    elif "sale" in report:
                        categories = ['sales']
                    elif "profit" in report or "p&l" in report or "p and l" in report:
                        categories = ['sales', 'expense', 'purchase']
                        
                    for sub in submissions:
                        match_sender = phone in str(sub.sender)
                        group_name = group_names_by_id.get(r.whatsapp_group_id)
                        match_group = r.whatsapp_group_id and group_name and sub.group_name and str(sub.group_name).lower() == group_name.lower()
                        
                        if match_sender or match_group:
                            if categories:
                                if sub.category in categories:
                                    submitted = True
                                    break
                            else:
                                if report in str(sub.notes).lower():
                                    submitted = True
                                    break
                    if not submitted:
                        missing_reports.append(report)
                
                if not assigned_reports or missing_reports:
                    pending_assignees.append({
                        "name": name,
                        "phone": phone,
                        "jid": target_jid,
                        "missing_reports": missing_reports
                    })
                    
            if pending_assignees:
                # 1. Send private reminder to each pending assignee
                for p in pending_assignees:
                    if not assigned_reports:
                        private_body = r.task_notes
                    else:
                        missing_str = format_report_list(p['missing_reports'])
                        private_body = f"Please submit today's *{missing_str}* Report so the daily records and reports can be completed accurately."
                    
                    private_msg = (
                        "⏰Sunfra Farms Reminder\n\n"
                        f"Hi *{p['name']}*,\n\n"
                        f"{private_body}\n\n"
                        "Thank you! 🌱"
                    )
                    
                    logger.info(f"Sending private reminder to {p['name']} ({p['jid']})")
                    send_waha_message(p['jid'], private_msg)
                
                # 2. Send single group reminder mentioning all pending assignees
                if r.whatsapp_group_id:
                    name_tags = format_name_list([p['name'] for p in pending_assignees])
                    jids = [p['jid'] for p in pending_assignees]
                    
                    if not assigned_reports:
                        group_body = r.task_notes
                    else:
                        all_missing = sorted(list(set([rep for p in pending_assignees for rep in p['missing_reports']])))
                        missing_str = format_report_list(all_missing)
                        group_body = f"Please submit today's *{missing_str}* Report so the daily records and reports can be completed accurately."
                        
                    group_msg = (
                        "⏰Sunfra Farms Reminder\n\n"
                        f"Hi {name_tags},\n\n"
                        f"{group_body}\n\n"
                        "Thank you! 🌱"
                    )
                        
                    logger.info(f"Sending combined group reminder to {r.whatsapp_group_id} for {', '.join([p['name'] for p in pending_assignees])}")
                    send_waha_message(r.whatsapp_group_id, group_msg, mentions=jids)
                    
                repeat = str(r.repeat_interval).lower()
                if repeat != 'none' and repeat != '':
                    minutes = 0
                    if repeat == '5m': minutes = 5
                    elif repeat == '10m': minutes = 10
                    elif repeat == '15m': minutes = 15
                    elif repeat == '30m': minutes = 30
                    elif repeat == '1h': minutes = 60
                    
                    if minutes > 0 and now_ist.hour >= 6 and now_ist.hour < 23:
                        r.trigger_time = now_ist + timedelta(minutes=minutes)
                        db.commit()
                        logger.info(f"Nagging reminder scheduled for {r.person_name} in {minutes} mins.")
                        continue
                        
            freq = str(r.frequency).lower()
            if freq == 'once':
                r.status = 'sent'
            else:
                r.trigger_time = get_next_occurrence(r.trigger_time, freq)
                r.status = 'sent'  # Set status to sent so it displays as green (complete for today) in UI
            db.commit()
            logger.info(f"Reminder for {r.person_name} updated to next occurrence: {r.trigger_time} (status: sent)")
            
    except Exception as e:
        logger.error(f"Error in poll_and_execute_unified_reminders: {e}")
    finally:
        db.close()

def sync_custom_alarms_job():
    db = SessionLocal()
    try:
        pending_alarms = db.query(CustomAlarm).filter(CustomAlarm.status == 'pending').all()
        for alarm in pending_alarms:
            job_id = f"custom_alarm_{alarm.id}"
            if not scheduler.get_job(job_id):
                logger.info(f"Dynamically scheduling custom alarm {alarm.id} (frequency: {alarm.frequency}) for {alarm.trigger_time}")
                schedule_custom_alarm(alarm.id, alarm.trigger_time)
    except Exception as e:
        logger.error(f"Error in sync_custom_alarms_job: {e}")
    finally:
        db.close()

async def cleanup_old_files_job():
    logger.info("Starting media and report directory cleanup...")
    import os
    import time
    now = time.time()
    cutoff_time = now - (2 * 24 * 3600)  # 2 days ago
    
    # Clean /app/media/ for files older than 2 days
    media_dir = "/app/media"
    if os.path.exists(media_dir):
        for item in os.listdir(media_dir):
            item_path = os.path.join(media_dir, item)
            if os.path.isfile(item_path):
                # Don't delete QR session images or persistent keys
                if item.startswith("qr_") or item == "keys.json":
                    continue
                try:
                    if os.path.getmtime(item_path) < cutoff_time:
                        os.remove(item_path)
                except Exception as e:
                    logger.error(f"Error removing old media file {item_path}: {e}")
                    
    # Clean /app/media/reports for files older than 7 days
    reports_dir = "/app/media/reports"
    cutoff_reports = now - (7 * 24 * 3600)  # 7 days ago
    if os.path.exists(reports_dir):
        for item in os.listdir(reports_dir):
            item_path = os.path.join(reports_dir, item)
            if os.path.isfile(item_path):
                try:
                    if os.path.getmtime(item_path) < cutoff_reports:
                        os.remove(item_path)
                except Exception as e:
                    logger.error(f"Error removing old report file {item_path}: {e}")

def sync_groups_to_live():
    logger.info("Syncing local WAHA groups to live server...")
    try:
        import os
        import requests
        waha_url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/groups"
        headers = {"Accept": "application/json"}
        api_key = os.getenv("WAHA_API_KEY", "123")
        if api_key: headers["X-Api-Key"] = api_key
        
        response = requests.get(waha_url, headers=headers, timeout=10)
        if response.status_code == 200:
            groups = []
            data = response.json()
            if isinstance(data, list):
                for g in data:
                    groups.append({"id": g.get("id"), "name": g.get("subject") or g.get("name")})
            elif isinstance(data, dict):
                for k, v in data.items():
                    groups.append({"id": k, "name": v.get("subject") or v.get("name")})
            
            payload = {"status": "success", "groups": groups}
            sync_resp = requests.post("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=waha/groups/sync", json=payload, timeout=10)
            if sync_resp.status_code == 200:
                logger.info(f"Successfully synced {len(groups)} groups to live server.")
            else:
                logger.error(f"Failed to sync groups to live server. Status: {sync_resp.status_code}")
        else:
            logger.error(f"Failed to fetch groups from local WAHA. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error syncing groups: {e}")

def poll_live_alarms():
    logger.info("Polling live server for pending alarms...")
    try:
        import requests
        response = requests.get("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=bridge/alarms", timeout=10)
        if response.status_code == 200:
            alarms = response.json()
            
            from datetime import timezone, timedelta
            IST = timezone(timedelta(hours=5, minutes=30))
            now_ist = datetime.now(IST).replace(tzinfo=None)
            
            pending_found = False
            for alarm in alarms:
                if alarm.get('status') == 'pending':
                    pending_found = True
                    trigger_time = datetime.fromisoformat(alarm['trigger_time'])
                    
                    if trigger_time <= now_ist:
                        target_id = alarm.get('whatsapp_id')
                        notes = alarm.get('task_notes', '')
                        if target_id:
                            logger.info(f"Triggering live alarm {alarm['id']} to {target_id}")
                            msg = f"🔔 *Live Custom Alarm*\n\n{notes}"
                            send_waha_message(target_id, msg)
                            
                            # Mark as sent on live server
                            requests.post(f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=alarms/{alarm['id']}/trigger", timeout=10)
            if not pending_found:
                logger.debug("No pending live alarms found.")
    except Exception as e:
        logger.error(f"Error polling live server: {e}")

def setup_scheduler():
    global scheduler
    
    # Schedule Health Monitor every 5 minutes
    scheduler.add_job(health_monitor_job, CronTrigger(minute="*/5", timezone="Asia/Kolkata"), misfire_grace_time=300)
    
    # Schedule media/report cleanup daily at 12:05 AM IST
    scheduler.add_job(cleanup_old_files_job, CronTrigger(hour=0, minute=5, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule 6:00 PM data entry reminders everyday
    scheduler.add_job(scheduled_reminder_job, CronTrigger(hour=18, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule daily report at 10:00 PM IST everyday
    scheduler.add_job(scheduled_report_job, CronTrigger(hour=22, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule weekly report at 11:00 PM IST on Sunday
    scheduler.add_job(scheduled_weekly_report_job, CronTrigger(day_of_week='sun', hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule monthly report at 11:00 PM IST on the 1st day of every month
    scheduler.add_job(scheduled_monthly_report_job, CronTrigger(day='1', hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)

    # Schedule yearly report at 11:00 PM IST on Dec 31
    scheduler.add_job(scheduled_yearly_report_job, CronTrigger(month=12, day=31, hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    import os
    if os.getenv("USE_N8N", "false").lower() == "true":
        logger.info("USE_N8N is enabled. Live Alarms, Group Sync, and Unified Reminders are delegated to n8n.")
    else:
        # Schedule live alarms polling every 1 minute
        scheduler.add_job(poll_live_alarms, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
        # Schedule group syncing to live PHP server every 5 minutes
        scheduler.add_job(sync_groups_to_live, CronTrigger(minute="*/5", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
        # Schedule database polling for unified reminders every 1 minute
        scheduler.add_job(poll_and_execute_unified_reminders, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
    scheduler.start()
    logger.info("APScheduler started.")
