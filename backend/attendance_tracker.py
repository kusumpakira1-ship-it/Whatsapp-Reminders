import os
import re
import json
import logging
import calendar
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
            {"name": "Akshay", "phone": "9019713446", "aliases": ["akshay", "akshay i h", "akshay - a", "206686828683301", "9019713446", "919019713446"]},
            {"name": "Poornima", "phone": "7204484516", "aliases": ["poornima", "poorna", "207627359363311", "7204484516", "917204484516"]},
            {"name": "Ramya", "phone": "7019063646", "aliases": ["ramya", "259149770277018", "7019063646", "917019063646"]},
        ]
    },
    {
        "group": "Sunfra AI",
        "group_jids": ["120363429752031220", "ai attendance", "ai", "sunfra ai"],
        "employees": [
            {"name": "Kusum", "phone": "7975209680", "aliases": ["kusum", "kusumpakira", "7975209680", "917975209680", "7259510983", "917259510983", "183300681367688"]},
            {"name": "Shareef", "phone": "6303896125", "aliases": ["shareef", "sharif", "sk md shareef", "6303896125", "916303896125", "207399910654120", "207399910654120@lid"]},
            {"name": "Kaveri", "phone": "8790550230", "aliases": ["kaveri", "ss kaveri", "rivi", "8790550230", "918790550230", "1864183640196", "1864183640196@lid"]},
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
        "group_jids": ["120363428872126006", "jataayu attendance"],
        "excluded_kws": ["updates", "digital team", "jewellers", "bongo", "bbb"],
        "employees": [
            {"name": "Roopa", "phone": "8686856459", "aliases": ["roopa", "rupa", "rupakamalapuram", "147635256201243", "8686856459", "918686856459"]},
        ]
    },
    {
        "group": "Sunfra Corporate",
        "group_jids": ["120363428349268084", "sunfra corporate"],
        "excluded_kws": ["p&l", "p & l", "payments", "sales", "receivables"],
        "employees": [
            {"name": "Divya", "phone": "9381255565", "aliases": ["divya", "9381255565", "919381255565", "56556230058144"]},
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
            {"name": "Thanuja", "phone": "8978331872", "aliases": ["thanuja", "thota thanuja", "125889819983939", "8978331872", "918978331872"]},
            {"name": "Aishwarya", "phone": "8495004826", "aliases": ["aishwarya", "20551502401730", "8495004826", "918495004826"]},
            {"name": "Lakshmi", "phone": "137812783452345", "aliases": ["lakshmi", "lakshmy", "137812783452345", "137812783452345@lid"]},
        ]
    },
    {
        "group": "Sunfra HR Team",
        "group_jids": ["120363431222906850", "sunfra hr team"],
        "employees": [
            {"name": "Bhanushree", "phone": "9901497574", "aliases": ["bhanushree", "bhanushree n.t", "bhanu", "81991244460218", "9901497574", "919901497574"]},
        ]
    },
    {
        "group": "Indus",
        "group_jids": ["120363431080782528", "indus"],
        "employees": [
            {"name": "Girija", "phone": "8618580633", "aliases": ["girija", "girijaa dn", "133522631176396", "8618580633", "918618580633"]},
            {"name": "Jagadish", "phone": "7676711899", "aliases": ["jagadish", "7676711899", "917676711899"]},
            {"name": "RaviTeja", "phone": "9535843064", "aliases": ["raviteja", "ravi teja", "ravi tej v", "ravi tej", "51110463168709", "51110463168709@lid", "9535843064", "919535843064"]},
        ]
    },
    {
        "group": "Sunfra Farms",
        "group_jids": ["120363429481469212", "sunfra farms"],
        "excluded_kws": ["payment", "payments", "accounts", "gate manager", "feed formula", "raw material", "prices", "team", "sales", "receivables"],
        "employees": [
            {"name": "Mahalakshmi", "phone": "6364817749", "aliases": ["mahalakshmi", "184791135711366", "6364817749", "916364817749"]},
            {"name": "Sai Kishore", "phone": "9398796968", "aliases": ["sai kishore", "sai", "kishore", "9398796968", "919398796968"], "not_started_yet": True},
        ]
    },
    {
        "group": "Sunfra Feeds",
        "group_jids": ["120363413108636132", "sunfra feeds"],
        "excluded_kws": ["summary", "accounts", "sales", "plant", "payments", "doctor", "formula", "prices", "orders"],
        "employees": [
            {"name": "Venkat", "phone": "8247586860", "aliases": ["venkat", "45586833240126", "8247586860", "918247586860"]},
        ]
    },
    {
        "group": "Management Team",
        "group_jids": ["120363410684018393", "management team"],
        "excluded_kws": ["balaji team", "ai & iot", "ai iot", "digital team", "final year", "hyperscale", "p&l", "rule book", "feed plant", "formula"],
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

# Employees who have Day Off on Saturdays (All others have normal working Saturdays)
SATURDAY_OFF_EMPLOYEES = {
    # Sunfra Mudah
    ("Sunfra Mudah", "Aishwarya"),
    ("Sunfra Mudah", "Bharath"),
    ("Sunfra Mudah", "Krishna"),
    ("Sunfra Mudah", "Lakshmi"),
    ("Sunfra Mudah", "Nisha"),
    ("Sunfra Mudah", "Thanuja"),
    # Sunfra OLX CEE
    ("Sunfra OLX CEE", "Prasanna"),
    ("Sunfra OLX CEE", "Yashaswini"),
    # Sunfra Corporate
    ("Sunfra Corporate", "Prajwal"),
    # Tendered
    ("Tendered", "Ganga"),
}

def evaluate_attendance_for_date(target_date_str: str = None, is_eod_check: bool = False) -> dict:
    if not target_date_str:
        target_date_str = date.today().strftime('%Y-%m-%d')

    from datetime import timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    today_str = now_ist.date().strftime('%Y-%m-%d')
    is_eod = is_eod_check or (target_date_str < today_str) or (target_date_str == today_str and (now_ist.hour == 23 and now_ist.minute >= 45))

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

        # Also query local SQLite fallback database to ensure zero lost messages
        try:
            import sqlite3
            sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_reminders.sqlite")
            if os.path.exists(sqlite_path):
                sconn = sqlite3.connect(sqlite_path)
                scur = sconn.cursor()
                srows = scur.execute(
                    "SELECT sender, group_name, raw_text, timestamp FROM sunfra_raw_messages WHERE timestamp >= ? AND timestamp <= ?",
                    (f"{target_date_str} 00:00:00", f"{target_date_str} 23:59:59")
                ).fetchall()
                for sr in srows:
                    ts_val = sr[3]
                    if isinstance(ts_val, str):
                        try:
                            ts_val = datetime.strptime(ts_val[:19], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    raws.append(SimpleMsg(sr[0], sr[1], sr[2], ts_val))
                sconn.close()
        except Exception as sqle:
            logger.warning(f"Failed to query SQLite fallback in attendance_tracker: {sqle}")

        group_records = []
        tot_present = 0
        tot_half_day_present = 0
        tot_half_day = 0
        tot_leave = 0
        tot_absent = 0
        tot_day_off = 0
        tot_employees = 0

        is_saturday = datetime.strptime(target_date_str, '%Y-%m-%d').weekday() == 5

        for grp_data in COMMUNITY_EMPLOYEES:
            grp_name = grp_data["group"]
            grp_name_lower = grp_name.lower()
            grp_jids = [j.lower() for j in grp_data.get("group_jids", [])]
            grp_excluded_kws = [k.lower() for k in grp_data.get("excluded_kws", [])]
            emp_list = []

            for emp in grp_data["employees"]:
                tot_employees += 1
                emp_name = emp["name"]
                phone = emp["phone"]
                aliases = emp.get("aliases", [])

                grp_target_name = grp_name.lower()
                grp_jids_lower = [j.lower() for j in grp_data.get("group_jids", [])] + [grp_target_name]

                # Match messages sent by this employee in their specific group
                matched_msgs = []
                for r in raws:
                    s_str = str(r.sender or "").strip().lower()
                    g_str = str(r.group_name or "").strip().lower()
                    
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
                    
                    if not is_sender_match:
                        continue

                    # Check if message is in the employee's designated group
                    matches_jid = any(jid in g_str or f"[{jid}]" in s_str for jid in grp_jids_lower)
                    matches_name = any(name in g_str or f"[{name}]" in s_str for name in grp_jids_lower)
                    if not (matches_jid or matches_name):
                        continue

                    # Check if message matches any excluded keywords
                    is_excluded = False
                    for ex in grp_excluded_kws:
                        if ex in g_str or f"[{ex}" in s_str or f"{ex}]" in s_str:
                            is_excluded = True
                            break
                    if is_excluded:
                        continue

                    matched_msgs.append(r)

                matched_msgs.sort(key=lambda x: str(x.timestamp))

                login_time = None
                logout_time = None
                leave_time = None
                lunch_start_time = None
                lunch_end_time = None
                break_start_time = None
                break_end_time = None
                total_break_seconds = 0
                curr_break_start = None
                last_break_type = None

                login_kws = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "loging in", "sign in", "signing in", "signed in", "sing in", "singin", "singed in", "morning team", "good morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]
                logout_kws = ["logout", "log out", "logged out", "loged out", "logedout", "logging out", "loging out", "sign out", "signout", "signing out", "signed out", "sign off", "signoff", "signing off", "signed off", "bye team", "bye all", "signing off team", "out", "im out", "i'm out"]
                lunch_kws = ["lunch", "lunch break", "out for lunch", "going for lunch", "leaving for lunch"]
                break_kws = ["break", "tea", "tea break", "tea-break", "snacks", "coffee", "brb", "afk", "taking break", "on break", "short break"]
                break_start_kws = lunch_kws + break_kws
                break_end_kws = ["back", "return", "returned", "back to work", "rejoined"]
                leave_regex = re.compile(r'\b(leave|on\s+leave|taking\s+leave|leave\s+today|sick\s+leave|casual\s+leave|applied\s+leave|planned\s+leave|cl|sl|eave)\b', re.IGNORECASE)
                half_day_leave_regex = re.compile(r'\b(half\s*day\s*leave|half\s*day|1/2\s*day|half\s*cl|half\s*sl|cl\s*half|sl\s*half|half\s*sick|half\s*casual)\b', re.IGNORECASE)
                is_half_day_leave = False
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
                    if any(t.startswith(prefix) for prefix in ["🌾", "🐔", "⚡", "🚨", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "📊", "📋"]) or "report" in t or "eod summary" in t:
                        return False
                    lines = [l.strip() for l in t.split('\n') if l.strip()]
                    for line in lines:
                        for kw in kws:
                            if re.search(r'\b' + re.escape(kw) + r'\b', line):
                                return True
                    return False

                for m in matched_msgs:
                    txt = (m.raw_text or "").strip().lower()
                    
                    # Check leave keywords
                    if leave_regex.search(txt):
                        leave_time = m.timestamp
                    if half_day_leave_regex.search(txt):
                        is_half_day_leave = True
                        leave_time = m.timestamp

                    # Break and lunch evaluations removed per user request (only login and logout evaluated)

                    # Check login keywords
                    if is_keyword_match(txt, login_kws):
                        if not login_time:
                            login_time = m.timestamp
                    # Check logout keywords
                    if is_keyword_match(txt, logout_kws) or logout_regex.search(txt):
                        logout_time = m.timestamp

                # Admin Approved Login Time Override for forgotten login
                for m in matched_msgs:
                    txt_low = (m.raw_text or "").lower()
                    if any(k in txt_low for k in ["forgot", "forget", "missed", "late login"]) and any(k in txt_low for k in ["came", "in at", "reached", "login at", "came at"]):
                        time_match = re.search(r'\b(\d{1,2})[:\.](\d{2})\b', txt_low)
                        if time_match:
                            req_h = int(time_match.group(1))
                            req_m = int(time_match.group(2))
                            if "pm" in txt_low and req_h < 12: req_h += 12
                            elif "am" in txt_low and req_h == 12: req_h = 0
                            
                            is_approved = any(any(app in (r.raw_text or "").lower() for app in ["approved", "approve", "approved login"]) for r in raws)
                            if is_approved:
                                login_time = m.timestamp.replace(hour=req_h, minute=req_m, second=0)
                                logger.info(f"Admin approved login time for {emp_name}: {login_time}")
                                break

                # Check Divya presence if mentioned by name e.g. "Divya ma'am came" in Sunfra Corporate
                if emp_name == "Divya" and not login_time:
                    for r in raws:
                        g_str = str(r.group_name or "").lower()
                        s_str = str(r.sender or "").lower()
                        if any(k in g_str or f"[{k}]" in s_str for k in ["120363428349268084", "sunfra corporate"]) and "p&l" not in g_str and "[sunfra corporate p&l]" not in s_str:
                            raw_low = (r.raw_text or "").lower()
                            if "divya" in raw_low and ("came" in raw_low or "in" in raw_low or "present" in raw_low):
                                login_time = r.timestamp
                                break

                # Prasad Leave override in Management Team
                if emp_name == "Prasad" and not leave_time:
                    for r in raws:
                        g_str = str(r.group_name or "").lower()
                        s_str = str(r.sender or "").lower()
                        if any(k in g_str or f"[{k}]" in s_str for k in ["120363410684018393", "management team"]) and "balaji team" not in g_str:
                            raw_low = (r.raw_text or "").lower()
                            if "prasad" in raw_low and ("leave" in raw_low or "on leave" in raw_low):
                                leave_time = r.timestamp
                                break

                # User confirmation override: Balaji logged in on 2026-09-19 or 2026-10-29
                if emp_name == "Balaji" and not login_time and target_date_str == "2026-09-19":
                    login_time = datetime.strptime(f"{target_date_str} 09:00:00", "%Y-%m-%d %H:%M:%S")
                if emp_name == "Balaji" and not login_time and target_date_str == "2026-10-29":
                    login_time = datetime.strptime(f"{target_date_str} 10:47:00", "%Y-%m-%d %H:%M:%S")

                # Fallback login time for active employees who posted work/break messages today (not for leave messages)
                if not login_time and not leave_time and matched_msgs:
                    login_time = matched_msgs[0].timestamp

                gross_hours = 0.0
                net_hours = 0.0
                if login_time and logout_time:
                    gross_seconds = (logout_time - login_time).total_seconds()
                    gross_hours = gross_seconds / 3600.0
                    net_hours = gross_hours
                elif login_time:
                    gross_seconds = (datetime.now() - login_time).total_seconds() if target_date_str == date.today().strftime('%Y-%m-%d') else 0.0
                    net_hours = gross_seconds / 3600.0

                # Late login threshold is 11:00 AM (login posted after 11:00 AM)
                is_late = login_time and (login_time.hour > 11 or (login_time.hour == 11 and login_time.minute > 0))
                is_sat_off = is_saturday and (grp_name, emp_name) in SATURDAY_OFF_EMPLOYEES

                # Apply Attendance Rules (Login & Logout based):
                if is_sat_off:
                    if login_time and net_hours >= 8.0:
                        status_type = "present"
                        status_badge = "🟢 Present"
                        detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')}" if (login_time and logout_time) else f"Login at {login_time.strftime('%I:%M %p')} ({round(net_hours, 1)} hrs)"
                        tot_present += 1
                    elif login_time and net_hours >= 4.5:
                        status_type = "half_day_weekend_work"
                        status_badge = "🟡 Half Day Present"
                        detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')}" if (login_time and logout_time) else f"Login at {login_time.strftime('%I:%M %p')} ({round(net_hours, 1)} hrs)"
                        tot_half_day += 1
                        tot_half_day_present += 1
                    else:
                        status_type = "day_off"
                        status_badge = "⚪ Day Off"
                        detail = "Saturday Day Off"
                        tot_day_off += 1
                elif is_half_day_leave:
                    if login_time:
                        status_type = "half_day_approved_leave"
                        status_badge = "🟡 Half Day (Half Day Leave)"
                        detail = f"Applied Half Day Leave (Logged in at {login_time.strftime('%I:%M %p')})"
                        tot_half_day += 1
                    else:
                        status_type = "on_leave"
                        status_badge = "🔵 On Leave"
                        detail = "Half Day Leave requested"
                        tot_leave += 1
                elif leave_time and not login_time:
                    status_type = "on_leave"
                    status_badge = "🔵 On Leave"
                    detail = f"Leave message at {leave_time.strftime('%I:%M %p')}"
                    tot_leave += 1
                elif emp.get("not_started_yet") and not login_time and not logout_time:
                    # Check if employee has ever logged in previously
                    has_prior_login = False
                    try:
                        prior = db.query(DailyAttendance).filter(
                            DailyAttendance.employee_name == emp_name,
                            DailyAttendance.login_time.isnot(None)
                        ).first()
                        if prior:
                            has_prior_login = True
                    except Exception:
                        pass

                    if not has_prior_login:
                        status_type = "not_started"
                        status_badge = "-"
                        detail = "Not started yet"
                        tot_employees = max(0, tot_employees - 1)
                    else:
                        status_type = "absent"
                        status_badge = "🔴 Absent"
                        detail = "No login or logout message"
                        tot_absent += 1
                elif not login_time and not logout_time:
                    status_type = "absent"
                    status_badge = "🔴 Absent"
                    detail = "No login or logout message"
                    tot_absent += 1
                elif emp_name == "Ramya" or is_late:
                    tot_half_day += 1
                    if login_time and logout_time:
                        status_type = "half_day_late"
                        status_badge = "🟡 Half Day (Late Login)"
                        detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')}"
                    elif is_eod and not logout_time:
                        # At 11:45 PM EOD lock (or past dates): late login and forgot to log out
                        status_type = "half_day_late_no_logout"
                        status_badge = "🟡 Half Day (Late Login & No Logout)"
                        detail = f"Login at {login_time.strftime('%I:%M %p')} (Late & No Logout)" if login_time else "Late Login & No Logout"
                    else:
                        # Before 11:45 PM EOD lock on current day
                        status_type = "half_day_late"
                        status_badge = "🟡 Half Day (Late Login)"
                        detail = f"Login at {login_time.strftime('%I:%M %p')}" if login_time else "Late Login"
                elif is_eod and not logout_time:
                    # Logged in on time, but forgot to log out by 11:45 PM EOD -> Half Day (No Logout)
                    status_type = "half_day_no_logout"
                    status_badge = "🟡 Half Day (No Logout)"
                    detail = f"Login at {login_time.strftime('%I:%M %p')} (No Logout)"
                    tot_half_day += 1
                elif (login_time and logout_time and net_hours < 6.5) or (emp_name == "Mahalakshmi" and target_date_str == "2026-10-29"):
                    # Early logout / half day hours (e.g. Mahalakshmi 10:15 AM - 02:50 PM = 4.58 hrs)
                    status_type = "half_day_early_logout"
                    status_badge = "🟡 Half Day Present"
                    detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')}"
                    tot_half_day += 1
                    tot_half_day_present += 1
                else:
                    # Valid login & logout (or active login before EOD) -> Full Day Present
                    status_type = "present"
                    status_badge = "🟢 Present"
                    detail = f"{login_time.strftime('%I:%M %p')} - {logout_time.strftime('%I:%M %p')}" if (login_time and logout_time) else (f"Login at {login_time.strftime('%I:%M %p')}" if login_time else "Present")
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
            
            # Preserves configured order in COMMUNITY_EMPLOYEES (e.g. Kusum, Shareef, Kaveri)

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
            "total_day_off": tot_day_off,
            "total_absent": tot_absent,
            "groups": group_records
        }
    finally:
        db.close()

BASELINES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employee_monthly_leave_baselines.json")
PROCESSED_DATES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_attendance_dates.json")


def check_and_reset_monthly_baselines(target_month_str: str, baselines: dict) -> tuple:
    """Resets employee absence baselines to 0.0 at the start of a new month."""
    stored_month = baselines.get("_current_month")
    if stored_month != target_month_str:
        logger.info(f"New month detected ({target_month_str} vs {stored_month}). Resetting employee absence baselines to 0.0.")
        new_baselines = {"_current_month": target_month_str}
        for k, v in baselines.items():
            if k == "_current_month":
                continue
            new_baselines[k] = 0.0
        return new_baselines, True
    return baselines, False


def update_daily_absence_increments(data: dict):
    """Automatically increments employee monthly absence baseline when daily attendance is finalized for a new date."""
    target_date_str = data.get("date")
    if not target_date_str:
        return

    processed = set()
    try:
        if os.path.exists(PROCESSED_DATES_FILE):
            with open(PROCESSED_DATES_FILE, "r") as f:
                processed = set(json.load(f))
    except Exception:
        processed = set()

    if target_date_str in processed:
        return

    # Skip historical dates on or before 2026-09-21 (since baselines already include up to 21 Sep 2026)
    if target_date_str <= "2026-09-21":
        processed.add(target_date_str)
        try:
            with open(PROCESSED_DATES_FILE, "w") as f:
                json.dump(list(processed), f)
        except Exception:
            pass
        return

    baselines = {}
    try:
        if os.path.exists(BASELINES_FILE):
            with open(BASELINES_FILE, "r") as f:
                baselines = json.load(f)

        target_month_str = target_date_str[:7]
        baselines, _ = check_and_reset_monthly_baselines(target_month_str, baselines)

        for g in data.get("groups", []):
            grp_name = g.get("group_name", "")
            for emp in g.get("employees", []):
                emp_name = emp.get("name", "")
                status_type = emp.get("status_type", "")
                badge = emp.get("status_badge", "")

                if target_date_str == "2026-10-29" and emp_name == "Mahalakshmi":
                    continue  # Already included as 0.5 per user directive

                inc = 0.0
                if status_type in ["day_off", "half_day_weekend_work", "not_started"]:
                    inc = 0.0
                elif "Absent" in badge or "On Leave" in badge or "Leave" in badge or status_type in ["absent", "on_leave"]:
                    inc = 1.0
                elif "Half Day" in badge or status_type.startswith("half_day"):
                    inc = 0.5

                if inc > 0:
                    key = f"{emp_name}_{grp_name}"
                    if key not in baselines:
                        key = emp_name
                    current_val = baselines.get(key, 0.0)
                    if current_val == "-" or current_val is None:
                        current_val = 0.0
                    baselines[key] = round(current_val + inc, 1)

        with open(BASELINES_FILE, "w") as f:
            json.dump(baselines, f, indent=2)

        processed.add(target_date_str)
        with open(PROCESSED_DATES_FILE, "w") as f:
            json.dump(list(processed), f)
        logger.info(f"Successfully updated monthly absence baselines for {target_date_str}.")
    except Exception as e:
        logger.error(f"Error updating daily absence increments: {e}")


def get_employee_absence_label(emp_name: str, grp_name: str) -> str:
    """Returns the monthly absence/leave count label string (e.g. ' (Ab - 3)' or ' (Ab - 2.5)')."""
    try:
        baselines = {}
        if os.path.exists(BASELINES_FILE):
            with open(BASELINES_FILE, "r") as f:
                baselines = json.load(f)
        
        current_month_str = datetime.now().strftime("%Y-%m")
        baselines, reset_occurred = check_and_reset_monthly_baselines(current_month_str, baselines)
        if reset_occurred:
            try:
                with open(BASELINES_FILE, "w") as f:
                    json.dump(baselines, f, indent=2)
            except Exception:
                pass
        
        key = f"{emp_name}_{grp_name}"
        if key not in baselines and emp_name in baselines:
            key = emp_name
            
        cnt = baselines.get(key, 0.0)
        if cnt == "-" or cnt is None:
            return " (Ab - -)"
        cnt_str = str(int(cnt)) if cnt == int(cnt) else str(cnt)
        return f" (Ab - {cnt_str})"
    except Exception:
        pass
    return " (Ab - 0)"

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
            abs_lbl = get_employee_absence_label(emp['name'], g['group_name'])
            lines.append(f"  • *{emp['name']}*{abs_lbl} : {badge}")

    stats = [
        "\n==================================================",
        f"📊 *OVERALL STATS:*",
        f"👥 Total Employees: *{data['total_employees']}*",
        f"🟢 Present (Full Day): *{data['total_present']}*",
        f"🟡 Half Day: *{data['total_half_day']}*",
        f"🔵 On Leave: *{data.get('total_leave', 0)}*",
    ]
    if data.get('total_day_off', 0) > 0:
        stats.append(f"⚪ Day Off: *{data['total_day_off']}*")
    stats.extend([
        f"🔴 Absent: *{data['total_absent']}*",
        "=================================================="
    ])
    lines.extend(stats)

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
            abs_lbl = get_employee_absence_label(emp['name'], g['group_name'])
            lines.append(f"  • *{emp['name']}*{abs_lbl} : {badge}")

        company_msgs[g['group_name']] = "\n".join(lines)
    return company_msgs

def get_monthly_working_days(year: int, month: int, grp_name: str, emp_name: str) -> int:
    """Calculates working days for a given employee in a specific month/year based on Sunday Off and Saturday Off rules."""
    num_days = calendar.monthrange(year, month)[1]
    is_sat_off = (grp_name, emp_name) in SATURDAY_OFF_EMPLOYEES
    working_days = 0
    for day in range(1, num_days + 1):
        dt = date(year, month, day)
        w = dt.weekday() # Monday=0 ... Saturday=5, Sunday=6
        if w == 6: # Sunday
            continue
        if w == 5 and is_sat_off: # Saturday off
            continue
        working_days += 1
    return working_days

def generate_monthly_attendance_summary_message(target_date: date = None) -> str:
    """Generates the Monthly Attendance Report across all departments and employees."""
    if not target_date:
        target_date = date.today()
    
    year = target_date.year
    month = target_date.month
    month_name = target_date.strftime('%B %Y')
    num_days = calendar.monthrange(year, month)[1]

    baselines = {}
    if os.path.exists(BASELINES_FILE):
        try:
            with open(BASELINES_FILE, "r") as f:
                baselines = json.load(f)
        except Exception:
            baselines = {}

    lines = [
        f"📋 *MONTHLY ATTENDANCE REPORT*",
        f"🗓️ *Period:* {month_name} (Total Days: {num_days})",
        "=================================================="
    ]

    tot_working_days_all = 0
    tot_present_days_all = 0.0
    tot_absent_days_all = 0.0
    tot_emp_count = 0

    for grp_data in COMMUNITY_EMPLOYEES:
        grp_name = grp_data["group"]
        grp_lines = [f"\n🏢 *{grp_name}*"]
        
        for emp in grp_data["employees"]:
            tot_emp_count += 1
            emp_name = emp["name"]
            
            w_days = get_monthly_working_days(year, month, grp_name, emp_name)
            
            key = f"{emp_name}_{grp_name}"
            if key not in baselines:
                key = emp_name
            
            absent_days = float(baselines.get(key, 0.0))
            present_days = max(0.0, w_days - absent_days)
            
            tot_working_days_all += w_days
            tot_present_days_all += present_days
            tot_absent_days_all += absent_days

            abs_str = f"{absent_days:g}"
            pres_str = f"{present_days:g}"

            is_sat_off = (grp_name, emp_name) in SATURDAY_OFF_EMPLOYEES
            schedule_note = " (5-day week)" if is_sat_off else ""
            
            grp_lines.append(f"  • *{emp_name}*: *{pres_str}* Pres / *{w_days}* Wrk ({abs_str} Ab){schedule_note}")

        lines.extend(grp_lines)

    lines.extend([
        "\n==================================================",
        f"📊 *OVERALL MONTHLY SUMMARY:*",
        f"👥 Total Employees: *{tot_emp_count}*",
        f"🟢 Total Present Days: *{tot_present_days_all:g}*",
        f"🔴 Total Absent/Leave Days: *{tot_absent_days_all:g}*",
        f"💼 Total Working Days Pool: *{tot_working_days_all}*",
        "=================================================="
    ])

    return "\n".join(lines)

if __name__ == "__main__":
    report_data = evaluate_attendance_for_date()
    msg = generate_attendance_summary_message(report_data)
    print("\n" + msg)
