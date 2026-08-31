import os
import json
import re
import logging
import requests
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

TARGET_GROUP_JID = "120363427898200198@g.us"
WATER_FLOW_FARM_URL = "https://sunfra.com/farm/sunfra/sensor/water_flow_for_farm.php"
STATE_FILE_PATH = os.path.join(os.path.dirname(__file__), "water_flow_farm_state.json")

IST = timezone(timedelta(hours=5, minutes=30))

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def load_farm_monitoring_state():
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading state file {STATE_FILE_PATH}: {e}")
    return {}

def save_farm_monitoring_state(state):
    try:
        with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing state file {STATE_FILE_PATH}: {e}")

def check_and_dispatch_water_flow_farm_alerts():
    """
    Monitors Water Flow & Indicator telemetry from https://sunfra.com/farm/sunfra/sensor/water_flow_for_farm.php.
    If no telemetry is received for >= 4 hours (14,400s), sends a Device OFF alert to 120363427898200198@g.us.
    """
    logger.info("Running Water Flow & Indicator Telemetry Check...")
    now_ist = datetime.now(IST)
    now_ts = now_ist.timestamp()

    try:
        resp = requests.get(WATER_FLOW_FARM_URL, headers=REQUEST_HEADERS, timeout=20)
        if resp.status_code != 200:
            logger.error(f"Water Flow Farm webpage returned HTTP {resp.status_code}")
            return False

        html = resp.text
        state = load_farm_monitoring_state()

        # 1. Parse Indicator Last Reading
        indicator_data = None
        ind_match = re.search(r'Indicator\s*Last\s*Reading.*?class="v"[^>]*>([\d\-:\s]+)<.*?MAC:\s*([A-F0-9\-]{17})', html, re.S | re.I)
        if ind_match:
            ind_ts_str = ind_match.group(1).strip()
            ind_mac = ind_match.group(2).strip()
            indicator_data = {"mac": ind_mac, "timestamp": ind_ts_str}

        # 2. Parse Water Flow Devices from Daily Breakdown Table
        water_devices = []
        rows = re.findall(r'<tr>\s*<td>.*?badge.*?>([\d\-:\s]+)<.*?<td>([A-F0-9\-]{17})</td>', html, re.S | re.I)
        for ts_str, mac_str in rows:
            water_devices.append({"mac": mac_str.strip(), "timestamp": ts_str.strip()})

        # Process Indicator Device
        if indicator_data:
            mac = indicator_data["mac"]
            ts_str = indicator_data["timestamp"]
            _evaluate_device_off_alert("indicator", mac, ts_str, now_ist, now_ts, state)

        # Process Water Flow Devices
        for dev in water_devices:
            mac = dev["mac"]
            ts_str = dev["timestamp"]
            _evaluate_device_off_alert("water_flow", mac, ts_str, now_ist, now_ts, state)

        save_farm_monitoring_state(state)
        return True
    except Exception as e:
        logger.error(f"Error in check_and_dispatch_water_flow_farm_alerts: {e}")
        return False

def _evaluate_device_off_alert(device_type, mac, ts_str, now_ist, now_ts, state):
    try:
        updated_dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
        diff_seconds = (now_ist - updated_dt).total_seconds()
        diff_hours = diff_seconds / 3600.0
    except Exception:
        diff_seconds = 999999
        diff_hours = 999.0

    dev_state = state.setdefault(mac, {
        "last_off_alert_ts": 0,
        "off_active": False
    })

    # Device OFF if no telemetry received for >= 4 hours (14,400 sec)
    if diff_hours >= 4.0:
        last_off_ts = dev_state.get("last_off_alert_ts", 0)
        # Send alert if never sent or 4 hours (14,400 sec) have passed since last alert
        if (now_ts - last_off_ts) >= 14400:
            if device_type == "indicator":
                msg = (
                    f"⚠️ *INDICATOR ALERT!*\n\n"
                    f"Location: Sunfra Farm\n"
                    f"Device: Level_sensor (`{mac}`)\n"
                    f"indicator device is OFF\n"
                    f"Last Telemetry: {ts_str}"
                )
            else:
                msg = (
                    f"⚠️ *WATER FLOW ALERT!*\n\n"
                    f"Location: Sunfra Farm\n"
                    f"Device: Level_sensor (`{mac}`)\n"
                    f"water flow device is OFF\n"
                    f"Last Telemetry: {ts_str}"
                )

            logger.info(f"Sending {device_type.upper()} OFF Alert for {mac} to {TARGET_GROUP_JID}...")
            sent = send_waha_message(TARGET_GROUP_JID, msg)
            if sent:
                dev_state["last_off_alert_ts"] = now_ts
                dev_state["off_active"] = True
    else:
        if dev_state.get("off_active"):
            logger.info(f"Device {mac} back online (last telemetry {ts_str}). Clearing OFF alert state.")
        dev_state["off_active"] = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_and_dispatch_water_flow_farm_alerts()
