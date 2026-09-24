import logging
import os
import re
import imaplib
import email
import json
from email.header import decode_header
from datetime import datetime, timezone, timedelta, date
from database import get_db_session
from models import PapaakEggRate
from config import settings
from waha_service import send_waha_message

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

GMAIL_EMAIL = os.getenv("PAPAAK_EMAIL", "kusum@sunfra.com")
GMAIL_APP_PASS = os.getenv("PAPAAK_APP_PASS", "kfgykqtorkchfkke")

# Standard City Order for Report
LOADING_CENTERS = ["HPT", "HYD", "NKL", "BWL", "KOL", "MYS"]
PAPER_CENTERS = ["CHE", "BLR", "HPT", "HYD", "NKL", "MYS", "BWL"]

FEED_COMMODITIES = [
    ("BAJ", ["DLH"]),
    ("MAZ", ["DLH"]),
    ("DMC", ["KOTA GOYAL", "KOTA SHIV"]),
    ("DRB", ["HRY", "PJB"]),
    ("GNE45", ["ROC"]),
    ("GNE40", ["ROC"]),
    ("GNE 50", ["ROC"]),
    ("SOY", ["DHULIYA", "INDORE", "KOTA GOYAL", "KOTA SHIV", "NADED", "NAGPUR", "SANGLI", "SOLAPUR"]),
    ("SOY HYP", ["KOTA"])
]

FALLBACK_FEED_BENCHMARKS = {
    "BAJ:DLH": 2400,
    "MAZ:DLH": 2550,
    "DMC:KOTA GOYAL": 2700,
    "DMC:KOTA SHIV": 2700,
    "DRB:HRY": 2140,
    "DRB:PJB": 2140,
    "GNE45:ROC": 3510,
    "GNE40:ROC": 3460,
    "GNE 50:ROC": 3760,
    "SOY:DHULIYA": 4600,
    "SOY:INDORE": 4670,
    "SOY:KOTA GOYAL": 4700,
    "SOY:KOTA SHIV": 4700,
    "SOY:NADED": 4720,
    "SOY:NAGPUR": 4620,
    "SOY:SANGLI": 4670,
    "SOY:SOLAPUR": 4700,
    "SOY HYP:KOTA": 5170,
}

COUNTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "papaak_report_counters.json")
FEED_COUNTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "papaak_feed_report_counters.json")


def get_next_report_number(date_key: str) -> int:
    """Gets and increments the sequential report counter for a specific date (YYYY-MM-DD)."""
    try:
        counters = {}
        if os.path.exists(COUNTER_FILE):
            try:
                with open(COUNTER_FILE, "r") as f:
                    counters = json.load(f)
            except Exception:
                counters = {}
        current = counters.get(date_key, 0) + 1
        counters[date_key] = current
        with open(COUNTER_FILE, "w") as f:
            json.dump(counters, f)
        return current
    except Exception as e:
        logger.error(f"Error getting report number: {e}")
        return 1


def get_current_report_number(date_key: str) -> int:
    """Gets the current report counter for a specific date without incrementing."""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                counters = json.load(f)
                return max(1, counters.get(date_key, 1))
    except Exception:
        pass
    return 1


def get_next_feed_report_number(date_key: str) -> int:
    """Gets and increments the sequential feed report counter for a specific date (YYYY-MM-DD)."""
    try:
        counters = {}
        if os.path.exists(FEED_COUNTER_FILE):
            try:
                with open(FEED_COUNTER_FILE, "r") as f:
                    counters = json.load(f)
            except Exception:
                counters = {}
        current = counters.get(date_key, 0) + 1
        counters[date_key] = current
        with open(FEED_COUNTER_FILE, "w") as f:
            json.dump(counters, f)
        return current
    except Exception as e:
        logger.error(f"Error getting feed report number: {e}")
        return 1


def get_current_feed_report_number(date_key: str) -> int:
    """Gets the current feed report counter for a specific date without incrementing."""
    try:
        if os.path.exists(FEED_COUNTER_FILE):
            with open(FEED_COUNTER_FILE, "r") as f:
                counters = json.load(f)
                return max(1, counters.get(date_key, 1))
    except Exception:
        pass
    return 1


FORWARDED_EMAILS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "forwarded_papaak_email_ids.json")

def get_forwarded_email_ids() -> set:
    try:
        if os.path.exists(FORWARDED_EMAILS_FILE):
            with open(FORWARDED_EMAILS_FILE, "r") as f:
                return set(json.load(f))
    except Exception:
        pass
    return set()

def mark_email_id_forwarded(msg_id: str):
    try:
        current = get_forwarded_email_ids()
        current.add(msg_id)
        with open(FORWARDED_EMAILS_FILE, "w") as f:
            json.dump(list(current), f)
    except Exception as e:
        logger.error(f"Error marking email id forwarded: {e}")


def parse_egg_email_text(email_text: str, msg_date: datetime):
    """
    Parses rates (Egg loading, Paper, and Feed / Raw material rates) from PAPAAK SMS email body text.
    Returns list of dicts: [{'city': 'HPT', 'rate': 510, 'category': 'loading'/'paper'/'feed', 'date': date_obj}]
    """
    if not email_text:
        return []
        
    text = str(email_text)
    text_upper = text.upper()

    # Must contain PAPAAK or rate/feed keywords
    if not any(k in text_upper for k in ["EGG", "PAPER RATE", "PPR RATE", "CLOSING", "VEH KOL", "PAPAAK", "SOY", "MAZ", "DRB", "BAJ", "FEED", "DMC", "GNE", "RAW"]):
        return []

    parsed_records = []
    lines = text.splitlines()
    
    # Paper rates received in the evening belong to the current day's report (email_date)
    # Even if email text says 'PAPER RATE FOR TOMORROW', it applies to today's daily cycle
    email_date = msg_date.date()
    paper_target_date = email_date
    is_evening = msg_date.hour >= 17

    # Process line by line
    is_entire_msg_paper = ("PAPER RATE FOR" in text_upper or "PPR RATE FOR" in text_upper)
    is_paper_section = is_entire_msg_paper
    is_closing_section = False
    is_feed_section = any(k in text_upper for k in ["SOY", "MAZ", "DRB", "BAJ", "GNE45", "DMC", "FEED", "RAW MATERIAL"])
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_upper = line_clean.upper()

        if "CLOSING" in line_upper:
            is_closing_section = True
            is_paper_section = False
            continue

        if ("PAPER RATE FOR" in line_upper or "PPR RATE FOR" in line_upper):
            is_paper_section = True
            is_closing_section = False
            continue

        if (line_upper.startswith("PAPER RATE") or line_upper.startswith("PPR RATE")):
            is_paper_section = True
            is_closing_section = False
            # check inline like PAPER RATE HYD 520 or PPR RATE BWL:540
            cleaned_line = line_upper.replace("PAPER RATE", "").replace("PPR RATE", "")
            matches_inline = list(re.finditer(r'\b([A-Z\(\)]+)\s*[:\s]\s*(\d{3})\b', cleaned_line))
            if matches_inline:
                for m_inline in matches_inline:
                    city = m_inline.group(1).strip()
                    rate = int(m_inline.group(2))
                    parsed_records.append({
                        "city": city,
                        "rate": rate,
                        "category": "paper",
                        "date": paper_target_date
                    })
            continue

        # If a new time-based Egg loading rate announcement starts, e.g. "11:15 Egg" or "8:02 Egg"
        if re.search(r'\b\d{1,2}:\d{2}\s*EGG\b', line_upper) or line_upper == "EGG":
            if not is_entire_msg_paper:
                is_paper_section = False
                is_closing_section = False
            continue

        # 1. Match Feed/Raw Material pattern e.g. "SOY-3850", "MAZ:1950", "DRB-1200", "BAJ 1800", "SOY HYP-3900", "GNE45-2100", "DMC-1500"
        feed_match = re.search(r'\b(SOY\s*HYP|SOY|MAZ|DRB|BAJ|GNE45|DMC|FEED|RAW\s*MAT)\s*[:\-\s]\s*(\d{3,6})\b', line_upper)
        if feed_match:
            item_code = feed_match.group(1).replace(" ", "_").strip()
            rate = int(feed_match.group(2))
            parsed_records.append({
                "city": item_code,
                "rate": rate,
                "category": "feed",
                "date": email_date
            })
            continue

        # 2. Match Egg Rate pattern CITY:RATE (supports multiple per line, e.g. "HPT:500 HYD:510")
        matches = re.finditer(r'\b([A-Z\(\)]+)\s*[:\s]\s*(\d{3})\b', line_upper)
        for match in matches:
            city = match.group(1).strip()
            rate = int(match.group(2))
            
            # Categorize rate
            if is_paper_section:
                cat = "paper"
                rec_date = paper_target_date
            elif is_closing_section:
                cat = "loading" if city in LOADING_CENTERS else ("paper" if is_evening and city in PAPER_CENTERS else "loading")
                rec_date = email_date
            elif is_feed_section and city not in LOADING_CENTERS and city not in PAPER_CENTERS:
                cat = "feed"
                rec_date = email_date
            else:
                cat = "loading" if city in LOADING_CENTERS else ("paper" if is_evening and city in PAPER_CENTERS else "loading")
                rec_date = email_date

            parsed_records.append({
                "city": city,
                "rate": rate,
                "category": cat,
                "date": rec_date
            })

    # Fallback: If no structured rate lines matched, but email is from PAPAAK, create generic record to track and forward
    if not parsed_records and len(text.strip()) > 5:
        parsed_records.append({
            "city": "PAPAAK_RAW",
            "rate": 0,
            "category": "feed" if is_feed_section else "loading",
            "date": email_date
        })

    return parsed_records


def parse_feed_email_text(email_text: str, msg_date: datetime):
    """
    Parses Feed / Raw Material rates from PAPAAK SMS email body text.
    Handles multi-line commodity blocks such as:
    BAJ-
    DLH:2400
    MAZ-
    DLH:2550
    DMC-
    KOTA GOYAL:2700
    ...
    Returns list of dicts: [{'city': 'BAJ:DLH', 'commodity': 'BAJ', 'center': 'DLH', 'rate': 2400, 'category': 'feed', 'date': date_obj}]
    """
    if not email_text:
        return []
    text = str(email_text)
    text_upper = text.upper()

    email_date = msg_date.date()
    parsed_records = []
    lines = text.splitlines()

    current_commodity = None

    commodity_patterns = [
        ("SOY HYP", r'^(?:SOY\s*HYP|SOY\s*HI\s*PRO)[-:\s]*$'),
        ("SOY", r'^(?:SOY|SOYA)[-:\s]*$'),
        ("BAJ", r'^(?:BAJ|BAJRA)[-:\s]*$'),
        ("MAZ", r'^(?:MAZ|MAIZE)[-:\s]*$'),
        ("DMC", r'^(?:DMC|MUSTARD\s*CAKE)[-:\s]*$'),
        ("DRB", r'^(?:DRB|RICE\s*BRAN)[-:\s]*$'),
        ("GNE45", r'^(?:GNE\s*45)[-:\s]*$'),
        ("GNE40", r'^(?:GNE\s*40)[-:\s]*$'),
        ("GNE 50", r'^(?:GNE\s*50)[-:\s]*$'),
        ("GNE", r'^(?:GNE)[-:\s]*$'),
    ]

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_upper = line_clean.upper()

        # Skip headers / footers
        if "PAPAAK" in line_upper or "FROM :" in line_upper or re.search(r'\b\d{1,2}:\d{2}\s*FEED\b', line_upper):
            continue

        # Check if line is a commodity section header
        matched_comm = False
        for comm_name, comm_regex in commodity_patterns:
            if re.match(comm_regex, line_upper):
                current_commodity = comm_name
                matched_comm = True
                break
        if matched_comm:
            continue

        # Match rate line e.g. "DLH:2400", "KOTA GOYAL:2700", "ROC:3510", "PJB:2140"
        m_rate = re.match(r'^([A-Z0-9\s\(\)\.]+)\s*[:\-]\s*(\d{3,6})$', line_upper)
        if m_rate and current_commodity:
            center = m_rate.group(1).strip()
            rate = int(m_rate.group(2))
            code = f"{current_commodity}:{center}"
            parsed_records.append({
                "commodity": current_commodity,
                "center": center,
                "city": code,
                "rate": rate,
                "category": "feed",
                "date": email_date
            })
            continue

        # Inline format fallback e.g. "SOY-DHULIYA:4600"
        m_inline = re.match(r'^(SOY\s*HYP|SOY|BAJ|MAZ|DMC|DRB|GNE\s*\d{2}|GNE)\s*[-:]\s*([A-Z0-9\s\(\)\.]+)\s*[:\-]\s*(\d{3,6})$', line_upper)
        if m_inline:
            comm = m_inline.group(1).strip()
            center = m_inline.group(2).strip()
            rate = int(m_inline.group(3))
            code = f"{comm}:{center}"
            parsed_records.append({
                "commodity": comm,
                "center": center,
                "city": code,
                "rate": rate,
                "category": "feed",
                "date": email_date
            })

    return parsed_records


def fetch_and_process_papaak_emails(notify_on_new: bool = True):
    """
    Connects to Gmail, fetches unread/recent emails from CP-PAPAAK-S, parses egg and feed rates,
    and stores them in sunfra_papaak_egg_rates table in MySQL.
    If new records are added and notify_on_new is True:
    1. Instantly dispatches raw incoming message text to 7259510983.
    2. If message contains egg loading/paper rates, instantly dispatches the formatted report (with sequential counter).
    """
    logger.info(f"Checking Gmail ({GMAIL_EMAIL}) for CP-PAPAAK-S egg & feed rate emails...")
    db = get_db_session()
    new_records_count = 0
    forwarded_ids = get_forwarded_email_ids()
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
        mail.select("inbox")

        # Search for messages containing CP-PAPAAK-S
        status, data = mail.search(None, 'TEXT "CP-PAPAAK-S"')
        if status != 'OK' or not data[0]:
            mail.logout()
            return 0

        mail_ids = data[0].split()
        # Fetch last 15 emails
        recent_ids = mail_ids[-15:]

        for m_id in recent_ids:
            _, msg_data = mail.fetch(m_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    sender = str(msg.get("from", ""))
                    # Extract Subject (handling MIME base64/UTF-8 encoded headers)
                    subject_raw = msg.get("subject", "")
                    subject = ""
                    if subject_raw:
                        try:
                            decoded_parts = decode_header(subject_raw)
                            for part, encoding in decoded_parts:
                                if isinstance(part, bytes):
                                    subject += part.decode(encoding or 'utf-8', errors='ignore')
                                else:
                                    subject += str(part)
                        except Exception:
                            subject = str(subject_raw)

                    # Extract body text first
                    body_text = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body_text = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                except Exception:
                                    pass
                    else:
                        try:
                            body_text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            pass

                    # Check if email is from PAPAAK (check sender, decoded subject, OR body text)
                    if "PAPAAK" not in sender.upper() and "PAPAAK" not in subject.upper() and "PAPAAK" not in body_text.upper():
                        continue

                    # Extract Date
                    date_header = msg.get("date")
                    msg_dt = datetime.now(IST)
                    if date_header:
                        try:
                            msg_dt = email.utils.parsedate_to_datetime(date_header).astimezone(IST)
                        except Exception:
                            pass

                    email_uid = msg.get("Message-ID") or f"{msg.get('date', '')}_{body_text[:50]}"
                    is_new_email = email_uid not in forwarded_ids

                    # Determine if Feed or Egg message
                    is_feed = "FEED" in body_text.upper() or any(k in body_text.upper() for k in ["SOY", "MAZ", "DRB", "BAJ", "GNE45", "DMC"])

                    # Parse records
                    if is_feed:
                        records = parse_feed_email_text(body_text, msg_dt)
                    else:
                        records = parse_egg_email_text(body_text, msg_dt)

                    has_egg_rates = False
                    has_feed_rates = False
                    msg_date_obj = msg_dt.date()

                    for r in records:
                        city = r["city"]
                        rate = r["rate"]
                        cat = r["category"]
                        r_date = r["date"]
                        msg_date_obj = r_date

                        if cat in ["loading", "paper"] and rate > 0:
                            has_egg_rates = True
                        if cat == "feed" and rate > 0:
                            has_feed_rates = True

                        # Check if this exact rate record already exists
                        if city == "PAPAAK_RAW":
                            existing = db.query(PapaakEggRate).filter(
                                PapaakEggRate.city_code == "PAPAAK_RAW",
                                PapaakEggRate.email_timestamp == msg_dt.replace(tzinfo=None)
                            ).first()
                        else:
                            existing = db.query(PapaakEggRate).filter(
                                PapaakEggRate.date == r_date,
                                PapaakEggRate.category == cat,
                                PapaakEggRate.city_code == city,
                                PapaakEggRate.rate_value == rate
                            ).first()

                        if not existing:
                            # Fetch previous recorded rate to calculate difference (+5, -10, 0)
                            prev_record = db.query(PapaakEggRate).filter(
                                PapaakEggRate.city_code == city,
                                PapaakEggRate.category == cat,
                                PapaakEggRate.date < r_date
                            ).order_by(PapaakEggRate.date.desc()).first()

                            prev_val = prev_record.rate_value if prev_record else rate
                            diff = rate - prev_val

                            new_rate = PapaakEggRate(
                                date=r_date,
                                email_timestamp=msg_dt.replace(tzinfo=None),
                                category=cat,
                                city_code=city,
                                rate_value=rate,
                                prev_rate_value=prev_val,
                                diff_value=diff,
                                raw_text=body_text[:500]
                            )
                            db.add(new_rate)
                            new_records_count += 1

                    if is_new_email and notify_on_new and len(body_text.strip()) > 5:
                        header = "🌾 *New PAPAAK Feed Rate Message*" if is_feed else "📩 *New PAPAAK Egg Rate Message*"
                        forward_msg = f"{header}\n\n{body_text.strip()}"

                        logger.info(f"Auto-forwarding PAPAAK email ({'FEED' if is_feed else 'EGG'}) to 917259510983@c.us...")
                        send_waha_message("917259510983@c.us", forward_msg)

                        # If message includes Egg Loading / Paper Rates, send formatted report with sequential number
                        if has_egg_rates:
                            today_date = msg_dt.date()
                            date_key = today_date.strftime("%Y-%m-%d")
                            rep_num = get_next_report_number(date_key)
                            report_msg = generate_daily_egg_rates_report(target_date=today_date, report_number=rep_num)
                            if report_msg:
                                logger.info(f"Auto-dispatching formatted report #{rep_num} to 917259510983@c.us...")
                                send_waha_message("917259510983@c.us", report_msg)

                        # If message includes Feed Rates, send formatted feed report with sequential number
                        if has_feed_rates:
                            today_date = msg_dt.date()
                            date_key = today_date.strftime("%Y-%m-%d")
                            rep_num = get_next_feed_report_number(date_key)
                            feed_report_msg = generate_daily_feed_rates_report(target_date=today_date, report_number=rep_num)
                            if feed_report_msg:
                                logger.info(f"Auto-dispatching formatted feed report #{rep_num} to 917259510983@c.us...")
                                send_waha_message("917259510983@c.us", feed_report_msg)

                        mark_email_id_forwarded(email_uid)
                        forwarded_ids.add(email_uid)

        db.commit()
        mail.logout()
        logger.info(f"Processed PAPAAK emails successfully. Added {new_records_count} new rate records.")

    except Exception as e:
        logger.error(f"Error fetching PAPAAK emails: {e}")
    finally:
        db.close()
        
    return new_records_count


def generate_daily_egg_rates_report(target_date=None, report_number: int = None) -> str:
    """
    Generates the formatted Egg Loading & Paper Rates report for target_date (always today's date).
    Header Format:
    📊 *DAILY EGG LOADING & PAPER RATES REPORT - 1*
    📅 *Date:* 22 Sep 2026
    """
    from datetime import datetime
    now_ist = datetime.now(IST)
    if not target_date:
        target_date = now_ist.date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    date_str = target_date.strftime("%d %b %Y")
    date_key = target_date.strftime("%Y-%m-%d")

    if report_number is None:
        report_number = get_current_report_number(date_key)

    db = get_db_session()
    
    try:
        # Fetch latest loading rates for target_date and compare against previous day
        loading_rates = {}
        paper_rates = {}

        # 1. Loading Rates (compared with yesterday's loading rates)
        for city in LOADING_CENTERS:
            r = db.query(PapaakEggRate).filter(
                PapaakEggRate.date <= target_date,
                PapaakEggRate.city_code == city,
                PapaakEggRate.category == "loading"
            ).order_by(PapaakEggRate.date.desc(), PapaakEggRate.id.desc()).first()

            if r:
                if r.date == target_date:
                    prev_record = db.query(PapaakEggRate).filter(
                        PapaakEggRate.date < target_date,
                        PapaakEggRate.city_code == city,
                        PapaakEggRate.category == "loading"
                    ).order_by(PapaakEggRate.date.desc(), PapaakEggRate.id.desc()).first()

                    if prev_record:
                        diff_val = r.rate_value - prev_record.rate_value
                    else:
                        diff_val = r.diff_value
                else:
                    diff_val = 0

                diff_str = f"(+{diff_val})" if diff_val > 0 else f"({diff_val})"
                loading_rates[city] = f"{r.rate_value}{diff_str}"
            else:
                defaults = {"HPT": "500(0)", "HYD": "510(0)", "NKL": "520(0)", "BWL": "558(0)", "KOL": "605(0)", "MYS": "610(0)"}
                loading_rates[city] = defaults.get(city, "500(0)")

        # 2. Paper Rates (compared with yesterday's paper rates)
        # User Directive: If morning, daytime or evening announces paper rate for a city (e.g. PAPER RATE HYD 520, PPR RATE BWL:540),
        # accept it immediately for that city and compute diff against yesterday's closing benchmark.
        # For cities without any paper rate announced today yet, show yesterday's closing benchmark with (0) in brackets.
        for city in PAPER_CENTERS:
            # Yesterday's closing benchmark paper rate
            yesterday_paper = db.query(PapaakEggRate).filter(
                PapaakEggRate.date < target_date,
                PapaakEggRate.city_code == city,
                PapaakEggRate.category == "paper"
            ).order_by(PapaakEggRate.date.desc(), PapaakEggRate.id.desc()).first()

            fallback_paper = {
                "CHE": 600,
                "BLR": 580,
                "HPT": 520,
                "HYD": 520,
                "NKL": 560,
                "MYS": 590,
                "BWL": 558
            }
            yesterday_rate = yesterday_paper.rate_value if yesterday_paper else fallback_paper.get(city, 540)

            # Check if this city has an announced paper rate today (morning, noon, or evening)
            today_paper = db.query(PapaakEggRate).filter(
                PapaakEggRate.date == target_date,
                PapaakEggRate.city_code == city,
                PapaakEggRate.category == "paper"
            ).order_by(PapaakEggRate.id.desc()).first()

            if today_paper:
                diff_val = today_paper.rate_value - yesterday_rate
                diff_str = f"(+{diff_val})" if diff_val > 0 else f"({diff_val})"
                paper_rates[city] = f"{today_paper.rate_value}{diff_str}"
            else:
                # Not yet announced today: keep yesterday's rate with (0)
                paper_rates[city] = f"{yesterday_rate}(0)"

        # Assemble formatted report message (Without 🥚 emoji)
        lines = [
            f"📊 *DAILY EGG LOADING & PAPER RATES REPORT - {report_number}*",
            f"📅 *Date:* {date_str}",
            "",
            "*Loading Rates*"
        ]

        for city in LOADING_CENTERS:
            lines.append(f"{city}: {loading_rates.get(city)}")

        lines.append("")
        lines.append("*Paper Rates*")
        for city in PAPER_CENTERS:
            lines.append(f"{city}: {paper_rates.get(city)}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Error generating PAPAAK egg rates report: {e}")
        return ""
    finally:
        db.close()


def send_daily_papaak_egg_rates_report(target_phone: str = "917259510983@c.us", fetch_first: bool = True):
    """
    Fetches latest emails and dispatches the daily report to target_phone (Kusum).
    """
    logger.info("Executing Egg Loading & Paper Rates Report Dispatcher...")
    try:
        # Fetch & parse any new incoming emails first if requested
        if fetch_first:
            fetch_and_process_papaak_emails(notify_on_new=False)
        
        # Generate formatted report
        report_msg = generate_daily_egg_rates_report()
        if report_msg:
            if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
                target_phone = f"{target_phone}@c.us"
                
            logger.info(f"Sending Daily Egg Loading & Paper Rates Report to {target_phone}...")
            send_waha_message(target_phone, report_msg)
    except Exception as e:
        logger.error(f"Error in send_daily_papaak_egg_rates_report: {e}")


def generate_daily_feed_rates_report(target_date=None, report_number: int = None) -> str:
    """
    Generates the formatted Feed Rates report for target_date compared with previous day.
    Header Format:
    🌾 *DAILY PAPAAK FEED RATES REPORT - 1*
    📅 *Date:* 23 Sep 2026
    """
    from datetime import datetime
    now_ist = datetime.now(IST)
    if not target_date:
        target_date = now_ist.date()
    elif isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    date_str = target_date.strftime("%d %b %Y")
    date_key = target_date.strftime("%Y-%m-%d")

    if report_number is None:
        report_number = get_current_feed_report_number(date_key)

    db = get_db_session()
    try:
        lines = [
            f"🌾 *DAILY PAPAAK FEED RATES REPORT - {report_number}*" if report_number else "🌾 *DAILY PAPAAK FEED RATES REPORT*",
            f"📅 *Date:* {date_str}",
            ""
        ]

        for comm, centers in FEED_COMMODITIES:
            lines.append(f"*{comm}*")
            for center in centers:
                code = f"{comm}:{center}"
                # Latest record on or before target_date
                today_rec = db.query(PapaakEggRate).filter(
                    PapaakEggRate.date <= target_date,
                    PapaakEggRate.city_code == code,
                    PapaakEggRate.category == "feed"
                ).order_by(PapaakEggRate.date.desc(), PapaakEggRate.id.desc()).first()

                # Previous benchmark record (yesterday or earlier)
                prev_rec = db.query(PapaakEggRate).filter(
                    PapaakEggRate.date < target_date,
                    PapaakEggRate.city_code == code,
                    PapaakEggRate.category == "feed"
                ).order_by(PapaakEggRate.date.desc(), PapaakEggRate.id.desc()).first()

                fallback_val = FALLBACK_FEED_BENCHMARKS.get(code, 2400)

                if today_rec and today_rec.date == target_date:
                    curr_val = today_rec.rate_value
                    prev_val = prev_rec.rate_value if prev_rec else fallback_val
                    diff_val = curr_val - prev_val
                    diff_str = f"(+{diff_val})" if diff_val > 0 else f"({diff_val})"
                    lines.append(f"{center}: {curr_val}{diff_str}")
                elif prev_rec:
                    lines.append(f"{center}: {prev_rec.rate_value}(0)")
                else:
                    lines.append(f"{center}: {fallback_val}(0)")
            lines.append("")

        return "\n".join(lines).strip()
    except Exception as e:
        logger.error(f"Error generating PAPAAK feed rates report: {e}")
        return ""
    finally:
        db.close()


def send_daily_papaak_feed_rates_report(target_phone: str = "917259510983@c.us", fetch_first: bool = False):
    """
    Generates and sends the daily feed report to target_phone.
    """
    logger.info("Executing Feed Rates Report Dispatcher...")
    try:
        if fetch_first:
            fetch_and_process_papaak_emails(notify_on_new=False)
        report_msg = generate_daily_feed_rates_report()
        if report_msg:
            if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
                target_phone = f"{target_phone}@c.us"
            logger.info(f"Sending Daily Feed Rates Report to {target_phone}...")
            send_waha_message(target_phone, report_msg)
    except Exception as e:
        logger.error(f"Error in send_daily_papaak_feed_rates_report: {e}")
