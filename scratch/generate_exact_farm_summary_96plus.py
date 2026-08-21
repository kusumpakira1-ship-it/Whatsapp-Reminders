"""
Generate exact Daily Farm Summary for Yesterday (13 Aug 2026) with 96+% capping rule.
"""
import pymysql, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# 1. Mortality Data for 13 Aug 2026
mortality_data = {
    'Shead 1': 7,
    'Shead 2': 8,
    'Shead 3': 2,
    'Shead 4': 7,
    'Shead 5': 0,
    'Shead 6': 12,
    'Shead 7': 8,
    'Shead 8': 2,
    'Chick 1': 0
}

# 2. Production Data for 13 Aug 2026
production_data = {
    'Shead 1': {'trays': 594, 'loose': 17, 'total_eggs': 17837, 'damaged': 115},
    'Shead 2': {'trays': 619, 'loose': 3, 'total_eggs': 18573, 'damaged': 60},
    'Shead 3': {'trays': 642, 'loose': 28, 'total_eggs': 19288, 'damaged': 50},
    'Shead 4': {'trays': 622, 'loose': 5, 'total_eggs': 18665, 'damaged': 67},
    'Shead 5': {'trays': 7, 'loose': 8, 'total_eggs': 218, 'damaged': 6},
    'Shead 6': {'trays': 592, 'loose': 27, 'total_eggs': 17787, 'damaged': 74},
    'Shead 7': {'trays': 574, 'loose': 10, 'total_eggs': 17230, 'damaged': 250},
    'Shead 8': {'trays': 678, 'loose': 15, 'total_eggs': 20355, 'damaged': 35}
}

# 3. Birds Weight Data
weight_data = {
    'Shead 1': 1417.88,
    'Shead 2': 1412.38,
    'Shead 3': 1235.63,
    'Shead 4': 1511.60,
    'Shead 5': 1051.88,
    'Shead 6': 1491.63,
    'Shead 7': 1528.75,
    'Shead 8': 1403.00,
    'Chick 1': None
}

target_date = datetime.date(2026, 8, 13)

cursor.execute("SELECT * FROM sunfra_flocks WHERE status = 'active'")
flocks = {f['shed_name']: f for f in cursor.fetchall()}

production_rows = []
weight_rows = []
mortality_rows = []

for s_num in range(1, 9):
    sname = f"Shead {s_num}"
    fl = flocks.get(sname, {})
    hatch = fl.get('hatch_date')
    live_birds = fl.get('live_birds', 0)
    
    if hatch:
        age_days = (target_date - hatch).days
        age_weeks = age_days // 7
    else:
        age_weeks = fl.get('running_weeks', 0)

    cursor.execute("SELECT AVG(expected_production_pct) as bp, AVG(expected_body_weight_g) as bw FROM sunfra_book_standards WHERE week = %s", (age_weeks,))
    b_std = cursor.fetchone() or {}
    book_pct = round(float(b_std.get('bp') or 0))
    book_weight = round(float(b_std.get('bw') or 0))

    # Mortality
    m_val = mortality_data.get(sname, 0)
    mortality_rows.append(f"{sname}: {m_val}")

    # Production
    p_info = production_data.get(sname, {'trays': 0, 'loose': 0, 'total_eggs': 0})
    trays = p_info['trays']
    loose = p_info['loose']
    total_eggs = p_info['total_eggs']
    actual_pct_raw = round((total_eggs / live_birds * 100)) if live_birds > 0 else 0
    
    # Cap production display at 96+% if > 96%
    if actual_pct_raw > 96:
        actual_pct_str = "96+%"
    else:
        actual_pct_str = f"{actual_pct_raw}%"

    prod_icon = "🟢" if actual_pct_raw >= book_pct else "🔴"
    trays_fmt = f"{trays}.{loose:02d}"
    production_rows.append(f"{sname}: {age_weeks}w | {trays_fmt} Trays | {actual_pct_str} (Book: {book_pct}%) {prod_icon}")

    # Weight
    act_weight = weight_data.get(sname)
    if act_weight:
        diff_weight = round(act_weight - book_weight)
        weight_icon = "🟢" if act_weight >= book_weight else "🔴"
        diff_str = f"+{diff_weight}g" if diff_weight > 0 else f"{diff_weight}g"
        weight_rows.append(f"{sname}: {act_weight:.2f}g (Book: {book_weight}g | {diff_str}) {weight_icon}")
    else:
        weight_rows.append(f"{sname}: No Weight Data (Book: {book_weight}g)")

mortality_rows.append(f"Chick 1: {mortality_data['Chick 1']}")

report = f"""📋 *DAILY FARM SUMMARY (13/08/2026)*

💀 *Shed-Wise Mortality*
```
""" + "\n".join(mortality_rows) + f"""
Total mortality: {sum(mortality_data.values())}
```

🥚 *Shed-Wise Production (Actual vs Book Standard)*
```
""" + "\n".join(production_rows) + """
```

⚖️ *Birds Weight Comparison (Actual vs Book Standard)*
```
""" + "\n".join(weight_rows) + """
```"""

print(report)

conn.close()

