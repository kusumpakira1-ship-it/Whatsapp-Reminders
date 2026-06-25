import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.report_generator import generate_daily_reports
from services.waha_service import send_waha_message, send_waha_file
from db.database import SessionLocal
from db.models import ReportRecipient

logger = logging.getLogger(__name__)

async def scheduled_report_job():
    logger.info("Starting scheduled 11 PM report generation...")
    
    pdf_path, excel_path, summary_text = generate_daily_reports()
    
    db = SessionLocal()
    recipients = db.query(ReportRecipient).filter(ReportRecipient.is_active == True).all()
    db.close()
    
    if not recipients:
        logger.warning("No active recipients found to send reports to.")
        return
        
    for r in recipients:
        phone = r.phone_number
        # Send summary text
        send_waha_message(phone, summary_text)
        
        # Send files if generated
        if pdf_path:
            send_waha_file(phone, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")
        if excel_path:
            send_waha_file(phone, excel_path, caption=f"Excel Report - {excel_path.split('/')[-1]}")

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

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    # Schedule reminder at 11:00 PM IST (Requested)
    scheduler.add_job(scheduled_reminder_job, CronTrigger(hour=23, minute=0, timezone="Asia/Kolkata"))
    # Schedule report at 11:00 PM IST everyday
    scheduler.add_job(scheduled_report_job, CronTrigger(hour=23, minute=0, timezone="Asia/Kolkata"))
    scheduler.start()
    logger.info("APScheduler started. Reminder scheduled at 12:45 and Report at 23:00.")
