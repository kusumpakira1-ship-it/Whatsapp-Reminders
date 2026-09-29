import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from papaak_email_service import generate_daily_feed_rates_report, generate_daily_egg_rates_report, send_waha_message

print("Generating Today's (24 Sep 2026) Daily PAPAAK Feed Rates Report (Compared with Yesterday)...")
feed_report = generate_daily_feed_rates_report(target_date="2026-09-24")

print("\n--- FEED REPORT PREVIEW ---")
print(feed_report)

if feed_report:
    print("\nSending Feed Report to 917259510983@c.us via WAHA...")
    send_waha_message("917259510983@c.us", feed_report)

print("\nGenerating Today's (24 Sep 2026) Daily PAPAAK Egg Rates Report...")
egg_report = generate_daily_egg_rates_report(target_date="2026-09-24")

print("\n--- EGG REPORT PREVIEW ---")
print(egg_report)

if egg_report:
    print("\nSending Egg Report to 917259510983@c.us via WAHA...")
    send_waha_message("917259510983@c.us", egg_report)

print("\nFinished dispatching reports.")
