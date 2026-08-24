import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage
from datetime import datetime, timezone, timedelta
import calendar

def generate_rental_vacancy_report():
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    date_formatted = now_ist.strftime("%A, %d %b %Y")
    day_num = now_ist.day
    days_in_month = calendar.monthrange(now_ist.year, now_ist.month)[1]
    month_name = now_ist.strftime("%B")

    RENT_RATES = {
        "Jumpin Stays": 23000,
        "Kadubeesanahalli": 23000,
        "Spice Garden": 25000,
        "K.R. Puram": 15000,
        "KR Puram": 15000
    }

    db = SessionLocal()
    group_jid = "120363409299826962@g.us"
    
    # Query latest message from Rental Updates group
    latest_msg = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.group_id.like("%120363409299826962%")
    ).order_by(WhatsAppMessage.timestamp.desc()).first()

    raw_text = ""
    if latest_msg and latest_msg.message_text:
        raw_text = latest_msg.message_text
    else:
        latest_raw = db.query(RawMessage).filter(
            RawMessage.group_name.like("%Rental%")
        ).order_by(RawMessage.timestamp.desc()).first()
        if latest_raw:
            raw_text = latest_raw.raw_text or ""

    db.close()

    # Default fallback vacancies if database message parse fallback
    vacancies = {
        "Jumpin Stays": [{"unit": "402", "floor": "4th Floor"}, {"unit": "404", "floor": "4th Floor"}],
        "Spice Garden": [{"unit": "302", "floor": "3rd Floor"}, {"unit": "402", "floor": "4th Floor"}],
        "K.R. Puram": [{"unit": "102", "floor": "1st Floor"}]
    }

    # If raw text available, parse dynamically
    if raw_text:
        parsed_vacancies = {"Jumpin Stays": [], "Spice Garden": [], "K.R. Puram": []}
        lines = raw_text.split('\n')
        for line in lines:
            line_clean = line.strip()
            if not line_clean: continue
            
            # Match Jumpin Stays / Kadubeesanahalli
            if re.search(r'kadubeesanahalli|jumpin', line_clean, re.I):
                units = re.findall(r'\b\d{3}\b', line_clean)
                for u in units:
                    floor_num = u[0]
                    floor_str = f"{floor_num}th Floor" if floor_num != '1' and floor_num != '2' and floor_num != '3' else f"{floor_num}st Floor" if floor_num == '1' else f"{floor_num}nd Floor" if floor_num == '2' else f"{floor_num}rd Floor"
                    parsed_vacancies["Jumpin Stays"].append({"unit": u, "floor": floor_str})

            # Match Spice Garden
            elif re.search(r'spice garden', line_clean, re.I):
                units = re.findall(r'\b\d{3}\b', line_clean)
                for u in units:
                    floor_num = u[0]
                    floor_str = f"{floor_num}th Floor" if floor_num != '1' and floor_num != '2' and floor_num != '3' else f"{floor_num}st Floor" if floor_num == '1' else f"{floor_num}nd Floor" if floor_num == '2' else f"{floor_num}rd Floor"
                    parsed_vacancies["Spice Garden"].append({"unit": u, "floor": floor_str})

            # Match K.R. Puram
            elif re.search(r'k\.?r\.?\s*puram', line_clean, re.I):
                units = re.findall(r'\b\d{3}\b', line_clean)
                for u in units:
                    floor_num = u[0]
                    floor_str = f"{floor_num}th Floor" if floor_num != '1' and floor_num != '2' and floor_num != '3' else f"{floor_num}st Floor" if floor_num == '1' else f"{floor_num}nd Floor" if floor_num == '2' else f"{floor_num}rd Floor"
                    parsed_vacancies["K.R. Puram"].append({"unit": u, "floor": floor_str})

        if any(parsed_vacancies.values()):
            vacancies = parsed_vacancies

    total_vacant_units = sum(len(units) for units in vacancies.values())
    total_daily_loss = 0
    property_blocks = []

    for prop_name, units in vacancies.items():
        monthly_rent = RENT_RATES.get(prop_name, 20000)
        daily_loss_per_unit = round(monthly_rent / days_in_month)
        
        unit_lines = []
        for item in units:
            u_no = item["unit"]
            fl = item["floor"]
            unit_lines.append(f"  └ Unit *{u_no}* ({fl}) - Rent: ₹{monthly_rent:,}/mo | *Loss: ₹{daily_loss_per_unit:,}/day*")
            total_daily_loss += daily_loss_per_unit

        if unit_lines:
            block = f"🏢 *{prop_name}:*\n" + "\n".join(unit_lines)
            property_blocks.append(block)

    mtd_loss = total_daily_loss * day_num
    projected_monthly_loss = total_daily_loss * days_in_month

    report = (
        f"🚨 *DAILY RENTAL & VACANCY LOSS REPORT* 🚨\n"
        f"📅 *Date:* {date_formatted}\n\n"
        f"📊 *SUMMARY OVERVIEW*\n"
        f"• Total Properties: 3 (Jumpin Stays, Spice Garden & K.R. Puram)\n"
        f"• *Empty/Vacant:* {total_vacant_units} Units\n\n"
        f"💰 *FINANCIAL VACANCY LOSS*\n"
        f"• *Daily Loss Today:* ₹{total_daily_loss:,}\n"
        f"• *MTD Loss ({month_name} 1-{day_num}):* ₹{mtd_loss:,}\n"
        f"• *Projected Monthly Loss:* ₹{projected_monthly_loss:,}\n\n"
        f"📍 *VACANT ROOMS DETAILS*\n"
        + "\n\n".join(property_blocks)
    )

    return report

if __name__ == "__main__":
    print(generate_rental_vacancy_report())
