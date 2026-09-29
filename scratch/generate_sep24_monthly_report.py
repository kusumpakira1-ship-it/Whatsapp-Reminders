import json
import os
import calendar
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import date

# The exact baselines up to 24 Sep 2026 provided by the user
EXACT_24SEP_BASELINES = {
    "Akshay_AI & IOT": 3.0,
    "Kusum": 2.0,
    "Poornima": 3.0,
    "Ramya": 3.5,
    "Asif": 0.0,
    "Prasanna": 0.0,
    "Yashaswini": 1.0,
    "Roopa": 1.5,
    "Divya": 1.5,
    "Prajwal": 2.0,
    "Aishwarya": 2.0,
    "Akshay_Sunfra Mudah": 1.0,
    "Bharath": 0.0,
    "Krishna": 2.0,
    "Lakshmi": 0.0,
    "Nisha": 1.0,
    "Ravi Teja": 1.5,
    "Thanuja": 2.5,
    "Bhanushree": 0.0,
    "Parvati": 0.0,
    "Girija": 10.5,
    "Jagadish": 2.0,
    "Mahalakshmi": 1.0,
    "Venkat": 3.0,
    "Balaji": 0.0,
    "Nani": 0.0,
    "Nikhil": 0.0,
    "Prasad": 2.5,
    "Prathiba": 0.5,
    "Vamsi": 0.0,
    "Ganga": 0.0
}

# Save these exact baselines to employee_monthly_leave_baselines.json
for path in [
    "backend/employee_monthly_leave_baselines.json",
    "backend/backend/employee_monthly_leave_baselines.json"
]:
    with open(path, "w") as f:
        json.dump(EXACT_24SEP_BASELINES, f, indent=2)
print("Updated employee_monthly_leave_baselines.json with exact 24 Sep baselines.")

SATURDAY_OFF_EMPLOYEES = {
    ("Sunfra Mudah", "Aishwarya"),
    ("Sunfra Mudah", "Bharath"),
    ("Sunfra Mudah", "Krishna"),
    ("Sunfra Mudah", "Lakshmi"),
    ("Sunfra Mudah", "Nisha"),
    ("Sunfra Mudah", "Ravi Teja"),
    ("Sunfra Mudah", "Thanuja"),
    ("Sunfra OLX CEE", "Prasanna"),
    ("Sunfra OLX CEE", "Yashaswini"),
    ("Sunfra Corporate", "Prajwal"),
    ("Tendered", "Ganga"),
}

COMMUNITY_EMPLOYEES = [
    {
        "group": "AI & IOT",
        "employees": ["Kusum", "Poornima", "Akshay", "Ramya"]
    },
    {
        "group": "Sunfra OLX CEE",
        "employees": ["Asif", "Prasanna", "Yashaswini"]
    },
    {
        "group": "Jataayu",
        "employees": ["Roopa"]
    },
    {
        "group": "Sunfra Corporate",
        "employees": ["Divya", "Prajwal"]
    },
    {
        "group": "Sunfra Mudah",
        "employees": ["Akshay", "Bharath", "Krishna", "Nisha", "Ravi Teja", "Thanuja", "Aishwarya", "Lakshmi"]
    },
    {
        "group": "Sunfra HR Team",
        "employees": ["Parvati", "Bhanushree"]
    },
    {
        "group": "Indus",
        "employees": ["Girija", "Jagadish"]
    },
    {
        "group": "Sunfra Farms",
        "employees": ["Mahalakshmi"]
    },
    {
        "group": "Sunfra Feeds",
        "employees": ["Venkat"]
    },
    {
        "group": "Management Team",
        "employees": ["Balaji", "Prathiba", "Vamsi", "Nikhil", "Nani", "Prasad"]
    },
    {
        "group": "Tendered",
        "employees": ["Ganga"]
    }
]

# Calculate working days for Sep 1 to Sep 24, 2026 (24 calendar days)
def get_working_days_till_24sep(grp_name, emp_name):
    is_sat_off = (grp_name, emp_name) in SATURDAY_OFF_EMPLOYEES
    working_days = 0
    for day in range(1, 25): # 1 to 24
        dt = date(2026, 9, day)
        w = dt.weekday() # Monday=0...Sat=5, Sun=6
        if w == 6: # Sunday
            continue
        if w == 5 and is_sat_off: # Saturday off
            continue
        working_days += 1
    return working_days

lines = [
    "📋 *MONTHLY ATTENDANCE REPORT*",
    "🗓️ *Period:* 01 Sep 2026 – 24 Sep 2026 (Total Days: 24)",
    "=================================================="
]

tot_working_days_all = 0
tot_present_days_all = 0.0
tot_absent_days_all = 0.0
tot_emp_count = 0

for grp_data in COMMUNITY_EMPLOYEES:
    grp_name = grp_data["group"]
    grp_lines = [f"\n🏢 *{grp_name}*"]
    
    for emp_name in grp_data["employees"]:
        tot_emp_count += 1
        w_days = get_working_days_till_24sep(grp_name, emp_name)
        
        key = f"{emp_name}_{grp_name}"
        if key not in EXACT_24SEP_BASELINES:
            key = emp_name
        
        absent_days = float(EXACT_24SEP_BASELINES.get(key, 0.0))
        present_days = max(0.0, w_days - absent_days)
        
        tot_working_days_all += w_days
        tot_present_days_all += present_days
        tot_absent_days_all += absent_days

        abs_str = f"{absent_days:g}"
        pres_str = f"{present_days:g}"

        is_sat_off = (grp_name, emp_name) in SATURDAY_OFF_EMPLOYEES
        schedule_note = " (5-day week)" if is_sat_off else ""
        
        grp_lines.append(f"  • *{emp_name}*: *{pres_str}* Pres / *{w_days}* Wrk ({abs_str} Ab Leaves){schedule_note}")

    lines.extend(grp_lines)

lines.extend([
    "\n==================================================",
    f"📊 *OVERALL MONTHLY SUMMARY (1 TO 24 SEP):*",
    f"👥 Total Employees: *{tot_emp_count}*",
    f"🟢 Total Present Days: *{tot_present_days_all:g}*",
    f"🔴 Total Absent/Leave Days: *{tot_absent_days_all:g}*",
    f"💼 Total Working Days Pool: *{tot_working_days_all}*",
    "=================================================="
])

report_str = "\n".join(lines)

with open("scratch/sep24_monthly_report.txt", "w", encoding="utf-8") as f:
    f.write(report_str)

print(report_str)
