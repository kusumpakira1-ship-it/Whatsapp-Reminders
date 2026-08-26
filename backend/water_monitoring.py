import os
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

TARGET_GROUP_JID = "120363409544891824@g.us"
TELEMETRY_API_URL = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=get_devices"
STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), "water_monitoring_state.json")

IST = timezone(timedelta(hours=5, minutes=30))

def load_monitoring_state():
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading state file {STATE_FILE_PATH}: {e}")
    return {}

def save_monitoring_state(state):
    try:
        with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing state file {STATE_FILE_PATH}: {e}")

def check_and_dispatch_water_alerts():
    logger.info("Running Water Level & Device OFF Telemetry Monitoring Check...")
    now_ist = datetime.now(IST)
    now_ts = now_ist.timestamp()
    
    try:
        resp = requests.get(TELEMETRY_API_URL, timeout=15)
        if resp.status_code != 200:
            logger.error(f"Telemetry API returned HTTP {resp.status_code}")
            return False
        
        data = resp.json()
        if not data.get("success"):
            logger.error(f"Telemetry API error response: {data}")
            return False

        devices = data.get("devices", [])
        state = load_monitoring_state()
        
        for dev in devices:
            mac = dev.get("mac_address")
            if not mac:
                continue
                
            name = dev.get("name", "Level_sensor")
            location = dev.get("location", "Unknown Location")
            water_level = int(dev.get("water_level", 0))
            status = str(dev.get("status", "ON")).upper()
            updated_at_str = dev.get("updated_at", "")
            
            # Parse updated_at timestamp
            try:
                updated_dt = datetime.strptime(updated_at_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
                diff_seconds = (now_ist - updated_dt).total_seconds()
                diff_hours = diff_seconds / 3600.0
            except Exception:
                diff_seconds = 999999
                diff_hours = 999.0
            
            dev_state = state.setdefault(mac, {
                "last_low_alert_ts": 0,
                "low_active": False,
                "last_off_alert_ts": 0,
                "off_active": False
            })
            
            # ─── RULE 1: Water Level <= 25% Alert (Repeat every 30 mins until >= 50%) ───
            if water_level <= 25:
                last_low_ts = dev_state.get("last_low_alert_ts", 0)
                # Send alert if never sent or 30 minutes (1800 sec) have passed
                if (now_ts - last_low_ts) >= 1800:
                    alert_msg = (
                        f"⚠️ *WATER LEVEL LOW ALERT!*\n\n"
                        f"*Location:* {location}\n"
                        f"*Device:* {name} (`{mac}`)\n"
                        f"*Current Water Level:* *{water_level}%* (CRITICAL ≤ 25%)\n"
                        f"*Last Telemetry:* {updated_at_str}"
                    )
                    logger.info(f"Sending Low Water Alert for {mac} to {TARGET_GROUP_JID}...")
                    sent = send_waha_message(TARGET_GROUP_JID, alert_msg)
                    if sent:
                        dev_state["last_low_alert_ts"] = now_ts
                        dev_state["low_active"] = True
            elif water_level >= 50:
                # Reset low water active state silently when water reaches >= 50%
                dev_state["low_active"] = False
                dev_state["last_low_alert_ts"] = 0

            # ─── RULE 2: Device OFF Alert (Data > 4 hours old or status == OFF) ───
            is_off = (status == "OFF") or (diff_hours > 4.0)
            if is_off:
                last_off_ts = dev_state.get("last_off_alert_ts", 0)
                # Send OFF alert if never sent or 4 hours (14400 sec) have passed
                if (now_ts - last_off_ts) >= 14400:
                    off_reason = "Status reported OFF" if status == "OFF" else f"No data received for {diff_hours:.1f} hours (> 4 hrs)"
                    off_msg = (
                        f"🔴 *DEVICE OFF / OFFLINE ALERT!* ⚠️\n"
                        f"📍 *Location:* {location}\n"
                        f"💻 *Device:* {name} (`{mac}`)\n"
                        f"⚠️ *Reason:* {off_reason}\n"
                        f"📅 *Last Telemetry:* {updated_at_str}\n"
                        f"⚡ *Power Status:* Device is OFF / Disconnected"
                    )
                    logger.info(f"Sending Device OFF Alert for {mac} to {TARGET_GROUP_JID}...")
                    sent = send_waha_message(TARGET_GROUP_JID, off_msg)
                    if sent:
                        dev_state["last_off_alert_ts"] = now_ts
                        dev_state["off_active"] = True
            else:
                if dev_state.get("off_active"):
                    logger.info(f"Device {mac} back online. Clearing OFF alert state.")
                dev_state["off_active"] = False
                dev_state["last_off_alert_ts"] = 0

        save_monitoring_state(state)
        return True
    except Exception as e:
        logger.error(f"Error in check_and_dispatch_water_alerts: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_and_dispatch_water_alerts()
