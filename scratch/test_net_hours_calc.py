import sys
import os
import re
from datetime import datetime

sys.path.append("backend")

from database import get_db_session
from models import RawMessage
from attendance_tracker import COMMUNITY_EMPLOYEES

db = get_db_session()
try:
    target_date_str = "2026-09-09"
    raws = db.query(RawMessage).filter(
        RawMessage.timestamp >= f"{target_date_str} 00:00:00",
        RawMessage.timestamp <= f"{target_date_str} 23:59:59"
    ).all()

    login_kws = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "loging in", "sign in", "signing in", "signed in", "morning team", "good morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]
    logout_kws = ["logout", "log out", "logged out", "loged out", "logedout", "logging out", "loging out", "sign out", "signing out", "signed out", "signing off", "signed off", "bye team", "signing off team", "out", "im out", "i'm out"]
    break_start_kws = ["lunch", "lunch break", "tea", "tea break", "break", "snacks", "coffee", "brb", "afk"]
    break_end_kws = ["back", "return", "returned", "back to work", "rejoined"]
    leave_regex = re.compile(r'\b(leave|on\s+leave|taking\s+leave|leave\s+today|sick\s+leave|casual\s+leave|applied\s+leave|planned\s+leave|cl|sl|eave)\b', re.IGNORECASE)

    def is_keyword_match(text_str, kws):
        t = text_str.strip().lower()
        for kw in kws:
            if t == kw or t.startswith(kw + " ") or t.startswith(kw + "\n"):
                return True
            if len(kw) >= 5 and t.startswith(kw):
                return True
        return False

    print(f"--- NET HOURS CALCULATION FOR {target_date_str} ---")

    for grp in COMMUNITY_EMPLOYEES:
        grp_name = grp["group"]
        grp_name_lower = grp_name.lower()
        for emp in grp["employees"]:
            emp_name = emp["name"]
            phone = emp["phone"]
            aliases = emp.get("aliases", [])

            matched_msgs = []
            for r in raws:
                s_str = str(r.sender or "").lower()
                g_str = str(r.group_name or "").lower()
                is_match = (phone in s_str) or (("91" + phone) in s_str)
                if not is_match:
                    for al in aliases:
                        if al.lower() in s_str:
                            is_match = True
                            break
                if is_match and not (phone in s_str or ("91" + phone) in s_str):
                    if f"[{grp_name_lower}]" not in s_str and grp_name_lower not in g_str:
                        other_groups = [g["group"].lower() for g in COMMUNITY_EMPLOYEES if g["group"].lower() != grp_name_lower]
                        if any(f"[{og}]" in s_str or og in g_str for og in other_groups):
                            is_match = False
                if is_match:
                    matched_msgs.append(r)

            if not matched_msgs:
                continue

            matched_msgs.sort(key=lambda x: x.timestamp)

            login_time = None
            logout_time = None
            leave_time = None
            total_break_seconds = 0
            curr_break_start = None

            for m in matched_msgs:
                txt = (m.raw_text or "").strip().lower()
                
                if leave_regex.search(txt):
                    leave_time = m.timestamp

                # Break start
                if is_keyword_match(txt, break_start_kws):
                    if not curr_break_start:
                        curr_break_start = m.timestamp
                    continue

                # Break end
                if is_keyword_match(txt, break_end_kws):
                    if curr_break_start:
                        break_sec = (m.timestamp - curr_break_start).total_seconds()
                        total_break_seconds += break_sec
                        curr_break_start = None
                    continue

                if is_keyword_match(txt, login_kws):
                    if not login_time:
                        login_time = m.timestamp

                if is_keyword_match(txt, logout_kws):
                    logout_time = m.timestamp

            if curr_break_start and logout_time and logout_time > curr_break_start:
                # Fallback: if break start was recorded but no back message before logout, add 45 mins
                total_break_seconds += 2700

            gross_hours = 0.0
            net_hours = 0.0
            if login_time and logout_time:
                gross_seconds = (logout_time - login_time).total_seconds()
                gross_hours = gross_seconds / 3600.0
                net_seconds = max(0, gross_seconds - total_break_seconds)
                net_hours = net_seconds / 3600.0

            # Rule check
            if leave_time and login_time:
                status = "⚪ Half Day Present"
            elif login_time and logout_time:
                if net_hours >= 8.0:
                    status = "🟢 Present (8+ Hrs)"
                else:
                    status = "🟡 Half Day (Short Hours < 8 Hrs)"
            elif login_time and not logout_time:
                status = "🟡 Half Day (No Logout)"
            elif not login_time and logout_time:
                status = "🟡 Half Day (No Login)"
            elif leave_time:
                status = "🔵 On Leave"
            else:
                status = "🔴 Absent"

            print(f"[{grp_name}] {emp_name}: {status} | Gross: {gross_hours:.2f}h | Breaks: {total_break_seconds/60:.0f}m | Net Work: {net_hours:.2f}h")

finally:
    db.close()
