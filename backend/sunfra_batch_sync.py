import requests
import re
import json
import datetime
import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from models import Flock

logger = logging.getLogger("batch_sync")
logging.basicConfig(level=logging.INFO)

LOGIN_URL = "https://sunfra.com/farm/sunfra/login/login.php"
BATCH_URL = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

def sync_flocks_from_sunfra_web():
    """Logs into sunfra.com and syncs official hatch dates, live birds, running weeks, and batch IDs for all sheds."""
    logger.info("Starting live flock & hatch date sync from sunfra.com...")
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # Step 1: Login to sunfra.com
        session.get(LOGIN_URL, timeout=15)
        login_payload = {
            "username": "sunfra",
            "password": "Sunfra#321",
            "login": "Login"
        }
        res_post = session.post(LOGIN_URL, data=login_payload, timeout=15)
        if res_post.status_code != 200:
            logger.error(f"Login failed to sunfra.com, HTTP status: {res_post.status_code}")
            return False

        # Step 2: Fetch batch_json_to_web.php
        res_batch = session.get(BATCH_URL, timeout=15)
        if res_batch.status_code != 200:
            logger.error(f"Failed to fetch batch_json_to_web.php, HTTP status: {res_batch.status_code}")
            return False

        html_text = res_batch.text

        # Step 3: Parse shed cards from HTML
        card_matches = re.findall(r'<div[^>]*class=["\'][^"\']*shed-card[^"\']*["\'][^>]*>(.*?)</div>\s*</div>', html_text, re.DOTALL)
        if not card_matches:
            logger.error("No shed-card elements found in batch_json_to_web.php HTML.")
            return False

        db = SessionLocal()
        today = datetime.date.today()
        synced_count = 0

        for card in card_matches:
            clean_text = re.sub(r'<[^>]+>', ' ', card)
            clean_text = ' '.join(clean_text.split())

            # Example text: "Edit Chick 1 Total Live Birds: 27371 Running Weeks: 4 Weeks Batch IDs: 22 Hatch Date: 04 Jul, 2026 No. of Chicks: 27800"
            m_shed = re.search(r'(Chick\s*\d+|Grower\s*\d+|Shead\s*\d+|Shed\s*\d+)', clean_text, re.IGNORECASE)
            m_live = re.search(r'Total Live Birds:\s*(\d+)', clean_text, re.IGNORECASE)
            m_weeks = re.search(r'Running Weeks:\s*(\d+)', clean_text, re.IGNORECASE)
            m_batch = re.search(r'Batch IDs:\s*([^\s]+(?:\s+[^\s]+)*?)\s*Hatch Date', clean_text, re.IGNORECASE)
            m_hatch = re.search(r'Hatch Date:\s*([0-9]{1,2}\s+[A-Za-z]{3},\s+[0-9]{4})', clean_text, re.IGNORECASE)
            m_chicks = re.search(r'No\. of Chicks:\s*(\d+)', clean_text, re.IGNORECASE)

            if m_shed:
                shed_name = m_shed.group(1).strip()
                hatch_str = m_hatch.group(1).strip() if m_hatch else None
                live_birds = int(m_live.group(1)) if m_live else 0
                running_weeks = int(m_weeks.group(1)) if m_weeks else 0
                batch_id = m_batch.group(1).strip() if m_batch else None
                no_of_chicks = int(m_chicks.group(1)) if m_chicks else 0

                hatch_date = None
                age_days = 0
                if hatch_str:
                    try:
                        hatch_date = datetime.datetime.strptime(hatch_str, "%d %b, %Y").date()
                        age_days = (today - hatch_date).days + 1
                    except Exception as pe:
                        logger.error(f"Failed to parse hatch date '{hatch_str}': {pe}")

                status_str = 'active' if live_birds > 0 else 'inactive'

                # Upsert into sunfra_flocks table
                flock = db.query(Flock).filter(Flock.shed_name == shed_name).first()
                if not flock:
                    flock = Flock(
                        shed_name=shed_name,
                        hatch_date=hatch_date,
                        running_days=age_days,
                        running_weeks=running_weeks,
                        initial_chicks=no_of_chicks,
                        live_birds=live_birds,
                        batch_id=batch_id,
                        status=status_str
                    )
                    db.add(flock)
                else:
                    flock.hatch_date = hatch_date
                    flock.running_days = age_days
                    flock.running_weeks = running_weeks
                    flock.initial_chicks = no_of_chicks
                    flock.live_birds = live_birds
                    flock.batch_id = batch_id
                    flock.status = status_str

                synced_count += 1
                logger.info(f"Synced {shed_name}: Hatch Date = {hatch_date} (Age: Day {age_days}), Live Birds = {live_birds}, Weeks = {running_weeks}")

        db.commit()
        db.close()
        logger.info(f"Successfully synced {synced_count} sheds directly from sunfra.com batch_json_to_web.php!")
        return True

    except Exception as e:
        logger.error(f"Error in sync_flocks_from_sunfra_web: {e}")
        return False

if __name__ == "__main__":
    sync_flocks_from_sunfra_web()
