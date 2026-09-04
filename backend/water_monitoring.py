import os
import json
import logging
import pymysql
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

TARGET_GROUP_JID = "120363409544891824@g.us"
TARGET_PHONE = "917259510983@c.us"
STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), "water_monitoring_state.json")

IST = timezone(timedelta(hours=5, minutes=30))

DB_CONFIG = {
    'host': '145.223.17.70',
    'user': 'u632391467_kusumpakira',
    'password': 'Kusum@2026Bb!',
    'database': 'u632391467_kusumpakira',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 10
}

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
        conn = pymysql.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get latest reading per MAC for our water monitoring devices
        query = """
            SELECT r1.*
            FROM device_readings r1
            INNER JOIN (
                SELECT mac_address, MAX(id) AS max_id
                FROM device_readings
                WHERE mac_address IN ('C4-4F-33-24-7C-59', '40-91-51-C8-0C-C8')
                GROUP BY mac_address
            ) r2 ON r1.id = r2.max_id
        """
        cur.execute(query)
        devices = cur.fetchall()
        conn.close()
        
        if not devices:
            logger.warning("No water monitoring devices found in database.")
            return True

        state = load_monitoring_state()
        
        for dev in devices:
            mac = dev.get("mac_address")
            if not mac:
                continue
                
            # Standardize location names
            if mac == '40-91-51-C8-0C-C8':
                location = 'Kadubeesanahalli'
            elif mac == 'C4-4F-33-24-7C-59':
                location = 'Spice garden'
            else:
                location = dev.get("location") or "Unknown Location"
                
            name = "Level_sensor"
            water_level = int(dev.get("water_level", 0))
            status = str(dev.get("status") or "ON").upper()
            ts = dev.get("timestamp")
            
            if isinstance(ts, datetime):
                updated_dt = ts.replace(tzinfo=IST) if ts.tzinfo is None else ts.astimezone(IST)
            elif isinstance(ts, str):
                updated_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
            else:
                updated_dt = now_ist
                
            updated_at_str = updated_dt.strftime("%Y-%m-%d %H:%M:%S")
            diff_seconds = (now_ist - updated_dt).total_seconds()
            diff_hours = diff_seconds / 3600.0

            dev_state = state.setdefault(mac, {
                "last_low_alert_ts": 0,
                "low_active": False,
                "last_off_alert_ts": 0,
                "off_active": False
            })
            
            # ─── RULE 1: Water Level <= 25% Alert (Send STRICTLY ONCE to Group) ───
            if water_level <= 25:
                if not dev_state.get("low_active"):
                    alert_msg = (
                        f"⚠️ WATER LEVEL LOW ALERT!\n\n"
                        f"Location: {location}\n"
                        f"Device: {name} ({mac})\n"
                        f"Current Water Level: {water_level}% (CRITICAL ≤ 25%)\n"
                        f"Last Telemetry: {updated_at_str}"
                    )
                    logger.info(f"Sending Low Water Alert for {mac} ({location}) STRICTLY ONCE to Group ({TARGET_GROUP_JID})...")
                    sent = send_waha_message(TARGET_GROUP_JID, alert_msg)
                    if sent or True:
                        dev_state["low_active"] = True
                        dev_state["last_low_alert_ts"] = now_ts
            elif water_level >= 50:
                # Clear low water alert state silently when water reaches >= 50%
                dev_state["low_active"] = False
                dev_state["last_low_alert_ts"] = 0

            # ─── RULE 2: Device OFF / Disconnected Alert (Send STRICTLY ONCE to Group) ───
            is_off = (status == "OFF") or (diff_hours > 4.0)
            if is_off:
                if not dev_state.get("off_active"):
                    off_msg = (
                        f"🔴 DEVICE OFF / DISCONNECTED ALERT!\n\n"
                        f"Location: {location}\n"
                        f"Device: {name} ({mac})\n"
                        f"Status: DISCONNECTED / NO DATA FOR > 4 HOURS\n"
                        f"Last Telemetry: {updated_at_str}"
                    )
                    logger.info(f"Sending Device OFF Alert for {mac} ({location}) STRICTLY ONCE to Group ({TARGET_GROUP_JID})...")
                    sent = send_waha_message(TARGET_GROUP_JID, off_msg)
                    if sent or True:
                        dev_state["off_active"] = True
                        dev_state["last_off_alert_ts"] = now_ts
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
