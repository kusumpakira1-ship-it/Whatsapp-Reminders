import os
import re
import logging
from datetime import datetime, date, time
from sqlalchemy import text
from database import SessionLocal
from models import RawMessage, WhatsAppMessage

logger = logging.getLogger(__name__)

# Master list of 10 Groups & Employees
COMMUNITY_EMPLOYEES = [
    {
        "group": "AI & IOT",
        "employees": [
            {"name": "Kusum", "phone": "7975209680", "aliases": ["kusum", "kusumpakira", "7975209680", "917975209680", "183300681367688"]},
            {"name": "Poornima", "phone": "7204484516", "aliases": ["poornima", "poorna", "207627359363311", "7204484516", "917204484516"]},
            {"name": "Akshay", "phone": "9019713446", "aliases": ["akshay i h", "206686828683301", "9019713446", "919019713446"]},
            {"name": "Ramya", "phone": "7019063646", "aliases": ["ramya", "259149770277018", "7019063646", "917019063646"]},
        ]
    },
    {
        "group": "Sunfra OLX CEE",
        "employees": [
            {"name": "Asif", "phone": "6364063475", "aliases": ["asif", "unfazed", "42932509909155", "6364063475", "916364063475"]},
            {"name": "Prasanna", "phone": "9618803740", "aliases": ["prasanna", "prasanna choudhary", "215538974326819", "9618803740", "919618803740"]},
            {"name": "Yashaswini", "phone": "9573630573", "aliases": ["yashaswini", "124798881513608", "9573630573", "919573630573"]},
        ]
    },
    {
        "group": "Jataayu",
        "employees": [
            {"name": "Roopa", "phone": "8686856459", "aliases": ["roopa", "8686856459", "918686856459"]},
        ]
    },
    {
        "group": "Sunfra Corporate",
        "employees": [
            {"name": "Divya", "phone": "9381255565", "aliases": ["divya", "56556230058144", "9381255565", "919381255565"]},
            {"name": "Prajwal", "phone": "9036597989", "aliases": ["prajwal", "68195624992799", "9036597989", "919036597989"]},
        ]
    },
    {
        "group": "Sunfra Mudah",
        "employees": [
            {"name": "Akshay", "phone": "8123466671", "aliases": ["265136954671130", "8123466671", "918123466671", "akshay (tester)"]},
            {"name": "Bharath", "phone": "7989525010", "aliases": ["bharath", "g r bharath", "166683486466210", "7989525010", "917989525010"]},
            {"name": "Krishna", "phone": "9182535260", "aliases": ["krishna", "chaitanya bandaru", "96074157031436", "9182535260", "919182535260"]},
            {"name": "Nisha", "phone": "9740828621", "aliases": ["nisha", "nisha_subbayya", "125795330740245", "9740828621", "919740828621"]},
            {"name": "Ravi Teja", "phone": "7981745785", "aliases": ["ravi teja", "ravi", "159313775583316", "7981745785", "917981745785"]},
            {"name": "Thanuja", "phone": "8978331872", "aliases": ["thanuja", "8978331872", "918978331872"]},
            {"name": "Aishwarya", "phone": "8495004826", "aliases": ["aishwarya", "8495004826", "918495004826"]},
        ]
    },
    {
        "group": "Sunfra HR Team",
        "employees": [
            {"name": "Parvati", "phone": "7995452523", "aliases": ["parvati", "paru bavisetti", "245225503076572", "7995452523", "917995452523"]},
        ]
    },
    {
        "group": "Indus",
        "employees": [
            {"name": "Girija", "phone": "8618580633", "aliases": ["girija", "girijaa dn", "133522631176396", "8618580633", "918618580633"]},
            {"name": "Jagadish", "phone": "7676711899", "aliases": ["jagadish", "7676711899", "917676711899"]},
        ]
    },
    {
        "group": "Sunfra Farms",
        "employees": [
            {"name": "Mahalakshmi", "phone": "6364817749", "aliases": ["mahalakshmi", "184791135711366", "6364817749", "916364817749"]},
        ]
    },
    {
        "group": "Sunfra Feeds",
        "employees": [
            {"name": "Venkat", "phone": "8247586860", "aliases": ["venkat", "45586833240126", "8247586860", "918247586860"]},
        ]
    },
    {
        "group": "Management Team",
        "employees": [
            {"name": "Balaji", "phone": "9493928388", "aliases": ["balaji", "balaji reddy", "242695733772318", "9493928388", "919493928388"]},
            {"name": "Prathiba", "phone": "8951520293", "aliases": ["prathiba", "8951520293", "918951520293"]},
            {"name": "Vamsi", "phone": "9677277787", "aliases": ["vamsi", "9677277787", "919677277787"]},
            {"name": "Nikhil", "phone": "9010889837", "aliases": ["nikhil", "9010889837", "919010889837"]},
            {"name": "Nani", "phone": "7204041105", "aliases": ["nani", "nani chinnam", "112300593815672", "26049698091190", "7204041105", "917204041105"]},
            {"name": "Prasad", "phone": "7204021105", "aliases": ["prasad", "vara prasad", "123622194712585", "7204021105", "917204021105"]},
        ]
    }
]

def evaluate_attendance_for_date(target_date_str: str = None) -> dict:
    if not target_date_str:
        target_date_str = date.today().strftime('%Y-%m-%d')

    db = SessionLocal()
    try:
        # Fetch raw messages for the day
        raws = db.query(RawMessage).filter(
            RawMessage.timestamp >= f"{target_date_str} 00:00:00",
            RawMessage.timestamp <= f"{target_date_str} 23:59:59"
        ).all()

        group_records = []
        tot_present = 0
        tot_half_day = 0
        tot_leave = 0
        tot_absent = 0
        tot_employees = 0

        for grp_data in COMMUNITY_EMPLOYEES:
            grp_name = grp_data["group"]
            grp_name_lower = grp_name.lower()
            emp_list = []

            for emp in grp_data["employees"]:
                tot_employees += 1
                emp_name = emp["name"]
                phone = emp["phone"]
                aliases = emp.get("aliases", [])

                # Match all messages sent by this employee
                matched_msgs = []
                for r in raws:
                    s_str = str(r.sender or "").lower()
                    g_str = str(r.group_name or "").lower()
                    
                    # Direct phone match
                    is_match = (phone in s_str) or (("91" + phone) in s_str)
                    
                    # Alias match
                    if not is_match:
                        for al in aliases:
                            if al.lower() in s_str:
                                is_match = True
                                break
                    
                    # Ensure group context if matched via non-phone alias
                    if is_match and not (phone in s_str or ("91" + phone) in s_str):
                        # If sender contains group prefix e.g. [Sunfra Mudah] or [AI & IOT]
                        if f"[{grp_name_lower}]" not in s_str and grp_name_lower not in g_str:
                            # If the message clearly belongs to another known group, skip
                            other_groups = [g["group"].lower() for g in COMMUNITY_EMPLOYEES if g["group"].lower() != grp_name_lower]
                            if any(f"[{og}]" in s_str or og in g_str for og in other_groups):
                                is_match = False
                    
                    if is_match:
                        matched_msgs.append(r)

                matched_msgs.sort(key=lambda x: x.timestamp)

                login_time = None
                logout_time = None
                leave_time = None

                login_kws = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "loging in", "sign in", "signing in", "signed in", "morning team", "good morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]
                logout_kws = ["logout", "log out", "logged out", "loged out", "logedout", "logging out", "loging out", "sign out", "signing out", "signed out", "signing off", "signed off", "bye team", "signing off team", "out", "im out", "i'm out"]
                ignore_regex = re.compile(r'\b(lunch|break|tea|snacks?|coffee|brb|afk)\b', re.IGNORECASE)
                leave_regex = re.compile(r'\b(leave|on\s+leave|taking\s+leave|leave\s+today|sick\s+leave|casual\s+leave|applied\s+leave|planned\s+leave|cl|sl|eave)\b', re.IGNORECASE)

                def is_keyword_match(text_str, kws):
                    t = text_str.strip().lower()
                    for kw in kws:
                        if t == kw or t.startswith(kw + " ") or t.startswith(kw + "\n"):
                            return True
                        if len(kw) >= 5 and t.startswith(kw):
                            return True
                    return False

                for m in matched_msgs:
                    txt = (m.raw_text or "").strip().lower()
                    
                    # Check leave keywords
                    if leave_regex.search(txt):
                        leave_time = m.timestamp

                    # Ignore lunch and intermediate break messages (using word boundary so 'team' is not matched as 'tea')
                    if ignore_regex.search(txt):
                        continue

                    # Check login keywords
                    if is_keyword_match(txt, login_kws):
                        if not login_time:
                            login_time = m.timestamp
                    # Check logout keywords
                    if is_keyword_match(txt, logout_kws):
                        logout_time = m.timestamp

                # Apply Attendance Rules:
                # 1. Leave message sent (and no login) -> On Leave 🔵
                # 2. Login before 11:00 AM + Logout -> Present 🟢
                # 3. Login after 11:00 AM -> Half Day (Late Login) 🟡
                # 4. Login <= 11:00 AM + No Logout -> Half Day (No Logout) 🟡
                # 5. No Login + Logout sent -> Half Day (No Login) 🟡
                # 6. No Login + No Logout -> Absent 🔴
                if leave_time and not login_time:
                    status_type = "on_leave"
                    status_badge = "🔵 On Leave"
                    detail = f"Leave message at {leave_time.strftime('%I:%M %p')}"
                    tot_leave += 1
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
                elif login_time.hour > 11 or (login_time.hour == 11 and login_time.minute > 0):
                    status_type = "half_day_late"
                    status_badge = "🟡 Half Day (Late Login)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} (> 11:00 AM)"
                    tot_half_day += 1
                elif not logout_time:
                    status_type = "half_day_no_logout"
                    status_badge = "🟡 Half Day (No Logout)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} | No Logout"
                    tot_half_day += 1
                else:
                    status_type = "present"
                    status_badge = "🟢 Present"
                    diff_hours = (logout_time - login_time).total_seconds() / 3600.0
                    detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')} ({diff_hours:.1f} hrs)"
                    tot_present += 1

                emp_list.append({
                    "name": emp_name,
                    "phone": phone,
                    "status_type": status_type,
                    "status_badge": status_badge,
                    "detail": detail,
                    "login_time": login_time.strftime('%I:%M %p') if login_time else "-",
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
            if emp['status_type'] == 'present':
                lines.append(f"  • *{emp['name']}*: 🟢 Present")
            elif emp['status_type'] == 'half_day_late':
                lines.append(f"  • *{emp['name']}*: 🟡 Half Day (Late Login)")
            elif emp['status_type'] == 'half_day_no_logout':
                lines.append(f"  • *{emp['name']}*: 🟡 Half Day (No Logout)")
            elif emp['status_type'] == 'half_day_no_login':
                lines.append(f"  • *{emp['name']}*: 🟡 Half Day (No Login)")
            elif emp['status_type'] == 'on_leave':
                lines.append(f"  • *{emp['name']}*: 🔵 On Leave")
            else:
                lines.append(f"  • *{emp['name']}*: 🔴 Absent")

    lines.extend([
        "\n==================================================",
        f"📊 *OVERALL STATS:*",
        f"👥 Total Employees: *{data['total_employees']}*",
        f"🟢 Present (Full Day): *{data['total_present']}*",
        f"🟡 Half Day: *{data['total_half_day']}*",
        f"🔵 On Leave: *{data.get('total_leave', 0)}*",
        f"🔴 Absent: *{data['total_absent']}*",
        "=================================================="
    ])

    return "\n".join(lines)

if __name__ == "__main__":
    report_data = evaluate_attendance_for_date()
    msg = generate_attendance_summary_message(report_data)
    print("\n" + msg)
