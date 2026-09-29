import sys
import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from papaak_email_service import fetch_and_process_papaak_emails, format_papaak_raw_forward, generate_daily_egg_rates_report, generate_daily_feed_rates_report

IST = timezone(timedelta(hours=5, minutes=30))

print("=== 1. FETCHING & PROCESSING EMAILS INTO DATABASE (WITHOUT SENDING WHATSAPP) ===")
count = fetch_and_process_papaak_emails(notify_on_new=False)
print(f"Processed email records added: {count}")

print("\n=== 2. FETCHING TODAY'S (28/09/2026) RAW PAPAAK MESSAGES & FORMATTED FORWARDS ===")
GMAIL_EMAIL = "kusum@sunfra.com"
GMAIL_APP_PASS = "kfgykqtorkchfkke"

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
mail.select("inbox")

status, data = mail.search(None, 'ALL')
mail_ids = data[0].split()
recent_ids = mail_ids[-30:]

today_date_str = "2026-09-28"

reports = []

for m_id in recent_ids:
    _, msg_data = mail.fetch(m_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            sender = str(msg.get("from", ""))
            
            date_header = msg.get("date")
            msg_dt = datetime.now(IST)
            if date_header:
                try:
                    msg_dt = email.utils.parsedate_to_datetime(date_header).astimezone(IST)
                except Exception:
                    pass

            # Body
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body_text = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            pass
            else:
                try:
                    body_text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                except Exception:
                    pass

            if msg_dt.strftime("%Y-%m-%d") == today_date_str and ("PAPAAK" in sender.upper() or "PAPAAK" in body_text.upper() or "CP-PAPAAK-S" in body_text.upper()):
                is_feed = "FEED" in body_text.upper() or any(k in body_text.upper() for k in ["SOY", "MAZ", "DRB", "BAJ", "GNE45", "DMC"])
                formatted_fw = format_papaak_raw_forward(body_text, is_feed, msg_dt)
                reports.append({
                    "dt": msg_dt.strftime("%I:%M %p"),
                    "raw": body_text.strip(),
                    "formatted": formatted_fw
                })

print(f"Total PAPAAK messages found for today ({today_date_str}): {len(reports)}")

for idx, r in enumerate(reports, 1):
    print(f"\n=================== REPORT #{idx} ({r['dt']}) ===================")
    print("--- Formatted Message ---")
    print(r['formatted'])
    print("\n--- Original Raw Message Text ---")
    print(r['raw'])

print("\n=================== CONSOLIDATED DAILY EGG LOADING & PAPER RATES REPORT ===================")
summary_report = generate_daily_egg_rates_report(target_date=today_date_str)
print(summary_report)
