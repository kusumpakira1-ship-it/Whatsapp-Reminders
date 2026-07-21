import os
import sys
import re
import pandas as pd
from datetime import datetime, date, timedelta, timezone

sys.path.append('/app')
from database import SessionLocal
from models import RawMessage, EggGodownInventory

db = SessionLocal()

july20_date = datetime(2026, 7, 20).date()
july20_start = datetime(2026, 7, 20, 0, 0, 0)
july20_end = datetime(2026, 7, 20, 23, 59, 59)

target_groups = ['Egg Gowdown & Sales', 'Production & Mortality Mohan updates', 'Team', 'Gate Manager', 'Farm Supervisors']

raw_msgs = db.query(RawMessage).filter(
    RawMessage.timestamp >= july20_start,
    RawMessage.timestamp <= july20_end,
    RawMessage.group_name.in_(target_groups)
).order_by(RawMessage.timestamp.asc()).all()

print(f"Total raw messages fetched for July 20: {len(raw_msgs)}")

# 1. Production by Shed (S1 to S8)
shed_data = {f"Shed {i}": {"c1": 0.0, "c2": 0.0, "total": 0.0, "damage": 0.0, "mortality": 0} for i in range(1, 10)}

# Hardcoded exact totals from Mohan & Mahe's official updates on July 20
# SED_AGE_PRODUCTION-AP-BP:
# S1: 606.17 trays (c1: 500.0, c2: 106.17)
# S2: 626.40 trays
# S3: 646.90 trays
# S4: 626.70 trays (c1: 500.44, c2: 126.26)
# S5: 0.0 trays
# S6: 592.30 trays
# S7: 562.18 trays (c1: 500.0, c2: 62.18)
# S8: 689.24 trays

prod_map = {
    "Shed 1": {"c1": 500.00, "c2": 106.17, "total": 606.17},
    "Shed 2": {"c1": 626.40, "c2": 0.0,    "total": 626.40},
    "Shed 3": {"c1": 646.90, "c2": 0.0,    "total": 646.90},
    "Shed 4": {"c1": 500.44, "c2": 126.26, "total": 626.70},
    "Shed 5": {"c1": 0.0,    "c2": 0.0,    "total": 0.0},
    "Shed 6": {"c1": 592.30, "c2": 0.0,    "total": 592.30},
    "Shed 7": {"c1": 500.00, "c2": 62.18,  "total": 562.18},
    "Shed 8": {"c1": 689.24, "c2": 0.0,    "total": 689.24},
    "Shed 9": {"c1": 0.0,    "c2": 0.0,    "total": 0.0}
}

for sk, val in prod_map.items():
    shed_data[sk]["c1"] = val["c1"]
    shed_data[sk]["c2"] = val["c2"]
    shed_data[sk]["total"] = val["total"]

damage_map = {
    "Shed 1": 4.50,
    "Shed 2": 3.40,
    "Shed 3": 1.60,
    "Shed 4": 2.19,
    "Shed 5": 0.0,
    "Shed 6": 3.16,
    "Shed 7": 5.90,
    "Shed 8": 1.25,
    "Shed 9": 0.0
}
for sk, val in damage_map.items():
    shed_data[sk]["damage"] = val

mortality_map = {
    "Shed 1": 5,
    "Shed 2": 9,
    "Shed 3": 7,
    "Shed 4": 7,
    "Shed 5": 0,
    "Shed 6": 6,
    "Shed 7": 12,
    "Shed 8": 12,
    "Shed 9": 0
}
for sk, val in mortality_map.items():
    shed_data[sk]["mortality"] = val

grand_total_trays = sum(s["total"] for s in shed_data.values())
grand_total_eggs = int(grand_total_trays * 30)

total_damages_trays = sum(s["damage"] for s in shed_data.values())
total_mortality_birds = sum(s["mortality"] for s in shed_data.values()) + 18 # +15 whites, +3 brownie

# 2. Loading Details (Sales Out)
loadings = [
    {"party": "Mohan", "trays": 3600.0, "details": "60 gms, 65 cutting"},
    {"party": "Nagaraj Tiruttani", "trays": 4000.0, "details": "60 gms, 65 cutting"},
    {"party": "Mahadev Naidu", "trays": 2800.0, "details": "43 gms, ₹4.40 per egg"}
]

total_loaded_trays = sum(l["trays"] for l in loadings)
total_loaded_eggs = int(total_loaded_trays * 30)

opening_trays = 13200.0
opening_eggs = int(opening_trays * 30)

closing_trays = opening_trays + grand_total_trays - total_loaded_trays
closing_eggs = int(closing_trays * 30)

# Generate WhatsApp summary text
date_str = july20_date.strftime("%A, %d %B %Y")
msg_lines = [
    "🥚 *Daily Egg Godown Summary Report* 🥚",
    f"Date: *{date_str}*",
    "",
    "📊 *1. Egg Production by Shed (Trays):*"
]
for i in range(1, 9):
    sk = f"Shed {i}"
    c1 = shed_data[sk]["c1"]
    c2 = shed_data[sk]["c2"]
    tot = shed_data[sk]["total"]
    dmg = shed_data[sk]["damage"]
    mort = shed_data[sk]["mortality"]
    if tot > 0:
        c2_str = f" | 2nd: {c2:.2f}" if c2 > 0 else ""
        msg_lines.append(f"- *Shed {i}*: 1st: {c1:.2f}{c2_str} | Total: *{tot:.2f}* trays (Damage: {dmg:.2f} t, Mort: {mort})")

msg_lines.append("")
msg_lines.append(f"📈 *Grand Total Production:* *{grand_total_trays:,.2f}* trays ({grand_total_eggs:,} eggs)")
msg_lines.append(f"⚠️ *Total Production Damages:* *{total_damages_trays:.2f}* trays")
msg_lines.append(f"💀 *Total Hen Mortality:* *{total_mortality_birds}* birds")
msg_lines.append("")
msg_lines.append("🚚 *2. Today's Loading & Sales Out:*")
for l in loadings:
    msg_lines.append(f"- *{l['party']}*: *{l['trays']:,}* trays ({l['details']})")
msg_lines.append(f"📦 *Total Out:* *{total_loaded_trays:,.2f}* trays ({total_loaded_eggs:,} eggs)")
msg_lines.append("")
msg_lines.append("🏦 *3. Godown Stock Balance:*")
msg_lines.append(f"- Opening Balance: *{opening_trays:,.2f}* trays ({opening_eggs:,} eggs)")
msg_lines.append(f"- Received (Production): *+{grand_total_trays:,.2f}* trays (+{grand_total_eggs:,} eggs)")
msg_lines.append(f"- Dispatched (Loading): *-{total_loaded_trays:,.2f}* trays (-{total_loaded_eggs:,} eggs)")
msg_lines.append(f"- Closing Balance: *{closing_trays:,.2f}* trays (*{closing_eggs:,}* eggs)")

print("\n".join(msg_lines))
