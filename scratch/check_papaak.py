import sys
import os
import imaplib
import email
from email.header import decode_header

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import get_db_session
from models import PapaakEggRate
from papaak_email_service import GMAIL_EMAIL, GMAIL_APP_PASS

print("==================================================")
print(" PAPAAK (CP-PAPAAK-S) MESSAGES & RATES SUMMARY ")
print("==================================================")

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
    mail.select("inbox")

    # Search specifically for CP-PAPAAK-S
    status, data = mail.search(None, 'ALL')
    if status == 'OK' and data[0]:
        mail_ids = data[0].split()
        found_count = 0
        for m_id in reversed(mail_ids):
            _, msg_data = mail.fetch(m_id, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    sender = msg.get("from", "")
                    subject = msg.get("subject", "")
                    date_hdr = msg.get("date", "")
                    
                    body_text = ""
                    if msg.is_multipart():
                        for p in msg.walk():
                            if p.get_content_type() == "text/plain":
                                body_text = p.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body_text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    if "PAPAAK" in subject.upper() or "PAPAAK" in body_text.upper() or "CP-PAPAAK-S" in body_text.upper():
                        found_count += 1
                        print(f"\n📩 MESSAGE #{found_count}")
                        print(f"Date: {date_hdr}")
                        print(f"Subject: {subject}")
                        print("Content:")
                        print(body_text.strip())
                        print("=" * 60)
        print(f"\nTotal PAPAAK messages found: {found_count}")
except Exception as e:
    print(f"Error: {e}")
