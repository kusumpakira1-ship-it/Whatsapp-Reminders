import re
import os
import sqlite3
import logging
from datetime import datetime, date, timedelta, timezone
from database import get_db_session
from models import SecondFeedRate
from waha_service import send_waha_message

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# Destination groups requested by the user
FEED_RATES_GROUP_JID = "120363411665097967@g.us"           # Feed Rates
EGG_RATES_FORECAST_GROUP_JID = "120363411797923836@g.us"   # Egg Rates & Weather Forecast

def get_feed_messages_for_date(target_date: date) -> list:
    """Fetch all second_feed_rates records for a given date from MySQL or SQLite fallback."""
    date_str = target_date.strftime("%Y-%m-%d")
    rows = []
    
    # 1. Primary DB (MySQL)
    db = get_db_session()
    try:
        recs = db.query(SecondFeedRate).filter(
            SecondFeedRate.timestamp >= f"{date_str} 00:00:00",
            SecondFeedRate.timestamp <= f"{date_str} 23:59:59"
        ).order_by(SecondFeedRate.id.asc()).all()
        for r in recs:
            rows.append((r.id, r.timestamp, r.raw_text))
    except Exception as e:
        logger.warning(f"Error querying MySQL for feed rates on {date_str}: {e}")
    finally:
        db.close()

    # 2. Fallback to SQLite if MySQL returned empty
    if not rows:
        try:
            sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_reminders.sqlite")
            if os.path.exists(sqlite_path):
                conn = sqlite3.connect(sqlite_path)
                cur = conn.cursor()
                rows = cur.execute(
                    "SELECT id, timestamp, raw_text FROM second_feed_rates WHERE timestamp >= ? AND timestamp <= ? ORDER BY id ASC",
                    (f"{date_str} 00:00:00", f"{date_str} 23:59:59")
                ).fetchall()
                conn.close()
        except Exception as sqle:
            logger.warning(f"Error querying SQLite for feed rates on {date_str}: {sqle}")

    return rows

def find_latest_available_feed_date(start_date: date) -> date:
    """Finds the most recent date on or before start_date that has feed rates data."""
    curr = start_date
    for _ in range(7):
        rows = get_feed_messages_for_date(curr)
        if rows:
            return curr
        curr -= timedelta(days=1)
    return start_date

CANONICAL_ALIASES = {
    # KA Maize
    "bengalure": ("ka_maize", "Bengaluru"),
    "bengaluru": ("ka_maize", "Bengaluru"),
    "dabaspet": ("ka_maize", "Dabaspet"),
    "budehal": ("ka_maize", "Budehal"),
    "peenya": ("ka_maize", "Peenya"),
    "sugun": ("ka_maize", "Suguna"),
    "sugun h": ("ka_maize", "Suguna"),
    "sugana hoskote": ("ka_maize", "Suguna Hoskote"),
    "abhis": ("ka_maize", "Abhis"),
    "abis": ("ka_maize", "Abhis"),
    "sneha": ("ka_maize", "Sneha"),
    "hoskote": ("ka_maize", "Hoskote (Credit)"),
    "godrej": ("ka_maize", "Godrej Godawan"),
    "godrej godawan": ("ka_maize", "Godrej Godawan"),
    "c mangalur": ("ka_maize", "C Mangaluru"),
    "c mangaluru": ("ka_maize", "C Mangaluru"),
    "c mangalore": ("ka_maize", "C Mangaluru"),
    "najangudu": ("ka_maize", "Nanjangudu"),
    "nanjangudu": ("ka_maize", "Nanjangudu"),
    "nanjangud": ("ka_maize", "Nanjangudu"),
    "mysore": ("ka_maize", "Mysore"),
    "mangalore": ("ka_maize", "Mangalore"),
    "hebari": ("ka_maize", "Hebbari"),
    "hebbari": ("ka_maize", "Hebbari"),
    "ranebennur": ("ka_maize", "Ranebennur"),
    "ranebenur": ("ka_maize", "Ranebennur"),
    "haveri rack": ("ka_maize", "Haveri Rack"),
    "haveri kargil": ("ka_maize", "Haveri Kargil"),
    "haveri": ("ka_maize", "Haveri"),
    "koppal": ("ka_maize", "Koppal"),
    "bagalakote": ("ka_maize", "Bagalkote"),
    "bagalkot": ("ka_maize", "Bagalkote"),
    "bgk": ("ka_maize", "Bagalkote"),
    "chikballapura": ("ka_maize", "Chikkaballapura"),
    "chikkaballapura": ("ka_maize", "Chikkaballapura"),
    "kolar": ("ka_maize", "Kolar"),
    "tumakur": ("ka_maize", "Tumakuru"),
    "tumakuru": ("ka_maize", "Tumakuru"),
    "davangere": ("ka_maize", "Davangere"),
    "vhl rnr": ("ka_maize", "VHL RNR"),
    "vhl  rnr": ("ka_maize", "VHL RNR"),
    "vhl hubli": ("ka_maize", "VHL Hubli"),
    "bgm": ("ka_maize", "Belgaum (BGM)"),
    "belgaum": ("ka_maize", "Belgaum (BGM)"),
    "sankeshwar": ("ka_maize", "Sankeshwar"),
    "ambuja": ("ka_maize", "Ambuja"),
    "gokak": ("ka_maize", "Gokak"),
    "kokak": ("ka_maize", "Gokak"),
    "sahyadri": ("ka_maize", "Sahyadri"),
    "shayadri": ("ka_maize", "Sahyadri"),
    "sangali": ("ka_maize", "Sangli"),
    "sangli": ("ka_maize", "Sangli"),
    "snagali": ("ka_maize", "Sangli"),
    "baramati": ("ka_maize", "Baramati"),
    "satara": ("ka_maize", "Satara"),
    "asha": ("ka_maize", "Asha"),
    "yaran": ("ka_maize", "Yaran"),
    "kunigal": ("ka_maize", "KCE Feeds Kunigal"),
    "kce feeds kunigal": ("ka_maize", "KCE Feeds Kunigal"),
    "ac kuligal feeds": ("ka_maize", "KCE Feeds Kunigal"),
    "ksk wh": ("ka_maize", "KSK WH"),
    "t begur": ("ka_maize", "T Begur"),
    "rg kasat bgk": ("ka_maize", "RG Kasat Bagalkote"),

    # TN / AP Maize
    "namakal": ("tn_maize", "Namakkal"),
    "namakkal": ("tn_maize", "Namakkal"),
    "namaal": ("tn_maize", "Namakkal"),
    "shanti": ("tn_maize", "Shanti (TN)"),
    "shantil": ("tn_maize", "Shanti (TN)"),
    "skm": ("tn_maize", "SKM Erode"),
    "skm erode": ("tn_maize", "SKM Erode"),
    "baramasagar": ("tn_maize", "Baramasagar"),
    "srs": ("tn_maize", "SRS"),
    "srs japanese": ("tn_maize", "SRS Japanese"),
    "paladam": ("tn_maize", "Palladam"),
    "palladam": ("tn_maize", "Palladam"),
    "annur": ("tn_maize", "Annur"),
    "tn annur": ("tn_maize", "Annur"),
    "tanjaure": ("tn_maize", "Thanjavur"),
    "thanjavur": ("tn_maize", "Thanjavur"),
    "hosur": ("tn_maize", "Hosur"),
    "mbs": ("tn_maize", "MBS"),
    "punanoor": ("tn_maize", "Punanoor (AP)"),
    "punanoor ap": ("tn_maize", "Punanoor (AP)"),
    "hyd": ("tn_maize", "Hyderabad"),
    "hyderabad": ("tn_maize", "Hyderabad"),
    "rohini hyd": ("tn_maize", "Rohini Hyd"),
    "udamalpet": ("tn_maize", "Udamalpet"),
    "krish": ("tn_maize", "Krish Nutrition"),
    "krish nutrition": ("tn_maize", "Krish Nutrition"),
    "chetoore": ("tn_maize", "CP Chittoor"),
    "cp chetoore": ("tn_maize", "CP Chittoor"),
    "chittur": ("tn_maize", "CP Chittoor"),
    "cp chittur": ("tn_maize", "CP Chittoor"),
    "cp cittur": ("tn_maize", "CP Chittoor"),
    "cp chittoor": ("tn_maize", "CP Chittoor"),
    "tirupati": ("tn_maize", "Tirupati Godavari"),
    "tirupati godavari": ("tn_maize", "Tirupati Godavari"),
    "kuppam": ("tn_maize", "Baramati Agro Kuppam"),
    "pollachi": ("tn_maize", "Baramati Agro Pollachi"),
    "gadag": ("ka_maize", "Baramati Agro Gadag"),
    "ramnagar": ("ka_maize", "Baramati Agro Ramnagar"),

    # Kirti Soya
    "solapur": ("kirti_soya", "Solapur"),
    "latur": ("kirti_soya", "Latur"),
    "nanded": ("kirti_soya", "Nanded"),
    "hingoli": ("kirti_soya", "Hingoli"),
    "karjol": ("kirti_soya", "Karjol"),
    "bijapur": ("kirti_soya", "Bijapur"),
    "vijayapura": ("kirti_soya", "Bijapur"),
    "bidar": ("kirti_soya", "Bidar"),
    "gulbarga": ("kirti_soya", "Gulbarga"),
    "bailhongal": ("kirti_soya", "Bailhongal"),
}

IGNORE_PHRASES = [
    "ananthlaxmi", "anathalaxmi", "news hubli", "contact", "phone", "conatact",
    "payment", "terms", "delivery", "broiler report", "poultry market", "doc report",
    "dorb", "paddy", "wxdadelivery", "whatsapp", "nutrifeeds and farms"
]

def clean_place_name(raw: str) -> str:
    """Cleans a raw place or processor name by stripping symbols, tags, and terms."""
    s = re.sub(r'[\*\=\:\,\.\(\)]', ' ', raw)
    s = re.sub(r'\b(?:\d+days|\+gst|\+tax|\-20|\-30|\-50|rs|pmt|nb)\b', ' ', s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_line_rate(line: str):
    """Extracts (rate, candidate_name) from any rate line."""
    line_clean = line.strip()
    if not line_clean:
        return None
    
    # Skip if line has 00 or NB (no booking / zero rate)
    if re.search(r'^\*?\s*00+\s+', line_clean) or re.search(r'\b(?:00|nb)\b', line_clean, re.I):
        return None
    
    # 1. PMT format: e.g. "KSK WH Rs. 33250 PMT" -> 3325
    m_pmt = re.search(r'([A-Za-z\s\.\(\)\-\&]+?)\s+(?:Rs\.?\s*)?(\d{5})\s*pmt', line_clean, re.I)
    if m_pmt:
        cand = clean_place_name(m_pmt.group(1))
        rate = int(m_pmt.group(2)) // 10
        if cand and len(cand) >= 2:
            return rate, cand

    # 2. Rate first: e.g. "3350 BENGALURE", "3200/3300 SANGALI", "*3370 SKM ERODE -20*", "7800 RADHA KRISHNA"
    m_rate_first = re.match(r'^\*?\s*(\d{4})(?:/\d{4})?\s+([A-Za-z0-9\s\.\(\)\-\&\/\+]+?)\*?$', line_clean)
    if m_rate_first:
        rate = int(m_rate_first.group(1))
        cand = clean_place_name(m_rate_first.group(2))
        if cand and len(cand) >= 2:
            return rate, cand

    # 3. Place first: e.g. "SOLAPUR 7990+GST", "CP CHITTUR 3450", "GOKAK 3210", "BIJAPUR 7850 + GST"
    m_place_first = re.match(r'^\*?\s*([A-Za-z\s\.\(\)\-\&]+?)\s+(\d{4})(?:\s*\+\s*gst|\s*\+\s*tax)?(?:\s*-\s*\d+)?\*?$', line_clean, re.I)
    if m_place_first:
        cand = clean_place_name(m_place_first.group(1))
        rate = int(m_place_first.group(2))
        if cand and len(cand) >= 2:
            return rate, cand

    return None

def parse_day_feed_messages(rows: list) -> dict:
    """Parses raw feed rate messages into structured category maps with dynamic place extraction."""
    ka_maize = {}
    tn_maize = {}
    kirti_soya = {}
    other_soya = {}
    grains = {}

    for r in rows:
        txt = r[2] or ""
        txt_low = txt.lower()

        # Skip unrelated reports
        if any(ign in txt_low for ign in ["broiler report", "poultry market", "doc report", "dorb", "paddy"]):
            continue

        is_kirti_msg = "kirti" in txt_low
        is_tn_msg = "tn maize" in txt_low or "tn srs" in txt_low
        is_soya_msg = ("soya seeds" in txt_low or "soyaseeds" in txt_low or "soya" in txt_low) and not is_kirti_msg
        
        current_sub_region = None

        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        for line in lines:
            l_low = line.lower().strip()
            if any(ign in l_low for ign in IGNORE_PHRASES):
                continue

            # Track explicit sub-region headers inside messages
            if re.match(r'^\*?ka\*?$', l_low):
                current_sub_region = "KA"
                continue
            if re.match(r'^\*?tn(?:\s+maize)?\*?$', l_low):
                current_sub_region = "TN"
                continue

            # Grains extraction
            if "khapli" in l_low:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', line.replace("*", ""))
                if m: grains["Khapli (Emmer Wheat)"] = m.group(1)
                continue
            elif "ragi" in l_low:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', line.replace("*", ""))
                if m: grains["Ragi"] = m.group(1)
                continue
            elif "hurali" in l_low:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', line.replace("*", ""))
                if m: grains["Hurali (Mysore)"] = m.group(1)
                continue
            elif "halasandi" in l_low:
                m = re.search(r'(\d{4,5}/\d{4,5}|\d{4,5}\s*-\s*\d{4,5})', line.replace("*", ""))
                if m: grains["Halasandi"] = m.group(1)
                continue

            res = parse_line_rate(line)
            if not res:
                continue

            rate, cand = res
            cand_low = cand.lower().strip()

            # Check if candidate matches any known canonical alias (longest key match first)
            matched_cat = None
            matched_name = None

            if is_kirti_msg and "gadag" in cand_low:
                matched_cat = "kirti_soya"
                matched_name = "Gadag"
            else:
                for alias_key in sorted(CANONICAL_ALIASES.keys(), key=len, reverse=True):
                    if alias_key in cand_low:
                        matched_cat, matched_name = CANONICAL_ALIASES[alias_key]
                        break

            # If no predefined alias exists, dynamically create a clean title-cased name
            if not matched_name:
                matched_name = cand.title()

            # Categorize dynamically by rate range and context
            if 6500 <= rate <= 8500:
                if is_kirti_msg or matched_cat == "kirti_soya" or matched_name in ["Solapur", "Latur", "Nanded", "Hingoli", "Karjol", "Bijapur", "Bidar", "Gulbarga", "Bailhongal"]:
                    kirti_soya[matched_name] = rate
                else:
                    other_soya[matched_name] = rate
            elif 2700 <= rate <= 4200:
                # Maize categorization
                if matched_cat == "tn_maize":
                    tn_maize[matched_name] = rate
                elif matched_cat == "ka_maize":
                    ka_maize[matched_name] = rate
                elif current_sub_region == "KA":
                    ka_maize[matched_name] = rate
                elif current_sub_region == "TN" or is_tn_msg:
                    tn_maize[matched_name] = rate
                else:
                    # Dynamic place fallback: check for TN/AP indicators
                    if any(w in cand_low for w in ["tn", "tamil", "ap", "andhra", "hyd", "erode"]):
                        tn_maize[matched_name] = rate
                    else:
                        ka_maize[matched_name] = rate

    return {
        "ka_maize": ka_maize,
        "tn_maize": tn_maize,
        "kirti_soya": kirti_soya,
        "other_soya": other_soya,
        "grains": grains
    }

def generate_daily_feed_rates_summary(target_date: date = None) -> str:
    """Generates the clean WhatsApp formatted Daily Feed Rates Summary Report comparing against yesterday."""
    if not target_date:
        target_date = datetime.now(IST).date()

    actual_target_date = find_latest_available_feed_date(target_date)
    prev_date = find_latest_available_feed_date(actual_target_date - timedelta(days=1))

    today_rows = get_feed_messages_for_date(actual_target_date)
    yest_rows = get_feed_messages_for_date(prev_date) if prev_date != actual_target_date else []

    today_data = parse_day_feed_messages(today_rows)
    yest_data = parse_day_feed_messages(yest_rows) if yest_rows else None

    disp_date = actual_target_date.strftime("%d %b %Y")

    out = [
        "📋 *DAILY FEED RATES SUMMARY REPORT*",
        f"📅 *Date:* {disp_date}",
        "==================================================",
        "",
        "🌽 *1. MAIZE (CORN) RATES (₹/Quintal)*",
        "--------------------------------------------------",
        "*Karnataka (KA):*"
    ]

    # 1. KA Maize sorted alphabetically (combines yesterday's full baseline with today's live updates)
    all_ka_places = set(today_data["ka_maize"].keys())
    if yest_data:
        all_ka_places.update(yest_data["ka_maize"].keys())

    for item in sorted(all_ka_places, key=lambda x: x.lower()):
        if item in today_data["ka_maize"]:
            t_val = today_data["ka_maize"][item]
            diff_str = ""
            if yest_data and item in yest_data["ka_maize"]:
                y_val = yest_data["ka_maize"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,}*{diff_str}")
        elif yest_data and item in yest_data["ka_maize"]:
            y_val = yest_data["ka_maize"][item]
            out.append(f"• {item} : *₹{y_val:,}*")

    out.append("\n*Tamil Nadu (TN) & Andhra Pradesh (AP):*")
    # 2. TN & AP Maize sorted alphabetically (combines yesterday's full baseline with today's live updates)
    all_tn_places = set(today_data["tn_maize"].keys())
    if yest_data:
        all_tn_places.update(yest_data["tn_maize"].keys())

    for item in sorted(all_tn_places, key=lambda x: x.lower()):
        if item in today_data["tn_maize"]:
            t_val = today_data["tn_maize"][item]
            diff_str = ""
            if yest_data and item in yest_data["tn_maize"]:
                y_val = yest_data["tn_maize"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,}*{diff_str}")
        elif yest_data and item in yest_data["tn_maize"]:
            y_val = yest_data["tn_maize"][item]
            out.append(f"• {item} : *₹{y_val:,}*")

    out.extend([
        "",
        "--------------------------------------------------",
        "🌱 *2. SOYABEAN SEEDS (₹/Quintal)*",
        "--------------------------------------------------",
        "*Kirti Group Delivery (₹/Quintal + GST):*"
    ])

    # 3. Kirti Soya sorted alphabetically (combines yesterday's full baseline with today's live updates)
    all_kirti_places = set(today_data["kirti_soya"].keys())
    if yest_data:
        all_kirti_places.update(yest_data["kirti_soya"].keys())

    for item in sorted(all_kirti_places, key=lambda x: x.lower()):
        if item in today_data["kirti_soya"]:
            t_val = today_data["kirti_soya"][item]
            diff_str = ""
            if yest_data and item in yest_data["kirti_soya"]:
                y_val = yest_data["kirti_soya"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,} + GST*{diff_str}")
        elif yest_data and item in yest_data["kirti_soya"]:
            y_val = yest_data["kirti_soya"][item]
            out.append(f"• {item} : *₹{y_val:,} + GST*")

    all_other_soya = set(today_data["other_soya"].keys())
    if yest_data:
        all_other_soya.update(yest_data["other_soya"].keys())

    if all_other_soya:
        out.append("\n*Other Soya Seed Processors:*")
        # 4. Other Soya Processors sorted alphabetically (combines yesterday's full baseline with today's live updates)
        for item in sorted(all_other_soya, key=lambda x: x.lower()):
            if item in today_data["other_soya"]:
                t_val = today_data["other_soya"][item]
                diff_str = ""
                if yest_data and item in yest_data["other_soya"]:
                    y_val = yest_data["other_soya"][item]
                    if t_val != y_val:
                        diff = t_val - y_val
                        diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
                out.append(f"• {item} : *₹{t_val:,}*{diff_str}")
            elif yest_data and item in yest_data["other_soya"]:
                y_val = yest_data["other_soya"][item]
                out.append(f"• {item} : *₹{y_val:,}*")

    # 5. Grains sorted alphabetically
    out.extend([
        "",
        "--------------------------------------------------",
        "🌾 *3. KHAPLI & GRAINS*",
        "--------------------------------------------------"
    ])
    merged_grains = dict(yest_data["grains"]) if yest_data else {}
    merged_grains.update(today_data["grains"])
    if "Khapli (Emmer Wheat)" not in merged_grains:
        merged_grains["Khapli (Emmer Wheat)"] = "5,500 – 5,700 / Qtl"
    for g_name in sorted(merged_grains.keys(), key=lambda x: x.lower()):
        g_val = merged_grains[g_name]
        if not g_val.endswith("/ Qtl") and not g_val.endswith("Qtl"):
            g_val = f"{g_val} / Qtl"
        out.append(f"• {g_name} : *₹{g_val}*")

    return "\n".join(out)

def send_daily_feed_rates_summary(target_date: date = None) -> dict:
    """Dispatches the daily feed rates summary to both target WhatsApp groups."""
    report_text = generate_daily_feed_rates_summary(target_date)
    
    results = {}
    target_groups = [
        (EGG_RATES_FORECAST_GROUP_JID, "Egg Rates & Weather Forecast"),
        (FEED_RATES_GROUP_JID, "Feed Rates")
    ]
    
    for jid, group_label in target_groups:
        try:
            logger.info(f"Sending Daily Feed Rates Summary to group '{group_label}' ({jid})...")
            success = send_waha_message(jid, report_text)
            results[group_label] = {"jid": jid, "success": bool(success)}
        except Exception as e:
            logger.error(f"Failed to send feed rates summary to '{group_label}': {e}")
            results[group_label] = {"jid": jid, "success": False, "error": str(e)}

    return results

def scheduled_daily_feed_rates_summary_job():
    """Scheduled cron job triggered everyday at 6:30 PM IST."""
    logger.info("Executing 6:30 PM Daily Feed Rates Summary Job...")
    try:
        results = send_daily_feed_rates_summary()
        logger.info(f"6:30 PM Daily Feed Rates Summary Job completed with results: {results}")
    except Exception as e:
        logger.error(f"Error in scheduled_daily_feed_rates_summary_job: {e}")
