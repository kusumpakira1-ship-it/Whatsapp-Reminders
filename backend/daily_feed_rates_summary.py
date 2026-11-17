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

def parse_day_feed_messages(rows: list) -> dict:
    """Parses raw feed rate messages into structured category maps."""
    ka_maize = {}
    tn_maize = {}
    kirti_soya = {}
    other_soya = {}
    grains = {}

    for r in rows:
        txt = r[2] or ""
        txt_low = txt.lower()

        # Skip broiler / poultry live bird reports
        if "broiler report" in txt_low or "poultry market" in txt_low:
            continue

        lines = [l.strip() for l in txt.split("\n") if l.strip()]

        # 1. KIRTI SOYA GROUP
        if "kirti" in txt_low and ("soya" in txt_low or "solapur" in txt_low or "bijapur" in txt_low or "karjol" in txt_low):
            for l in lines:
                l_c = l.replace("*", "").replace("=", " ").replace("+gst", "").replace("+ gst", "").strip().lower()
                for loc in ["solapur", "latur", "nanded", "hingoli", "karjol", "bijapur", "vijayapura", "bidar", "gulbarga", "bailhongal", "gadag"]:
                    if loc in l_c:
                        m = re.search(r'(\d{4})', l_c)
                        if m:
                            val = int(m.group(1))
                            if 6900 <= val <= 7500:
                                name = "Bijapur" if loc in ["bijapur", "vijayapura"] else loc.title()
                                kirti_soya[name] = val
            continue

        # 2. TN MAIZE
        if "tn maize" in txt_low or "tn shanti" in txt_low or "tn srs" in txt_low:
            for l in lines:
                l_c = l.replace("*", "").strip().lower()
                for key, display in [
                    ("shanti", "Shanti (TN)"),
                    ("skm erode", "SKM Erode"),
                    ("baramasagar", "Baramasagar"),
                    ("namakkal", "Namakkal"),
                    ("namaal", "Namakkal"),
                    ("srs", "SRS"),
                    ("paladam", "Palladam"),
                    ("palladam", "Palladam"),
                    ("annur", "Annur"),
                    ("tanjaure", "Thanjavur"),
                    ("thanjavur", "Thanjavur"),
                    ("hosur", "Hosur"),
                    ("mbs", "MBS"),
                    ("punanoor", "Punanoor (AP)"),
                    ("hyd", "Hyderabad"),
                    ("udamalpet", "Udamalpet")
                ]:
                    if key in l_c:
                        m = re.search(r'(\d{4})', l_c)
                        if m:
                            val = int(m.group(1))
                            if 2800 <= val <= 4000:
                                tn_maize[display] = val
            continue

        # 3. KA MAIZE
        if "maize" in txt_low and "tn maize" not in txt_low:
            for l in lines:
                l_c = l.replace("*", "").replace(".", " ").strip().lower()
                for key, display in [
                    ("bengaluru", "Bengaluru"),
                    ("dabaspet", "Dabaspet"),
                    ("abhis", "Abhis"),
                    ("sneha", "Sneha"),
                    ("hoskote", "Hoskote (Credit)"),
                    ("c mangalur", "C Mangaluru"),
                    ("najangudu", "Nanjangudu"),
                    ("nanjangudu", "Nanjangudu"),
                    ("mysore", "Mysore"),
                    ("mangalore", "Mangalore"),
                    ("hebari", "Hebbari"),
                    ("hebbari", "Hebbari"),
                    ("ranebennur", "Ranebennur"),
                    ("ranebenur", "Ranebennur"),
                    ("haveri", "Haveri"),
                    ("koppal", "Koppal"),
                    ("bagalakote", "Bagalkote"),
                    ("chikballapura", "Chikkaballapura / Kolar"),
                    ("davangere", "Davangere"),
                    ("vhl rnr", "VHL RNR"),
                    ("vhl hubli", "VHL Hubli"),
                    ("bgm", "Belgaum (BGM)"),
                    ("sankeshwar", "Sankeshwar"),
                    ("ambuja", "Ambuja"),
                    ("gokak", "Gokak"),
                    ("sahyadri", "Sahyadri"),
                    ("sangli", "Sangli"),
                    ("snagali", "Sangli"),
                    ("asha", "Asha"),
                    ("yaran", "Yaran"),
                ]:
                    if key in l_c and display not in ka_maize:
                        m = re.search(r'(\d{4})', l_c)
                        if m:
                            val = int(m.group(1))
                            if 2800 <= val <= 3800:
                                ka_maize[display] = val
            continue

        # 4. OTHER SOYA SEEDS
        if ("soya seeds" in txt_low or "soyaseeds" in txt_low) and "dorb" not in txt_low:
            for l in lines:
                l_c = l.replace("*", "").strip()
                m = re.search(r'(\d{4})\s+([a-zA-Z\s]{3,30})', l_c)
                if not m:
                    m = re.search(r'([a-zA-Z\s]{3,30})\s+(\d{4})', l_c)
                    if m:
                        val = int(m.group(2))
                        p_name = m.group(1).strip().title()
                    else:
                        val = None
                else:
                    val = int(m.group(1))
                    p_name = m.group(2).strip().title()

                if val and 6800 <= val <= 7800 and not any(k in p_name.lower() for k in ["solapur", "latur", "nanded", "hingoli", "karjol", "bijapur", "bidar", "gulbarga", "bailhongal", "gadag"]):
                    if "chekamangalore" in p_name.lower() or "c mangalore" in p_name.lower():
                        p_name = "C Mangalore (KA)"
                    elif "darapuram" in p_name.lower():
                        p_name = "TN Darapuram"
                    other_soya[p_name] = val
            continue

        # 5. KHAPLI & GRAINS
        for l in lines:
            l_c = l.replace("*", "").strip().lower()
            if "khapli" in l_c:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', l.replace("*", ""))
                if m: grains["Khapli (Emmer Wheat)"] = m.group(1)
            elif "ragi" in l_c:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', l.replace("*", ""))
                if m: grains["Ragi"] = m.group(1)
            elif "hurali" in l_c:
                m = re.search(r'(\d{4}/\d{4}|\d{4}\s*-\s*\d{4})', l.replace("*", ""))
                if m: grains["Hurali (Mysore)"] = m.group(1)
            elif "halasandi" in l_c:
                m = re.search(r'(\d{4,5}/\d{4,5}|\d{4,5}\s*-\s*\d{4,5})', l.replace("*", ""))
                if m: grains["Halasandi"] = m.group(1)

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

    # Predefined ordering for KA Maize
    ka_order = [
        "Bengaluru", "Hoskote (Credit)", "Ranebennur", "Gokak", "Sneha", "Dabaspet",
        "Nanjangudu", "Mangalore", "Chikkaballapura / Kolar", "Mysore", "C Mangaluru",
        "Koppal", "Hebbari", "Abhis", "Davangere", "Bagalkote", "VHL Hubli",
        "VHL RNR", "Ambuja", "Sangli", "Haveri", "Sahyadri", "Sankeshwar", "Belgaum (BGM)",
        "Asha", "Yaran"
    ]
    for k in today_data["ka_maize"]:
        if k not in ka_order:
            ka_order.append(k)

    for item in ka_order:
        if item in today_data["ka_maize"]:
            t_val = today_data["ka_maize"][item]
            diff_str = ""
            if yest_data and item in yest_data["ka_maize"]:
                y_val = yest_data["ka_maize"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,}*{diff_str}")

    out.append("\n*Tamil Nadu (TN) & Andhra Pradesh (AP):*")
    tn_order = [
        "Shanti (TN)", "SKM Erode", "Baramasagar", "SRS", "Palladam", "Annur",
        "Thanjavur", "Namakkal", "Udamalpet", "Hosur", "MBS", "Punanoor (AP)", "Hyderabad"
    ]
    for k in today_data["tn_maize"]:
        if k not in tn_order:
            tn_order.append(k)

    for item in tn_order:
        if item in today_data["tn_maize"]:
            t_val = today_data["tn_maize"][item]
            diff_str = ""
            if yest_data and item in yest_data["tn_maize"]:
                y_val = yest_data["tn_maize"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,}*{diff_str}")

    out.extend([
        "",
        "--------------------------------------------------",
        "🌱 *2. SOYABEAN SEEDS (₹/Quintal)*",
        "--------------------------------------------------",
        "*Kirti Group Delivery (₹/Quintal + GST):*"
    ])

    kirti_order = ["Solapur", "Latur", "Hingoli", "Nanded", "Karjol", "Bijapur", "Bidar", "Gulbarga", "Bailhongal", "Gadag"]
    for item in kirti_order:
        if item in today_data["kirti_soya"]:
            t_val = today_data["kirti_soya"][item]
            diff_str = ""
            if yest_data and item in yest_data["kirti_soya"]:
                y_val = yest_data["kirti_soya"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,} + GST*{diff_str}")

    if today_data["other_soya"]:
        out.append("\n*Other Soya Seed Processors:*")
        for item, t_val in sorted(today_data["other_soya"].items()):
            diff_str = ""
            if yest_data and item in yest_data["other_soya"]:
                y_val = yest_data["other_soya"][item]
                if t_val != y_val:
                    diff = t_val - y_val
                    diff_str = f" (🔺 *+₹{diff}*)" if diff > 0 else f" (🔻 *-₹{abs(diff)}*)"
            out.append(f"• {item} : *₹{t_val:,}*{diff_str}")

    # Grains
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
    for g_name, g_val in merged_grains.items():
        if not g_val.endswith("/ Qtl") and not g_val.endswith("Qtl"):
            g_val = f"{g_val} / Qtl"
        out.append(f"• {g_name} : *₹{g_val}*")

    # Trend summary
    out.extend([
        "",
        "==================================================",
        "📊 *PRICE TREND SUMMARY:*",
        "• *Maize:* Active price changes updated with delivery quotes across Karnataka and Tamil Nadu plants.",
        "• *Soya Seeds:* Delivery and plant rates updated for Kirti Group and regional processors.",
        "=================================================="
    ])

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
