import sys
import os
from datetime import datetime, timezone, timedelta, date

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from papaak_email_service import format_papaak_raw_forward, generate_daily_egg_rates_report, send_waha_message, PAPAAK_RECIPIENTS

IST = timezone(timedelta(hours=5, minutes=30))

raw_body = """From : CP-PAPAAK-S()
VEH KOL 09
7:43 Egg
BRMP(OR):605
BPL:555
GOD:600
HYD:530
JBL:540
KOL:635
MYS:615
NKL:540
RAI:540
VIJ:600
VIZ:575
VIJ PACKING:545"""

msg_dt = datetime(2026, 10, 12, 7, 43, tzinfo=IST)
new_message = format_papaak_raw_forward(raw_body, False, msg_dt)
report_1 = generate_daily_egg_rates_report(target_date=date(2026, 10, 12), report_number=1)

print("--- 1. NEW MESSAGE ---")
print(new_message)
print("\n--- 2. REPORT 1 ---")
print(report_1)

for target in PAPAAK_RECIPIENTS:
    print(f"\nSending new message to {target}...")
    res1 = send_waha_message(target, new_message)
    print(f"New message send result: {res1}")

    print(f"Sending Report 1 to {target}...")
    res2 = send_waha_message(target, report_1)
    print(f"Report 1 send result: {res2}")
