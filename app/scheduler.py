import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from report_generator import generate_daily_reports, generate_custom_report
from waha_service import send_waha_message, send_waha_file, get_session_status, get_session_qr
from config import settings
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models import ReportRecipient, Group, Employee, ProcessedData, SystemSetting, CustomAlarm
from sqlalchemy import func

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def _send_reports_to_all(pdf_path, excel_path, summary_text):
    db = SessionLocal()
    recipients = db.query(ReportRecipient).filter(ReportRecipient.is_active == True).all()
    db.close()
    
    if not recipients:
        logger.warning("No active recipients found to send reports to.")
        return
        
    for r in recipients:
        phone = r.phone_number
        if summary_text:
            send_waha_message(phone, summary_text)
        if pdf_path:
            send_waha_file(phone, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")
        if excel_path:
            send_waha_file(phone, excel_path, caption=f"Excel Report - {excel_path.split('/')[-1]}")

async def scheduled_report_job():
    logger.info("Starting scheduled 11 PM daily report generation...")
    pdf_path, excel_path, summary_text = generate_daily_reports()
    await _send_reports_to_all(pdf_path, excel_path, summary_text)

async def scheduled_weekly_report_job():
    logger.info("Starting scheduled weekly report generation...")
    pdf_path, excel_path, summary_text = generate_custom_report('weekly')
    await _send_reports_to_all(pdf_path, excel_path, summary_text)

async def scheduled_monthly_report_job():
    logger.info("Starting scheduled monthly report generation...")
    pdf_path, excel_path, summary_text = generate_custom_report('monthly')
    await _send_reports_to_all(pdf_path, excel_path, summary_text)

async def scheduled_reminder_job():
    logger.info("Starting scheduled 6 PM data entry reminder...")
    db = SessionLocal()
    recipients = db.query(ReportRecipient).filter(ReportRecipient.is_active == True).all()
    db.close()
    
    if not recipients:
        return
        
    reminder_text = "⏰ *Friendly Reminder*\nPlease submit today's farm data (egg production, feed usage, sales, expenses) so your daily P&L report is accurate!"
    for r in recipients:
        send_waha_message(r.phone_number, reminder_text)

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

def setup_scheduler():
    global scheduler
    # Schedule general reminder at 11:00 PM IST (Requested)
    scheduler.add_job(scheduled_reminder_job, CronTrigger(hour=23, minute=0, timezone="Asia/Kolkata"))
    
    # Schedule targeted missed report reminder dynamically
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="targeted_reminder_time").first()
        reminder_time = setting.value if setting else "18:10"
        r_hour, r_minute = map(int, reminder_time.split(":"))
        
        # Schedule all pending custom alarms
        pending_alarms = db.query(CustomAlarm).filter(CustomAlarm.status == 'pending').all()
        for alarm in pending_alarms:
            schedule_custom_alarm(alarm.id, alarm.trigger_time)
    finally:
        db.close()
        
    scheduler.add_job(
        scheduled_targeted_reminder_job, 
        CronTrigger(hour=r_hour, minute=r_minute, timezone="Asia/Kolkata"),
        id='targeted_reminder_job',
        replace_existing=True
    )
    
    # Schedule sync custom alarms job every 10 seconds
    scheduler.add_job(sync_custom_alarms_job, CronTrigger(second="*/10", timezone="Asia/Kolkata"))
    
    # Schedule Health Monitor every 5 minutes
    scheduler.add_job(health_monitor_job, CronTrigger(minute="*/5", timezone="Asia/Kolkata"))
    
    # Schedule media/report cleanup daily at 12:05 AM IST
    scheduler.add_job(cleanup_old_files_job, CronTrigger(hour=0, minute=5, timezone="Asia/Kolkata"))
    
    # Schedule daily report at 11:00 PM IST everyday
    scheduler.add_job(scheduled_report_job, CronTrigger(hour=23, minute=0, timezone="Asia/Kolkata"))
    
    # Schedule weekly report at 11:00 PM IST on Sunday
    scheduler.add_job(scheduled_weekly_report_job, CronTrigger(day_of_week='sun', hour=23, minute=0, timezone="Asia/Kolkata"))
    
    # Schedule monthly report at 11:00 PM IST on the 1st day of every month
    scheduler.add_job(scheduled_monthly_report_job, CronTrigger(day='1', hour=23, minute=0, timezone="Asia/Kolkata"))
    
    scheduler.start()
    logger.info("APScheduler started. Daily, Weekly, Monthly reports, Targeted Reminders, and Cleanup jobs are scheduled.")
