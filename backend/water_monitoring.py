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
        
        # 1. Fetch only devices registered on the website (mac_devices table)
        cur.execute("""
            SELECT id, mac_address, name, location, water_level, status, updated_at, created_at
            FROM mac_devices
            WHERE (
                LOWER(name) LIKE '%level%' 
                OR LOWER(name) LIKE '%sensor%' 
                OR LOWER(name) LIKE '%water%' 
                OR LOWER(location) LIKE '%tank%' 
                OR LOWER(location) LIKE '%water%'
            )
            AND LOWER(name) NOT LIKE '%scale%'
            AND water_level >= 0
            ORDER BY id ASC
        """)
        registered_devices = cur.fetchall()
        
        if not registered_devices:
            logger.warning("No registered water monitoring devices found on the website (mac_devices).")
            conn.close()
            return True

        registered_macs = [d['mac_address'].strip() for d in registered_devices if d.get('mac_address')]
        
        # 2. Get latest telemetry reading per registered MAC from device_readings
        latest_readings = {}
        if registered_macs:
            format_strings = ','.join(['%s'] * len(registered_macs))
            query = f"""
                SELECT r1.*
                FROM device_readings r1
                INNER JOIN (
                    SELECT mac_address, MAX(id) AS max_id
                    FROM device_readings
                    WHERE mac_address IN ({format_strings})
                    GROUP BY mac_address
                ) r2 ON r1.id = r2.max_id
            """
            cur.execute(query, tuple(registered_macs))
            for r in cur.fetchall():
                latest_readings[r['mac_address'].strip()] = r
        conn.close()

        state = load_monitoring_state()
        
        # Prune any devices that were removed from the website
        for mac_key in list(state.keys()):
            if mac_key not in registered_macs:
                del state[mac_key]

        for reg_dev in registered_devices:
            mac = reg_dev.get("mac_address", "").strip()
            if not mac:
                continue
                
            name = reg_dev.get("name") or "Level_sensor"
            location = reg_dev.get("location") or "Main Tank"
            
            read = latest_readings.get(mac)
            if read:
                water_level = int(read.get("water_level", 0))
                status = str(read.get("status") or "ON").upper()
                ts = read.get("timestamp") or reg_dev.get("updated_at")
                if read.get("location") and read.get("location") != "Main Tank":
                    location = read.get("location")
            else:
                water_level = int(reg_dev.get("water_level") if reg_dev.get("water_level") is not None else -1)
                status = str(reg_dev.get("status") or "OFF").upper()
                ts = reg_dev.get("updated_at") or reg_dev.get("created_at") or now_ist
            
            if isinstance(ts, datetime):
                updated_dt = ts.replace(tzinfo=IST) if ts.tzinfo is None else ts.astimezone(IST)
            elif isinstance(ts, str):
                try:
                    updated_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
                except Exception:
                    updated_dt = now_ist
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
            
            # ─── RULE 1: Water Level 0% to 25% Alert (Recurring every 30 mins until >= 50%) ───
            if 0 <= water_level <= 25:
                last_low_ts = dev_state.get("last_low_alert_ts", 0)
                # Send alert if never sent or 30 minutes (1,800 sec) have passed since last alert
                if (now_ts - last_low_ts) >= 1800:
                    alert_msg = (
                        f"⚠️ WATER LEVEL LOW ALERT!\n\n"
                        f"Location: {location}\n"
                        f"Device: {name} ({mac})\n"
                        f"Current Water Level: {water_level}% (CRITICAL ≤ 25%)\n"
                        f"Last Telemetry: {updated_at_str}"
                    )
                    logger.info(f"Sending Low Water Alert for {mac} ({location}) (every 30 mins) to Group ({TARGET_GROUP_JID})...")
                    sent = send_waha_message(TARGET_GROUP_JID, alert_msg)
                    if sent or True:
                        dev_state["low_active"] = True
                        dev_state["last_low_alert_ts"] = now_ts
            elif water_level >= 50:
                # Clear low water alert state silently when water reaches >= 50%
                dev_state["low_active"] = False
                dev_state["last_low_alert_ts"] = 0

            # ─── RULE 2: Device OFF / Disconnected Alert (Data not updated for > 4 Hours) ───
            is_off = (status == "OFF") or (diff_hours > 4.0)
            if is_off:
                last_off_ts = dev_state.get("last_off_alert_ts", 0)
                # Send alert once when device goes off, and repeat every 4 hours if still OFF
                if not dev_state.get("off_active") or (now_ts - last_off_ts) >= 14400:
                    off_msg = (
                        f"🔴 DEVICE OFF / DISCONNECTED ALERT!\n\n"
                        f"Location: {location}\n"
                        f"Device: {name} ({mac})\n"
                        f"Status: DISCONNECTED / NO DATA FOR > 4 HOURS\n"
                        f"Last Telemetry: {updated_at_str}"
                    )
                    logger.info(f"Sending Device OFF Alert for {mac} ({location}) to Group ({TARGET_GROUP_JID})...")
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
