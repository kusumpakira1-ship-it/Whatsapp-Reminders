import os
import time
import requests
import logging
import sys
from datetime import datetime

# Python 3.9+ timezone handling, fallback to older datetime logic if missing
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from datetime import timezone, timedelta
# Ensure we can import from the app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from waha_service import send_waha_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LiveBridge')

LIVE_API_URL = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=bridge/alarms"
TRIGGER_API_URL = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=alarms/{}/trigger"
SYNC_GROUPS_URL = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=waha/groups/sync"

def sync_groups_to_live():
    logger.info("Syncing local WAHA groups to live server...")
    try:
        from config import settings
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
            sync_resp = requests.post(SYNC_GROUPS_URL, json=payload, timeout=10)
            if sync_resp.status_code == 200:
                logger.info(f"Successfully synced {len(groups)} groups to live server.")
            else:
                logger.error(f"Failed to sync groups to live server. Status: {sync_resp.status_code}")
        else:
            logger.error(f"Failed to fetch groups from local WAHA. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error syncing groups: {e}")

def get_current_ist_time():
    try:
        ist = ZoneInfo("Asia/Kolkata")
        return datetime.now(ist).replace(tzinfo=None)
    except NameError:
        # Fallback for Python < 3.9
        IST = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(IST).replace(tzinfo=None)

def poll_live_alarms():
    logger.info("Polling live server for pending alarms...")
    try:
        response = requests.get(LIVE_API_URL, timeout=10)
        if response.status_code == 200:
            alarms = response.json()
            now_ist = get_current_ist_time()
            
            pending_found = False
            for alarm in alarms:
                if alarm.get('status') == 'pending':
                    pending_found = True
                    # The trigger_time from PHP is like "2026-07-01T12:00:00"
                    trigger_time = datetime.fromisoformat(alarm['trigger_time'])
                    
                    if trigger_time <= now_ist:
                        target_id = alarm.get('whatsapp_id')
                        notes = alarm.get('task_notes', '')
                        if target_id:
                            logger.info(f"Triggering alarm {alarm['id']} to {target_id}")
                            
                            # Send WhatsApp message via local WAHA
                            msg = f"🔔 *Live Custom Alarm*\n\n{notes}"
                            send_waha_message(target_id, msg)
                            
                            # Mark as sent on live server
                            trigger_resp = requests.post(TRIGGER_API_URL.format(alarm['id']), timeout=10)
                            if trigger_resp.status_code == 200:
                                logger.info(f"Successfully marked alarm {alarm['id']} as sent on live server.")
                            else:
                                logger.error(f"Failed to mark alarm {alarm['id']} as sent. Status code: {trigger_resp.status_code}")
                        else:
                            logger.warning(f"Alarm {alarm['id']} has no whatsapp_id. Cannot send.")
            
            if not pending_found:
                logger.debug("No pending alarms found.")
        else:
            logger.error(f"Failed to fetch alarms. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error polling live server: {e}")

if __name__ == "__main__":
    logger.info("Starting live bridge polling service...")
    
    # Run an initial sync of groups when the script starts
    sync_groups_to_live()
    
    loops = 0
    while True:
        poll_live_alarms()
        time.sleep(60) # Poll every 60 seconds
        
        loops += 1
        # Sync groups every 5 minutes (5 loops)
        if loops % 5 == 0:
            sync_groups_to_live()
