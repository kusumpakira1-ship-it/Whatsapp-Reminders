import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from report_generator import generate_daily_reports, generate_custom_report
from waha_service import send_waha_message, send_waha_file, get_session_status, get_session_qr
from config import settings
from apscheduler.triggers.date import DateTrigger
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

def execute_custom_alarm(alarm_id: int):
    db = SessionLocal()
    try:
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if not alarm or alarm.status != 'pending':
            return
            
        target_whatsapp_id = None
        if alarm.target_type == 'employee':
            emp = db.query(Employee).filter(Employee.id == alarm.target_id).first()
            if emp:
                target_whatsapp_id = f"{emp.phone_number}@c.us"
        elif alarm.target_type == 'group':
            grp = db.query(Group).filter(Group.id == alarm.target_id).first()
            if grp:
                target_whatsapp_id = grp.whatsapp_group_id
                
        if target_whatsapp_id:
            msg = f"🔔 *Custom Alarm / Task Reminder*\n\n{alarm.task_notes}"
            send_waha_message(target_whatsapp_id, msg)
            
        alarm.status = 'sent'
        db.commit()
    except Exception as e:
        logger.error(f"Error executing custom alarm {alarm_id}: {e}")
    finally:
        db.close()

def schedule_custom_alarm(alarm_id: int, trigger_time):
    global scheduler
    job_id = f"custom_alarm_{alarm_id}"
    scheduler.add_job(
        execute_custom_alarm,
        DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata"),
        args=[alarm_id],
        id=job_id,
        replace_existing=True
    )

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
