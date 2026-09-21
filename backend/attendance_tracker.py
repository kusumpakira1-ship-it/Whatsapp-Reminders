import os
import re
import logging
from datetime import datetime, date, time
from sqlalchemy import text
from database import get_db_session
from models import RawMessage, WhatsAppMessage, DailyAttendance

logger = logging.getLogger(__name__)

# Master list of 11 Groups & 30 Employees
COMMUNITY_EMPLOYEES = [
    {
        "group": "AI & IOT",
        "group_jids": ["120363429469512014", "ai & iot"],
        "employees": [
            {"name": "Kusum", "phone": "7975209680", "aliases": ["kusum", "kusumpakira", "7975209680", "917975209680", "183300681367688"]},
            {"name": "Poornima", "phone": "7204484516", "aliases": ["poornima", "poorna", "207627359363311", "7204484516", "917204484516"]},
            {"name": "Akshay", "phone": "9019713446", "aliases": ["akshay i h", "206686828683301", "9019713446", "919019713446"]},
            {"name": "Ramya", "phone": "7019063646", "aliases": ["ramya", "259149770277018", "7019063646", "917019063646"]},
        ]
    },
    {
        "group": "Sunfra OLX CEE",
        "group_jids": ["120363428895707621", "sunfra olx cee"],
        "employees": [
            {"name": "Asif", "phone": "6364063475", "aliases": ["asif", "unfazed", "42932509909155", "6364063475", "916364063475"]},
            {"name": "Prasanna", "phone": "9618803740", "aliases": ["prasanna", "prasanna choudhary", "215538974326819", "9618803740", "919618803740"]},
            {"name": "Yashaswini", "phone": "9573630573", "aliases": ["yashaswini", "124798881513608", "9573630573", "919573630573"]},
        ]
    },
    {
        "group": "Jataayu",
        "group_jids": ["120363428872126006", "120363428881117777", "120363422729608263", "jataayu"],
        "employees": [
            {"name": "Roopa", "phone": "8686856459", "aliases": ["roopa", "rupa", "rupakamalapuram", "147635256201243", "8686856459", "918686856459"]},
        ]
    },
    {
        "group": "Sunfra Corporate",
        "group_jids": ["120363428349268084", "120363427470582988", "120363426659667927", "120363425581380088", "sunfra corporate"],
        "employees": [
            {"name": "Divya", "phone": "9381255565", "aliases": ["divya", "9381255565", "919381255565"]},
            {"name": "Prajwal", "phone": "9036597989", "aliases": ["prajwal", "68195624992799", "9036597989", "919036597989"]},
        ]
    },
    {
        "group": "Sunfra Mudah",
        "group_jids": ["120363410545216320", "sunfra mudah"],
        "employees": [
            {"name": "Akshay", "phone": "8123466671", "aliases": ["265136954671130", "8123466671", "918123466671", "akshay (tester)"]},
            {"name": "Bharath", "phone": "7989525010", "aliases": ["bharath", "g r bharath", "166683486466210", "7989525010", "917989525010"]},
            {"name": "Krishna", "phone": "9182535260", "aliases": ["krishna", "chaitanya bandaru", "96074157031436", "9182535260", "919182535260"]},
            {"name": "Nisha", "phone": "9740828621", "aliases": ["nisha", "nisha_subbayya", "125795330740245", "9740828621", "919740828621"]},
            {"name": "Ravi Teja", "phone": "7981745785", "aliases": ["ravi teja", "ravi", "159313775583316", "7981745785", "917981745785"]},
            {"name": "Thanuja", "phone": "8978331872", "aliases": ["thanuja", "thota thanuja", "125889819983939", "8978331872", "918978331872"]},
            {"name": "Aishwarya", "phone": "8495004826", "aliases": ["aishwarya", "20551502401730", "8495004826", "918495004826"]},
            {"name": "Lakshmi", "phone": "137812783452345", "aliases": ["lakshmi", "lakshmy", "137812783452345", "137812783452345@lid"]},
        ]
    },
    {
        "group": "Sunfra HR Team",
        "group_jids": ["120363431222906850", "sunfra hr team"],
        "employees": [
            {"name": "Parvati", "phone": "7995452523", "aliases": ["parvati", "paru bavisetti", "245225503076572", "7995452523", "917995452523"]},
            {"name": "Bhanushree", "phone": "9901497574", "aliases": ["bhanushree", "bhanushree n.t", "bhanu", "81991244460218", "9901497574", "919901497574"]},
        ]
    },
    {
        "group": "Indus",
        "group_jids": ["120363431080782528", "indus"],
        "employees": [
            {"name": "Girija", "phone": "8618580633", "aliases": ["girija", "girijaa dn", "133522631176396", "8618580633", "918618580633"]},
            {"name": "Jagadish", "phone": "7676711899", "aliases": ["jagadish", "7676711899", "917676711899"]},
        ]
    },
    {
        "group": "Sunfra Farms",
        "group_jids": ["120363429481469212", "120363221285198390", "120363221211615047", "120363421181996594", "120363410607412989", "sunfra farms"],
        "employees": [
            {"name": "Mahalakshmi", "phone": "6364817749", "aliases": ["mahalakshmi", "184791135711366", "6364817749", "916364817749"]},
        ]
    },
    {
        "group": "Sunfra Feeds",
        "group_jids": ["120363413108636132", "120363412616266332", "120363410508859526", "sunfra feeds"],
        "employees": [
            {"name": "Venkat", "phone": "8247586860", "aliases": ["venkat", "45586833240126", "8247586860", "918247586860"]},
        ]
    },
    {
        "group": "Management Team",
        "group_jids": ["120363410684018393", "120363406924564250", "management team"],
        "employees": [
            {"name": "Balaji", "phone": "9493928388", "aliases": ["balaji", "balaji reddy", "242695733772318", "9493928388", "919493928388"]},
            {"name": "Prathiba", "phone": "8951520293", "aliases": ["prathiba", "2169075933244", "8951520293", "918951520293"]},
            {"name": "Vamsi", "phone": "9677277787", "aliases": ["vamsi", "vamcgalla", "142648950186164", "9677277787", "919677277787"]},
            {"name": "Nikhil", "phone": "9010889837", "aliases": ["nikhil", "36919622766745", "9010889837", "919010889837"]},
            {"name": "Nani", "phone": "7204041105", "aliases": ["nani", "nani chinnam", "112300593815672", "26049698091190", "7204041105", "917204041105"]},
            {"name": "Prasad", "phone": "7204021105", "aliases": ["prasad", "vara prasad", "123622194712585", "7204021105", "917204021105"]},
        ]
    },
    {
        "group": "Tendered",
        "group_jids": ["120363411380848761", "tendered team", "tendered"],
        "employees": [
            {"name": "Ganga", "phone": "213795016290432", "aliases": ["ganga", "213795016290432", "213795016290432@lid"]},
        ]
    }
]

def evaluate_attendance_for_date(target_date_str: str = None) -> dict:
    if not target_date_str:
        target_date_str = date.today().strftime('%Y-%m-%d')

    db = get_db_session()
    try:
        # Fetch raw messages for the day as lightweight tuples to avoid connection leaks & ORM lazy loading issues
        class SimpleMsg:
            def __init__(self, sender, group_name, raw_text, timestamp):
                self.sender = sender
                self.group_name = group_name
                self.raw_text = raw_text
                self.timestamp = timestamp

        raw_tuples = db.query(
            RawMessage.sender, 
            RawMessage.group_name, 
            RawMessage.raw_text, 
            RawMessage.timestamp
        ).filter(
            RawMessage.timestamp >= f"{target_date_str} 00:00:00",
            RawMessage.timestamp <= f"{target_date_str} 23:59:59"
        ).all()

        wa_tuples = db.query(
            WhatsAppMessage.sender_id,
            WhatsAppMessage.group_id,
            WhatsAppMessage.message_text,
            WhatsAppMessage.timestamp
        ).filter(
            WhatsAppMessage.timestamp >= f"{target_date_str} 00:00:00",
            WhatsAppMessage.timestamp <= f"{target_date_str} 23:59:59"
        ).all()

        raws = [SimpleMsg(t[0], t[1], t[2], t[3]) for t in raw_tuples]
        for wt in wa_tuples:
            raws.append(SimpleMsg(wt[0], wt[1], wt[2], wt[3]))

        group_records = []
        tot_present = 0
        tot_half_day_present = 0
        tot_half_day = 0
        tot_leave = 0
        tot_absent = 0
        tot_employees = 0

        for grp_data in COMMUNITY_EMPLOYEES:
            grp_name = grp_data["group"]
            grp_name_lower = grp_name.lower()
            grp_jids = [j.lower() for j in grp_data.get("group_jids", [])]
            emp_list = []

            for emp in grp_data["employees"]:
                tot_employees += 1
                emp_name = emp["name"]
                phone = emp["phone"]
                aliases = emp.get("aliases", [])

                grp_target_name = grp_name.lower()
                grp_jids_lower = [j.lower() for j in grp_data.get("group_jids", [])] + [grp_target_name]

                # Match all messages sent by this employee across community groups
                matched_msgs = []
                for r in raws:
                    s_str = str(r.sender or "").lower()
                    g_str = str(r.group_name or "").lower()
                    
                    # Direct phone match
                    is_sender_match = (phone in s_str) or (("91" + phone) in s_str)
                    
                    # Alias / LID match
                    if not is_sender_match:
                        for al in aliases:
                            al_low = al.lower()
                            if al_low in s_str:
                                # Prevent false positive substring match: 'lakshmi' matching 'mahalakshmi'
                                if al_low == "lakshmi" and "mahalakshmi" in s_str:
                                    continue
                                is_sender_match = True
                                break
                    
                    # Match if sender matches (employee activity across community groups)
                    if is_sender_match:
                        matched_msgs.append(r)

                matched_msgs.sort(key=lambda x: x.timestamp)

                login_time = None
                logout_time = None
                leave_time = None
                lunch_start_time = None
                lunch_end_time = None
                break_start_time = None
                break_end_time = None
                total_break_seconds = 0
                curr_break_start = None

                login_kws = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "loging in", "sign in", "signing in", "signed in", "morning team", "good morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]
                logout_kws = ["logout", "log out", "logged out", "loged out", "logedout", "logging out", "loging out", "sign out", "signout", "signing out", "signed out", "sign off", "signoff", "signing off", "signed off", "bye team", "bye all", "signing off team", "out", "im out", "i'm out"]
                lunch_kws = ["lunch", "lunch break", "out for lunch", "going for lunch", "leaving for lunch"]
                break_kws = ["tea", "tea break", "break", "snacks", "coffee", "brb", "afk"]
                break_start_kws = lunch_kws + break_kws
                break_end_kws = ["back", "return", "returned", "back to work", "rejoined"]
                leave_regex = re.compile(r'\b(leave|on\s+leave|taking\s+leave|leave\s+today|sick\s+leave|casual\s+leave|applied\s+leave|planned\s+leave|cl|sl|eave)\b', re.IGNORECASE)
                logout_regex = re.compile(
                    r'\b('
                    r'log\s*out|logged\s*out|loged\s*out|loging\s*out|logging\s*out|'
                    r'sign\s*out|signed\s*out|signing\s*out|sign\s*off|signed\s*off|signing\s*off|'
                    r'signout|signoff|singout|singed\s*out|'
                    r'bye|bye\s+team|bye\s+all|good\s*night|gn|gn\s+team|'
                    r'done\s+for\s+today|done\s+for\s+the\s+day|work\s+done|work\s+completed|completed\s+for\s+today|'
                    r'leaving|leaving\s+office|left\s+office|left\s+for\s+today|left\s+for\s+the\s+day|heading\s+home|going\s+home|'
                    r'day\s+end|end\s+of\s+day|eod|out\s+for\s+the\s+day'
                    r')\b',
                    re.IGNORECASE
                )

                def is_keyword_match(text_str, kws):
                    t = text_str.strip().lower()
                    lines = [l.strip() for l in t.split('\n') if l.strip()]
                    for line in lines:
                        for kw in kws:
                            if line == kw or line.startswith(kw + " ") or line.endswith(" " + kw) or (f" {kw} " in line):
                                return True
                            if len(kw) >= 4 and (kw in line):
                                return True
                    return False

                for m in matched_msgs:
                    txt = (m.raw_text or "").strip().lower()
                    
                    # Check leave keywords
                    if leave_regex.search(txt):
                        leave_time = m.timestamp

                    # Check lunch start
                    if is_keyword_match(txt, lunch_kws):
                        if not lunch_start_time:
                            lunch_start_time = m.timestamp
                        if not curr_break_start:
                            curr_break_start = m.timestamp
                        continue

                    # Check general break start
                    if is_keyword_match(txt, break_kws):
                        if not break_start_time:
                            break_start_time = m.timestamp
                        if not curr_break_start:
                            curr_break_start = m.timestamp
                        continue

                    # Check break / lunch end
                    if is_keyword_match(txt, break_end_kws):
                        if curr_break_start:
                            if lunch_start_time and not lunch_end_time:
                                lunch_end_time = m.timestamp
                            elif break_start_time and not break_end_time:
                                break_end_time = m.timestamp
                            break_sec = (m.timestamp - curr_break_start).total_seconds()
                            total_break_seconds += break_sec
                            curr_break_start = None
                        continue

                    # Check login keywords
                    if is_keyword_match(txt, login_kws):
                        if not login_time:
                            login_time = m.timestamp
                    # Check logout keywords
                    if is_keyword_match(txt, logout_kws) or logout_regex.search(txt):
                        logout_time = m.timestamp

                # Fallback for login_time: If employee posted messages but didn't type explicit "login" keyword, use first message timestamp
                if not login_time and matched_msgs:
                    non_leave_msgs = [m for m in matched_msgs if not leave_regex.search((m.raw_text or "").strip().lower())]
                    if non_leave_msgs:
                        login_time = non_leave_msgs[0].timestamp

                # User confirmation override: Balaji logged in on 2026-09-19
                if emp_name == "Balaji" and not login_time and target_date_str == "2026-09-19":
                    login_time = datetime.strptime(f"{target_date_str} 09:00:00", "%Y-%m-%d %H:%M:%S")

                if curr_break_start and logout_time and logout_time > curr_break_start:
                    total_break_seconds += 2700

                gross_hours = 0.0
                net_hours = 0.0
                if login_time and logout_time:
                    gross_seconds = (logout_time - login_time).total_seconds()
                    gross_hours = gross_seconds / 3600.0
                    net_seconds = max(0, gross_seconds - total_break_seconds)
                    net_hours = net_seconds / 3600.0

                # Late login threshold is 11:00 AM (login after 11:00 AM)
                is_late = login_time and (login_time.hour > 11 or (login_time.hour == 11 and login_time.minute > 0))

                # Apply Attendance Rules:
                if leave_time and not login_time:
                    status_type = "on_leave"
                    status_badge = "🔵 On Leave"
                    detail = f"Leave message at {leave_time.strftime('%I:%M %p')}"
                    tot_leave += 1
                elif leave_time and login_time:
                    status_type = "half_day_leave"
                    status_badge = "⚪ Half Day Present"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} | Leave at {leave_time.strftime('%I:%M %p')}"
                    tot_half_day_present += 1
                elif not login_time and not logout_time:
                    status_type = "absent"
                    status_badge = "🔴 Absent"
                    detail = "No login or logout message"
                    tot_absent += 1
                elif not login_time and logout_time:
                    status_type = "half_day_no_login"
                    status_badge = "🟡 Half Day (No Login)"
                    detail = f"No Login | Logout at {logout_time.strftime('%I:%M %p')}"
                    tot_half_day += 1
                elif is_late and not logout_time:
                    status_type = "half_day_late_no_logout"
                    status_badge = "🟡 Half Day (Late Login & No Logout)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} (> 11:00 AM) | No Logout"
                    tot_half_day += 1
                elif is_late:
                    status_type = "half_day_late"
                    status_badge = "🟡 Half Day (Late Login)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} (> 11:00 AM)"
                    tot_half_day += 1
                elif not logout_time:
                    status_type = "half_day_no_logout"
                    status_badge = "🟡 Half Day (No Logout)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} | No Logout"
                    tot_half_day += 1
                elif net_hours < 8.0:
                    status_type = "present_short"
                    status_badge = "🟠 Present"
                    detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')} (Net: {net_hours:.1f} hrs)"
                    tot_present += 1
                else:
                    status_type = "present"
                    status_badge = "🟢 Present"
                    detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')} (Net: {net_hours:.1f} hrs)"
                    tot_present += 1

                # Persist / Upsert into DB table (sunfra_attendance_logs)
                try:
                    att_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                    existing_rec = db.query(DailyAttendance).filter(
                        DailyAttendance.date == att_date,
                        DailyAttendance.employee_name == emp_name,
                        DailyAttendance.company_name == grp_name
                    ).first()
                    
                    primary_group_id = grp_jids[0] if grp_jids else None
                    if not existing_rec:
                        existing_rec = DailyAttendance(
                            date=att_date,
                            employee_name=emp_name,
                            phone_number=phone,
                            company_name=grp_name,
                            group_id=primary_group_id
                        )
                        db.add(existing_rec)
                    else:
                        existing_rec.group_id = primary_group_id
                    
                    existing_rec.login_time = login_time.strftime('%I:%M %p') if login_time else None
                    existing_rec.lunch_start_time = lunch_start_time.strftime('%I:%M %p') if lunch_start_time else None
                    existing_rec.lunch_end_time = lunch_end_time.strftime('%I:%M %p') if lunch_end_time else None
                    existing_rec.break_start_time = break_start_time.strftime('%I:%M %p') if break_start_time else None
                    existing_rec.break_end_time = break_end_time.strftime('%I:%M %p') if break_end_time else None
                    existing_rec.logout_time = logout_time.strftime('%I:%M %p') if logout_time else None
                    existing_rec.total_break_minutes = int(total_break_seconds / 60)
                    existing_rec.net_hours = round(net_hours, 2)
                    existing_rec.status_type = status_type
                    existing_rec.status_badge = status_badge
                    existing_rec.detail = detail
                    
                    db.commit()
                except Exception as dbe:
                    db.rollback()
                    logger.warning(f"Failed to upsert attendance log for {emp_name}: {dbe}")

                emp_list.append({
                    "name": emp_name,
                    "phone": phone,
                    "status_type": status_type,
                    "status_badge": status_badge,
                    "detail": detail,
                    "net_hours": round(net_hours, 1),
                    "login_time": login_time.strftime('%I:%M %p') if login_time else "-",
                    "lunch_start_time": lunch_start_time.strftime('%I:%M %p') if lunch_start_time else "-",
                    "lunch_end_time": lunch_end_time.strftime('%I:%M %p') if lunch_end_time else "-",
                    "break_start_time": break_start_time.strftime('%I:%M %p') if break_start_time else "-",
                    "break_end_time": break_end_time.strftime('%I:%M %p') if break_end_time else "-",
                    "logout_time": logout_time.strftime('%I:%M %p') if logout_time else "-"
                })

            emp_list.sort(key=lambda x: x['name'].lower())

            group_records.append({
                "group_name": grp_name,
                "employees": emp_list
            })

        return {
            "date": target_date_str,
            "total_employees": tot_employees,
            "total_present": tot_present,
            "total_half_day_present": tot_half_day_present,
            "total_half_day": tot_half_day,
            "total_leave": tot_leave,
            "total_absent": tot_absent,
            "groups": group_records
        }
    finally:
        db.close()

def generate_attendance_summary_message(data: dict) -> str:
    dt = datetime.strptime(data['date'], '%Y-%m-%d')
    disp_date = dt.strftime('%d %b %Y')
    
    lines = [
        f"📋 *Daily Attendance Report*",
        f"📅 *Date:* {disp_date}",
        "=================================================="
    ]

    for g in data['groups']:
        lines.append(f"\n🏢 *{g['group_name']}*")
        for emp in g['employees']:
            badge = emp.get('status_badge') or '🔴 Absent'
            lines.append(f"  • *{emp['name']}*: {badge}")

    lines.extend([
        "\n==================================================",
        f"📊 *OVERALL STATS:*",
        f"👥 Total Employees: *{data['total_employees']}*",
        f"🟢 Present (Full Day): *{data['total_present']}*",
        f"⚪ Half Day Present: *{data.get('total_half_day_present', 0)}*",
        f"🟡 Half Day: *{data['total_half_day']}*",
        f"🔵 On Leave: *{data.get('total_leave', 0)}*",
        f"🔴 Absent: *{data['total_absent']}*",
        "=================================================="
    ])

    return "\n".join(lines)

def generate_company_attendance_messages(data: dict) -> dict:
    """Generates company-wise attendance messages for each of the 10 groups."""
    dt = datetime.strptime(data['date'], '%Y-%m-%d')
    disp_date = dt.strftime('%d %b %Y')
    
    company_msgs = {}
    for g in data['groups']:
        lines = [
            f"📋 *{g['group_name']} Attendance Report*",
            f"📅 *Date:* {disp_date}\n"
        ]

        for emp in g['employees']:
            badge = emp.get('status_badge') or '🔴 Absent'
            lines.append(f"  • *{emp['name']}*: {badge}")

        company_msgs[g['group_name']] = "\n".join(lines)
    return company_msgs

if __name__ == "__main__":
    report_data = evaluate_attendance_for_date()
    msg = generate_attendance_summary_message(report_data)
    print("\n" + msg)
