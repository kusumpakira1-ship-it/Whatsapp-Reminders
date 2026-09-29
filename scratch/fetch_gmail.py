import imaplib
import email
from email.header import decode_header
from datetime import datetime, timezone, timedelta
import sys

sys.stdout.reconfigure(encoding='utf-8')

IST = timezone(timedelta(hours=5, minutes=30))
GMAIL_EMAIL = "kusum@sunfra.com"
GMAIL_APP_PASS = "kfgykqtorkchfkke"

print(f"Connecting to Gmail for {GMAIL_EMAIL}...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
mail.select("inbox")

# Search for PAPAAK or ALL recent
status, data = mail.search(None, 'ALL')
print(f"Search status: {status}, Total emails in inbox: {len(data[0].split())}")

mail_ids = data[0].split()
recent_ids = mail_ids[-30:] # Last 30 emails

papaak_emails = []

for m_id in recent_ids:
    _, msg_data = mail.fetch(m_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            sender = str(msg.get("from", ""))
            
            # Subject
            subject_raw = msg.get("subject", "")
            subject = ""
            if subject_raw:
                try:
                    decoded_parts = decode_header(subject_raw)
                    for part, encoding in decoded_parts:
                        if isinstance(part, bytes):
                            subject += part.decode(encoding or 'utf-8', errors='ignore')
                        else:
                            subject += str(part)
                except Exception:
                    subject = str(subject_raw)

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

            # Date
            date_header = msg.get("date")
            msg_dt = datetime.now(IST)
            if date_header:
                try:
                    msg_dt = email.utils.parsedate_to_datetime(date_header).astimezone(IST)
                except Exception:
                    pass

            if "PAPAAK" in sender.upper() or "PAPAAK" in subject.upper() or "PAPAAK" in body_text.upper() or "EGG" in body_text.upper() or "RATE" in body_text.upper():
                papaak_emails.append({
                    "id": m_id.decode(),
                    "date": msg_dt.strftime("%Y-%m-%d %H:%M:%S IST"),
                    "sender": sender,
                    "subject": subject,
                    "body": body_text.strip()
                })

print(f"\nFound {len(papaak_emails)} PAPAAK / Rate emails:")
for idx, em in enumerate(papaak_emails, 1):
    print(f"\n--- Email #{idx} ---")
    print(f"Date: {em['date']}")
    print(f"From: {em['sender']}")
    print(f"Subject: {em['subject']}")
    print("Body:")
    print(em['body'])
    print("-" * 50)
