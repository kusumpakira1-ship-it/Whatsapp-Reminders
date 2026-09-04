import sys
import os

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

print("=== DISPATCHING RENTAL & VACANCY REPORT TO 7259510983 ===")

target_phone = "917259510983@c.us"

try:
    from scheduler import generate_rental_vacancy_report
    from waha_service import send_waha_message

    report_text = generate_rental_vacancy_report()
    if report_text:
        send_waha_message(target_phone, report_text)
        print("✅ Daily Rental & Vacancy Loss Report successfully sent to 7259510983!")
    else:
        print("⚠️ Rental report returned empty string.")
except Exception as e:
    print(f"❌ Error sending Rental Vacancy Report: {e}")
