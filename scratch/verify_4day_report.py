import sys
sys.stdout.reconfigure(encoding='utf-8')

# Data extracted directly from user's 4 daily attendance report posts (21, 22, 23, 24 Sep 2026)

daily_data = {
    "AI & IOT": {
        "Akshay": ["P", "P", "P", "P"],
        "Kusum": ["P", "P", "P", "P"],
        "Poornima": ["P", "P", "P", "P"],
        "Ramya": ["H", "H", "H", "H"]
    },
    "Sunfra OLX CEE": {
        "Asif": ["P", "P", "P", "P"],
        "Prasanna": ["H", "P", "P", "P"],
        "Yashaswini": ["L", "P", "P", "P"]
    },
    "Jataayu": {
        "Roopa": ["A", "P", "P", "P"]
    },
    "Sunfra Corporate": {
        "Divya": ["P", "P", "H", "P"],
        "Prajwal": ["A", "A", "A", "A"]
    },
    "Sunfra Mudah": {
        "Akshay": ["P", "P", "P", "P"],
        "Bharath": ["P", "P", "P", "P"],
        "Krishna": ["A", "P", "P", "P"],
        "Nisha": ["P", "P", "P", "P"],
        "Ravi Teja": ["P", "P", "H", "P"],
        "Thanuja": ["P", "P", "P", "P"],
        "Aishwarya": ["P", "P", "P", "P"],
        "Lakshmi": ["P", "P", "H", "P"]
    },
    "Sunfra HR Team": {
        "Parvati": ["P", "P", "P", "P"],
        "Bhanushree": ["P", "P", "P", "P"]
    },
    "Indus": {
        "Girija": ["A", "A", "A", "A"],
        "Jagadish": ["A", "A", "A", "A"]
    },
    "Sunfra Farms": {
        "Mahalakshmi": ["A", "P", "P", "P"]
    },
    "Sunfra Feeds": {
        "Venkat": ["P", "P", "P", "P"]
    },
    "Management Team": {
        "Balaji": ["A", "L", "P", "P"],
        "Nani": ["P", "P", "P", "P"],
        "Nikhil": ["H", "P", "P", "P"],
        "Prasad": ["L", "A", "P", "A"],
        "Prathiba": ["H", "H", "A", "H"],
        "Vamsi": ["A", "H", "A", "P"]
    },
    "Tendered": {
        "Ganga": ["P", "P", "P", "P"]
    }
}

lines = [
    "📋 *4-DAY ATTENDANCE SUMMARY REPORT*",
    "🗓️ *Period:* 21 Sep 2026 – 24 Sep 2026 (Total Working Days: 4)",
    "=================================================="
]

tot_working = 0
tot_present = 0.0
tot_absent = 0.0
tot_emp = 0

for grp_name, emps in daily_data.items():
    lines.append(f"\n🏢 *{grp_name}*")
    for emp_name, statuses in emps.items():
        tot_emp += 1
        p_count = 0.0
        a_count = 0.0
        for s in statuses:
            if s == "P":
                p_count += 1.0
            elif s == "H":
                p_count += 0.5
                a_count += 0.5
            elif s in ["A", "L"]:
                a_count += 1.0
        
        tot_working += 4
        tot_present += p_count
        tot_absent += a_count

        p_str = f"{p_count:g}"
        a_str = f"{a_count:g}"
        
        lines.append(f"  • *{emp_name}*: *{p_str}* Present / *4* Working ({a_str} Absent/Leave)")

lines.extend([
    "\n==================================================",
    "📊 *OVERALL 4-DAY SUMMARY (21 SEP TO 24 SEP):*",
    f"👥 Total Employees: *{tot_emp}*",
    f"🟢 Total Present Days: *{tot_present:g}*",
    f"🔴 Total Absent/Leave Days: *{tot_absent:g}*",
    f"💼 Total Working Days Pool: *{tot_working}*",
    "=================================================="
])

report_text = "\n".join(lines)
with open("scratch/four_day_report.txt", "w", encoding="utf-8") as f:
    f.write(report_text)

print(report_text)
