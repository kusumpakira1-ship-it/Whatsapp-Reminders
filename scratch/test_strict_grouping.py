import sys

sys.path.append('backend')
from attendance_tracker import COMMUNITY_EMPLOYEES
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ TESTING STRICT GROUP MATCHING ON 16 SEP 2026 ==================")

query = text("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE date(timestamp) = '2026-09-16'
    ORDER BY timestamp ASC
""")

raws = db.execute(query).fetchall()
print(f"Total raw messages on 16 Sep: {len(raws)}")

for grp_data in COMMUNITY_EMPLOYEES:
    grp_name = grp_data["group"]
    grp_target = grp_name.lower()
    grp_jids_lower = [j.lower() for j in grp_data.get("group_jids", [])] + [grp_target]

    print(f"\n*** Group: {grp_name} (Target keywords: {grp_jids_lower[:3]}) ***")

    for emp in grp_data["employees"]:
        emp_name = emp["name"]
        phone = emp["phone"]
        aliases = emp.get("aliases", [])

        matched = []
        for r in raws:
            s_str = str(r[0] or "").lower()
            g_str = str(r[1] or "").lower()

            # Check sender match
            is_sender = (phone in s_str) or (("91" + phone) in s_str) or any(al.lower() in s_str for al in aliases)

            # Check strict group match
            is_group = (grp_target in g_str) or any(j in g_str for j in grp_jids_lower)

            if is_sender and is_group:
                matched.append(r)

        if matched:
            print(f"  • {emp_name}: {len(matched)} msgs in group '{grp_name}'")
            print(f"    Earliest: [{matched[0][3]}] '{matched[0][2][:30]}'")
            print(f"    Latest:   [{matched[-1][3]}] '{matched[-1][2][:30]}'")
        else:
            print(f"  • {emp_name}: No msgs in group '{grp_name}'")

db.close()
