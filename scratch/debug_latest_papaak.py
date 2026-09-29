import sys
import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from papaak_email_service import GMAIL_EMAIL, GMAIL_APP_PASS, get_forwarded_email_ids, fetch_and_process_papaak_emails

print("1. Checking Gmail Inbox for all CP-PAPAAK-S messages...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
mail.select("inbox")

status, data = mail.search(None, 'ALL')
if status == 'OK' and data[0]:
    mail_ids = data[0].split()
    recent_ids = mail_ids[-15:]
    forwarded_ids = get_forwarded_email_ids()
    print(f"Total emails in Inbox: {len(mail_ids)}. Checking last 15:")
    
    for m_id in reversed(recent_ids):
        _, msg_data = mail.fetch(m_id, "(RFC822)")
        for part in msg_data:
            if isinstance(part, tuple):
                msg = email.message_from_bytes(part[1])
                sender = str(msg.get("from", ""))
                subject_raw = msg.get("subject", "")
                subject = ""
                if subject_raw:
                    try:
                        decoded = decode_header(subject_raw)
                        for p, enc in decoded:
                            if isinstance(p, bytes):
                                subject += p.decode(enc or 'utf-8', errors='ignore')
                            else:
                                subject += str(p)
                    except Exception:
                        subject = str(subject_raw)
                
                date_hdr = str(msg.get("date", ""))
                body_text = ""
                if msg.is_multipart():
                    for p in msg.walk():
                        if p.get_content_type() == "text/plain":
                            try:
                                body_text = p.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                            except Exception:
                                pass
                else:
                    try:
                        body_text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
                
                email_uid = msg.get("Message-ID") or f"{msg.get('date', '')}_{body_text[:50]}"
                
                if "PAPAAK" in sender.upper() or "PAPAAK" in subject.upper() or "PAPAAK" in body_text.upper() or "CP-PAPAAK" in body_text.upper():
                    print("\n--------------------------------------------------")
                    print(f"ID: {m_id.decode()}")
                    print(f"Date: {date_hdr}")
                    print(f"Subject: {subject}")
                    print(f"UID: {email_uid}")
                    print(f"In forwarded_ids list? {email_uid in forwarded_ids}")
                    print("Body:")
                    print(body_text.strip())

mail.logout()

print("\n2. Now running fetch_and_process_papaak_emails(notify_on_new=True)...")
res = fetch_and_process_papaak_emails(notify_on_new=True)
print(f"Done. Added {res} new rate records.")
