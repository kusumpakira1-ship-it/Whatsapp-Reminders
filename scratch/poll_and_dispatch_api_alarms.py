import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import CustomAlarm
from waha_service import send_waha_message
from datetime import datetime, timezone, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))
logger.info("🚀 Starting Standalone API Reminder Dispatcher Background Loop...")

while True:
    try:
        db = SessionLocal()
        now_ist = datetime.now(IST).replace(tzinfo=None)
        
        pending_alarms = db.query(CustomAlarm).filter(
            CustomAlarm.status == 'pending',
            CustomAlarm.trigger_time <= now_ist
        ).all()

        if pending_alarms:
            logger.info(f"Found {len(pending_alarms)} pending API reminders ready to send!")

        for alarm in pending_alarms:
            target = alarm.whatsapp_target_id
            text = alarm.task_notes
            logger.info(f"Dispatching API Reminder ID {alarm.id} to {target}...")
            
            success = send_waha_message(target, text)
            if success:
                alarm.status = 'sent'
                db.commit()
                logger.info(f"API Reminder ID {alarm.id} SENT SUCCESSFULLY ✅")
            else:
                logger.error(f"API Reminder ID {alarm.id} DISPATCH FAILED ❌")

        db.close()
    except Exception as e:
        logger.error(f"Error in background API dispatcher loop: {e}")

    time.sleep(5)  # Poll every 5 seconds
