import os
import time
import logging
import requests
from datetime import datetime
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

# Target WhatsApp Group: Motor Alerts
MOTOR_ALERTS_GROUP_JID = "120363430182157972@g.us"
DEFAULT_TARGET_RECIPIENTS = [MOTOR_ALERTS_GROUP_JID]

VOLTAGE_SENSOR_LOGS_URL = "https://sunfra.com/farm/voltage_sensor/api.php?endpoint=voltage-logs"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*"
}

OFF_VOLTAGE_THRESHOLD = 80.0
MOTOR_ALERTS_ON_HOLD = True  # Set to False when ready to resume sending WhatsApp alerts


def get_latest_motor_telemetry():
    """Fetches real-time voltage sensor logs and returns the latest reading per motor."""
    try:
        response = requests.get(VOLTAGE_SENSOR_LOGS_URL, headers=REQUEST_HEADERS, timeout=20)
        if response.status_code != 200:
            logger.error(f"Failed to fetch voltage sensor logs: HTTP {response.status_code}")
            return []

        data = response.json()
        logs = data.get("logs", [])
        if not logs:
            logger.warning("No voltage sensor logs returned from API.")
            return []

        latest_by_motor = {}
        for log in logs:
            m_id = str(log.get("motorId", "")).strip()
            mac = str(log.get("macAddress", "")).strip().upper()
            if not m_id:
                continue
            # Exclude test/mock sensor records (e.g., Motor 1 Test / AA-BB-CC-DD-EE-FF)
            if "AA-BB" in mac or "TEST" in m_id.upper() or (m_id == "Motor 1" and mac.startswith("AA")):
                continue
            # Keep first occurrence as logs are ordered descending by timestamp
            if m_id not in latest_by_motor:
                latest_by_motor[m_id] = log

        motors = []
        for m_id, item in sorted(latest_by_motor.items(), key=lambda x: str(x[0])):
            try:
                volt = float(item.get("voltage", 0.0))
            except (ValueError, TypeError):
                volt = 0.0

            raw_status = str(item.get("status", "")).strip().upper()
            is_off = ("OFF" in raw_status) or (volt < OFF_VOLTAGE_THRESHOLD)

            ts_str = str(item.get("timestamp", "")).strip()
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                formatted_ts = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                formatted_ts = ts_str or "N/A"

            motors.append({
                "motor_id": m_id,
                "location": item.get("location") or "Farm Station",
                "mac_address": item.get("macAddress") or "N/A",
                "voltage": volt,
                "status": raw_status or ("POWER OFF" if is_off else "POWER ON"),
                "is_off": is_off,
                "last_telemetry": formatted_ts
            })

        return motors

    except Exception as e:
        logger.error(f"Error fetching latest motor telemetry: {e}")
        return []


def build_motor_off_alert_message(motor_data: dict) -> str:
    """Formats the Motor OFF alert according to the user's template."""
    return (
        "⚠️ *MOTOR OFF ALERT!*\n\n"
        f"*Location:* {motor_data.get('location', 'N/A')}\n"
        f"*MAC Address:* {motor_data.get('mac_address', 'N/A')}\n"
        f"*Motor ID:* {motor_data.get('motor_id', 'N/A')}\n"
        f"*Voltage:* {motor_data.get('voltage', 0.0):.1f}V\n"
        f"*Last Telemetry:* {motor_data.get('last_telemetry', 'N/A')}"
    )


def check_and_dispatch_motor_voltage_alerts(target_recipients=None):
    """Checks motor statuses every 30 mins and sends alerts to Motor Alerts group if any motor is OFF."""
    if MOTOR_ALERTS_ON_HOLD:
        logger.info("Motor Voltage & Power Status Alerts are currently ON HOLD. Skipping alert dispatch.")
        return True
    logger.info("Starting Motor Voltage & Power Status Check (30-Minute Cycle)...")
    if target_recipients is None:
        recipients = DEFAULT_TARGET_RECIPIENTS
    elif isinstance(target_recipients, str):
        recipients = [target_recipients]
    else:
        recipients = list(target_recipients)

    motors = get_latest_motor_telemetry()
    if not motors:
        logger.warning("No motor telemetry data available to check.")
        return False

    off_motors = [m for m in motors if m.get("is_off")]
    logger.info(f"Checked {len(motors)} motors: {len(off_motors)} currently OFF, {len(motors) - len(off_motors)} ON.")

    if not off_motors:
        logger.info("All motors are running normally (POWER ON). No alerts needed.")
        return True

    dispatched_count = 0
    for motor in off_motors:
        alert_msg = build_motor_off_alert_message(motor)
        for recipient in recipients:
            logger.info(f"Dispatching Motor OFF Alert for Motor {motor.get('motor_id')} to {recipient}...")
            try:
                res = send_waha_message(recipient, alert_msg)
                if res:
                    dispatched_count += 1
                else:
                    logger.warning(f"Failed to send Motor OFF Alert to {recipient}")
            except Exception as e:
                logger.error(f"Error sending Motor OFF Alert to {recipient}: {e}")
            time.sleep(1.5)  # Brief pause between messages

    logger.info(f"Motor voltage check complete. Sent {dispatched_count} alert message(s).")
    return dispatched_count > 0
