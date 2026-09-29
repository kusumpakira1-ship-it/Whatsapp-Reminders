import sys
import os
import imaplib
import email
from email.header import decode_header

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from papaak_email_service import GMAIL_EMAIL, GMAIL_APP_PASS, get_forwarded_email_ids

print("Checking Gmail inbox for all recent emails...")
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(GMAIL_EMAIL, GMAIL_APP_PASS)
mail.select("inbox")

status, data = mail.search(None, 'ALL')
if status == 'OK' and data[0]:
    mail_ids = data[0].split()
    recent_ids = mail_ids[-30:]  # check last 30 emails
    print(f"Total emails in inbox: {len(mail_ids)}. Checking last {len(recent_ids)} emails:")
    
    forwarded_ids = get_forwarded_email_ids()
    print(f"Already forwarded email IDs count: {len(forwarded_ids)}")
    
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
                
                # Print details of any email received today or containing PAPAAK
                if "PAPAAK" in sender.upper() or "PAPAAK" in subject.upper() or "PAPAAK" in body_text.upper() or "CP-PAPAAK" in sender.upper() or "CP-PAPAAK" in body_text.upper():
                    print("\n--------------------------------------------------")
                    print(f"ID: {m_id.decode()}")
                    print(f"Date: {date_hdr}")
                    print(f"From: {sender}")
                    print(f"Subject: {subject}")
                    print(f"Message-ID (UID): {email_uid}")
                    print(f"Already Forwarded? {email_uid in forwarded_ids}")
                    print("Body Snippet:")
                    print(body_text.strip()[:300])

mail.logout()
