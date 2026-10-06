import os
import re
import logging
import requests
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

TARGET_PHONE = "917259510983@c.us"
SUNFRA_GROUP_JID = "120363410727174477@g.us"  # Sunfra Group Of Companies

TARGET_RECIPIENTS = [
    TARGET_PHONE,
    SUNFRA_GROUP_JID
]

WATER_FLOW_FARM_URL = "https://sunfra.com/farm/sunfra/sensor/water_flow_for_farm.php"

IST = timezone(timedelta(hours=5, minutes=30))

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# MAC Address -> (Location Name, Sort Order)
MAC_LOCATION_MAP = {
    "04-BA-5F-0F-F0-A4": ("Chick Shed", 1),
    "50-5C-F9-54-94-34": ("Shed 1", 2),
    "34-3B-80-1D-16-F0": ("Flavours Cafe", 3),
    "A0-F4-66-7C-E5-A4": ("Flat 101", 4),
    "5D-7E-24-33-4F-C4": ("Flat 102", 5),
    "88-F6-64-A5-05-28": ("Flat 201", 6),
    "F1-51-DC-2D-E6-B4": ("Flat 202", 7),
    "68-14-5F-0F-F0-A4": ("Flat 301", 8),
    "5C-26-14-C4-0A-24": ("Flat 302", 9),
    "DC-7A-57-DF-94-8C": ("Flat 401", 10),
    "B8-39-60-F5-76-30": ("Flat 402", 11),
    "D8-3A-80-1D-16-F0": ("Flat 501", 12),
    "94-FD-BA-3B-01-5C": ("Flat 502", 13)
}

def generate_water_flow_summary_message(target_date=None) -> str:
    """
    Fetches water flow consumption data for a target date (defaults to yesterday)
    and formats a WhatsApp summary report.
    """
    if target_date is None:
        now_ist = datetime.now(IST)
        target_date = (now_ist - timedelta(days=1)).date()

    date_str = target_date.strftime("%Y-%m-%d")
    formatted_date_str = target_date.strftime("%d %b %Y")

    url = f"{WATER_FLOW_FARM_URL}?mac_address=ALL&ppl=65&date={date_str}"
    logger.info(f"Fetching daily water flow report from {url}...")

    resp = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch water flow dashboard. HTTP {resp.status_code}")
        return None

    html = resp.text
    rows = re.findall(r'<tr.*?>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)

    fetched_data = {}
    for rw in rows:
        cols = re.findall(r'<td.*?>(.*?)</td>', rw, re.DOTALL | re.IGNORECASE)
        clean_cols = [re.sub(r'<.*?>', '', c).strip() for c in cols]
        if len(clean_cols) >= 4:
            mac = clean_cols[1]
            liters_str = clean_cols[3]
            if mac in MAC_LOCATION_MAP:
                try:
                    liters = float(liters_str.replace(',', ''))
                except ValueError:
                    liters = 0.0
                fetched_data[mac] = liters

    items = []
    for mac, (name, sort_order) in MAC_LOCATION_MAP.items():
        liters = fetched_data.get(mac, 0.0)
        mac_short = f"{mac[:2]}...{mac[-2:]}"
        items.append((sort_order, mac_short, name, liters))

    items.sort(key=lambda x: x[0])

    if not items:
        logger.warning(f"No matching MAC address data found for date {date_str}")
        return None

    msg = "💧 *Daily Water Flow Summary Report*\n"
    msg += f"📅 *Date:* {formatted_date_str}\n"
    msg += "───────────────────────────\n"
    msg += "📍 *Water Consumption Per Day*\n"

    for _, mac_short, name, liters in items:
        msg += f"• {mac_short} *{name}*: {liters:,.2f} Liters\n"

    return msg

def send_daily_water_flow_report_job(target_date=None, phone_numbers=None):
    """Job executed daily at 12:05 AM IST."""
    if phone_numbers is None:
        phone_numbers = TARGET_RECIPIENTS
    elif isinstance(phone_numbers, str):
        phone_numbers = [phone_numbers]

    logger.info("Starting scheduled daily water flow summary report job...")
    try:
        msg = generate_water_flow_summary_message(target_date=target_date)
        if msg:
            for recipient in phone_numbers:
                logger.info(f"Sending daily water flow summary report to {recipient}...")
                send_waha_message(recipient, msg)
            return True
        else:
            logger.error("Failed to generate water flow summary message.")
            return False
    except Exception as e:
        logger.error(f"Error in send_daily_water_flow_report_job: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_date = datetime.strptime("2026-10-03", "%Y-%m-%d").date()
    print(generate_water_flow_summary_message(target_date=test_date))
