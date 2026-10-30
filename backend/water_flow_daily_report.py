import os
import re
import logging
import requests
from datetime import datetime, timezone, timedelta
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

# Recipient configurations
# Message 1 (Sunfra Farms): 7259510983 & Sunfra Group Of Companies
SUNFRA_FARMS_RECIPIENTS = [
    "917259510983@c.us",
    "120363410727174477@g.us"  # Sunfra Group Of Companies
]

# Message 2 (Spice Garden): 7259510983 & Balaji (9493928388)
SPICE_GARDEN_RECIPIENTS = [
    "917259510983@c.us",
    "919493928388@c.us"        # Balaji
]

TARGET_RECIPIENTS = list(dict.fromkeys(SUNFRA_FARMS_RECIPIENTS + SPICE_GARDEN_RECIPIENTS))

WATER_FLOW_FARM_URL = "https://sunfra.com/farm/sunfra/sensor/water_flow_for_farm.php"

IST = timezone(timedelta(hours=5, minutes=30))

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# MAC Address -> (Location Name, Sort Order, Category)
MAC_LOCATION_MAP = {
    # Sunfra Farms
    "04-BA-5F-0F-F0-A4": ("Chick Shed", 1, "Sunfra Farms"),
    "50-5C-F9-54-94-34": ("Shed 1", 2, "Sunfra Farms"),
    # Spice Garden
    "34-3B-80-1D-16-F0": ("Flavours Cafe", 3, "Spice Garden"),
    "A0-F4-66-7C-E5-A4": ("Flat 101", 4, "Spice Garden"),
    "5D-7E-24-33-4F-C4": ("Flat 102", 5, "Spice Garden"),
    "88-F6-64-A5-05-28": ("Flat 201", 6, "Spice Garden"),
    "F1-51-DC-2D-E6-B4": ("Flat 202", 7, "Spice Garden"),
    "68-14-5F-0F-F0-A4": ("Flat 301", 8, "Spice Garden"),
    "5C-26-14-C4-0A-24": ("Flat 302", 9, "Spice Garden"),
    "DC-7A-57-DF-94-8C": ("Flat 401", 10, "Spice Garden"),
    "B8-39-60-F5-76-30": ("Flat 402", 11, "Spice Garden"),
    "D8-3A-80-1D-16-F0": ("Flat 501", 12, "Spice Garden"),
    "94-FD-BA-3B-01-5C": ("Flat 502", 13, "Spice Garden")
}

def generate_water_flow_summary_by_category(target_date=None) -> dict:
    """
    Fetches water flow consumption data for a target date (defaults to today)
    and formats 2 separate WhatsApp summary reports:
    - 'Sunfra Farms': Message 1
    - 'Spice Garden': Message 2
    """
    if target_date is None:
        now_ist = datetime.now(IST)
        target_date = now_ist.date()

    date_str = target_date.strftime("%Y-%m-%d")
    formatted_date_str = target_date.strftime("%d %b %Y")

    url = f"{WATER_FLOW_FARM_URL}?mac_address=ALL&ppl=65&date={date_str}"
    logger.info(f"Fetching daily water flow report from {url}...")

    resp = requests.get(url, headers=REQUEST_HEADERS, timeout=20)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch water flow dashboard. HTTP {resp.status_code}")
        return {}

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

    farms_items = []
    spice_items = []
    for mac, (name, sort_order, category) in MAC_LOCATION_MAP.items():
        liters = fetched_data.get(mac, 0.0)
        mac_short = f"{mac[:2]}...{mac[-2:]}"
        item = (sort_order, mac_short, name, liters)
        if category == "Sunfra Farms":
            farms_items.append(item)
        else:
            spice_items.append(item)

    farms_items.sort(key=lambda x: x[0])
    spice_items.sort(key=lambda x: x[0])

    category_reports = {}

    # 1. Sunfra Farms message
    if farms_items:
        msg_farms = "💧 *Daily Water Flow Summary Report*\n"
        msg_farms += f"📅 *Date:* {formatted_date_str}\n"
        msg_farms += "────────────────────────\n"
        msg_farms += "📍 *Water Consumption Per Day*\n"
        msg_farms += "Sunfra Farms \n"
        for _, mac_short, name, liters in farms_items:
            msg_farms += f"• {mac_short} *{name}*: {int(round(liters)):,} Liters\n"
        category_reports["Sunfra Farms"] = msg_farms.strip()

    # 2. Spice Garden message
    if spice_items:
        msg_spice = "💧 *Daily Water Flow Summary Report*\n"
        msg_spice += f"📅 *Date:* {formatted_date_str}\n"
        msg_spice += "────────────────────────\n"
        msg_spice += "📍 *Water Consumption Per Day*\n"
        msg_spice += "Spice Garden \n"
        for _, mac_short, name, liters in spice_items:
            msg_spice += f"• {mac_short} *{name}*: {int(round(liters)):,} Liters\n"
        category_reports["Spice Garden"] = msg_spice.strip()

    return category_reports


def generate_water_flow_summary_messages(target_date=None) -> list:
    """Returns the list of generated reports."""
    reports = generate_water_flow_summary_by_category(target_date=target_date)
    msgs = []
    if "Sunfra Farms" in reports:
        msgs.append(reports["Sunfra Farms"])
    if "Spice Garden" in reports:
        msgs.append(reports["Spice Garden"])
    return msgs


def generate_water_flow_summary_message(target_date=None) -> str:
    """Returns both reports combined for backward compatibility."""
    msgs = generate_water_flow_summary_messages(target_date=target_date)
    return "\n\n".join(msgs) if msgs else None


def send_daily_water_flow_report_job(target_date=None, farms_recipients=None, spice_recipients=None):
    """
    Job executed daily at 11:58 PM IST:
    - Message 1 (Sunfra Farms) -> 917259510983@c.us & Sunfra Group Of Companies (120363410727174477@g.us)
    - Message 2 (Spice Garden) -> 917259510983@c.us & Balaji (919493928388@c.us)
    """
    import time

    if farms_recipients is None:
        farms_recipients = SUNFRA_FARMS_RECIPIENTS
    elif isinstance(farms_recipients, str):
        farms_recipients = [farms_recipients]

    if spice_recipients is None:
        spice_recipients = SPICE_GARDEN_RECIPIENTS
    elif isinstance(spice_recipients, str):
        spice_recipients = [spice_recipients]

    logger.info("Starting scheduled daily water flow summary report job (Sunfra Farms & Spice Garden routed separately)...")

    reports = None
    for attempt in range(3):
        try:
            reports = generate_water_flow_summary_by_category(target_date=target_date)
            if reports and (reports.get("Sunfra Farms") or reports.get("Spice Garden")):
                break
            logger.warning(f"Water flow report generation attempt {attempt+1} returned empty. Retrying in 5s...")
        except Exception as e:
            logger.error(f"Water flow report generation attempt {attempt+1} failed: {e}")
        time.sleep(5)

    if not reports:
        logger.error("Failed to generate water flow summary messages after 3 attempts.")
        return False

    success = False

    # 1. Send Sunfra Farms report
    farms_msg = reports.get("Sunfra Farms")
    if farms_msg:
        for recipient in farms_recipients:
            for attempt in range(3):
                logger.info(f"Sending Sunfra Farms water report to {recipient} (Attempt {attempt+1})...")
                res = send_waha_message(recipient, farms_msg)
                if res:
                    success = True
                    break
                time.sleep(3)
            time.sleep(1)

    # 2. Send Spice Garden report
    spice_msg = reports.get("Spice Garden")
    if spice_msg:
        for recipient in spice_recipients:
            for attempt in range(3):
                logger.info(f"Sending Spice Garden water report to {recipient} (Attempt {attempt+1})...")
                res = send_waha_message(recipient, spice_msg)
                if res:
                    success = True
                    break
                time.sleep(3)
            time.sleep(1)

    return success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_date = datetime.strptime("2026-10-03", "%Y-%m-%d").date()
    for m in generate_water_flow_summary_messages(target_date=test_date):
        print(m)
        print("="*30)
