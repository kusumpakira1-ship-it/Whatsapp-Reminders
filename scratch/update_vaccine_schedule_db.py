"""
Script to update sunfra_book_standards table with vaccine schedules from the provided charts for Shed 5 and Chicks.
"""

import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

vaccine_updates = {
    1: "HVT + SB1 & IBH 120 (Dose: 0.2ml / Single - Ventri/MSD/Intervet)",
    3: "Mareks (HVT + SB1) (Dose: 0.2ml - Subcutaneous S/C)",
    5: "ND + IBD + IB KILLED (0.2ml/0.25ml S/C) & IB + LASOTA / MA5+Clone 30 (Eye Drop)",
    9: "DEBEAKING (Vitamin K)",
    12: "IBD B2K (Dose: Single - Sarabai)",
    13: "IBD + LIVE (Eye Drop - Ventri)",
    17: "CAV Live (Dose: 0.2ml - Subcutaneous S/C Ventris)",
    21: "IBH (IBD) (Dose: 0.25ml - Triple Sticker VIRBAC)",
    23: "IBD LIVE II (Eye Drop - Ventri)",
    30: "LASOTA + IB / F Fox (Dose: 0.2ml Eye Drop - Ventris)",
    35: "CORYZA - 1 / Lasota IB Live MA5 (Dose: 0.5ml I/M or S/C - MSD)",
    38: "Dalguban Lasota (Dose: One and Half - VIRBAC)",
    42: "FOWL POX - 1 (Dose: 0.2ml - I/M or Wing Web Ventris)",
    46: "VVND (KILLED - 1) (Dose: 0.5ml - I/M or S/C)",
    50: "IC KILLED (Dose: 0.5ml - MSD)",
    60: "VVND L+H (Dose: 0.5ml - HESTER Red cap)",
    84: "LASOTA + IB / R2B + F Pox (Dose: 0.5ml - Ventris / Drinking Water)",
    91: "DEBEAKING (Vitamin K) & FOWL POX - II (Dose: 0.2ml - I/M or Wing Web)",
    98: "Booster (MA5) / CORYZA - II (Dose: 0.5ml - MSD / S/C)",
    105: "DEWORMING & LASOTA + IB (Drinking Water)",
    108: "IC / VVND (KILLED) - II (Dose: 0.5ml - MSD / S/C)",
    115: "VVND L+H / ND KILLED (Dose: 0.5ml - HESTER Red / S/C)",
    129: "Dalguban Lasota (Single - VIRBAC) & ND+IBK (Dose: 0.5ml - Sarabai)",
    147: "ND KILLED (Dose: 0.5ml - Intra Muscular I/M)",
}

for day, vacc in vaccine_updates.items():
    week = (day - 1) // 7 + 1
    cur.execute("SELECT * FROM sunfra_book_standards WHERE day = %s", (day,))
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE sunfra_book_standards SET vaccine = %s, week = %s WHERE day = %s", (vacc, week, day))
    else:
        cur.execute("INSERT INTO sunfra_book_standards (day, week, vaccine) VALUES (%s, %s, %s)", (day, week, vacc))

conn.commit()
print("SUCCESS: Updated vaccine standards for all days/weeks in sunfra_book_standards!")

cur.execute("SELECT day, week, vaccine FROM sunfra_book_standards WHERE vaccine IS NOT NULL AND vaccine != '' ORDER BY day")
all_v = cur.fetchall()
print(f"\nTotal vaccine entries in DB: {len(all_v)}")
for v in all_v[:30]:
    print(f"Day {v['day']:3d} (Week {v['week']:2d}): {v['vaccine']}")

cur.close()
conn.close()
