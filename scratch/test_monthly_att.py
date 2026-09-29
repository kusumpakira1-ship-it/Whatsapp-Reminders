import calendar
from datetime import datetime, date
import json
import os

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("backend"))

# Import COMMUNITY_EMPLOYEES and SATURDAY_OFF_EMPLOYEES
from attendance_tracker import COMMUNITY_EMPLOYEES, SATURDAY_OFF_EMPLOYEES, BASELINES_FILE

def get_monthly_working_days(year: int, month: int, grp_name: str, emp_name: str) -> int:
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

def generate_monthly_attendance_summary(target_date: date = None) -> str:
    if not target_date:
        target_date = date.today()
    
    year = target_date.year
    month = target_date.month
    month_name = target_date.strftime('%B %Y')
    num_days = calendar.monthrange(year, month)[1]

    baselines = {}
    if os.path.exists(BASELINES_FILE):
        with open(BASELINES_FILE, "r") as f:
            baselines = json.load(f)

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
            
            # Lookup absent baseline
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
    report = generate_monthly_attendance_summary()
    print(report)
