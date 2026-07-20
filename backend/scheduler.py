import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from report_generator import generate_daily_reports, generate_custom_report
from waha_service import send_waha_message, send_waha_file, get_session_status, get_session_qr
from config import settings
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from models import ReportRecipient, Group, Employee, ProcessedData, RawMessage, SystemSetting, CustomAlarm, UnifiedReminder, WAHAEvent, Task, EggGodownInventory, WhatsAppMessage
from sqlalchemy import func

logger = logging.getLogger(__name__)


def clean_name_string(name: str) -> str:
    if not name:
        return ""
    import unicodedata
    # Normalize unicode to decompose accents (e.g. ú -> u)
    normalized = unicodedata.normalize('NFKD', name)
    # Filter to only keep alphanumeric characters and spaces
    cleaned = "".join(c for c in normalized if c.isalnum() or c.isspace())
    # Remove 'ss ' prefix if any, and clean whitespace
    cleaned = cleaned.lower().replace('ss ', '').strip()
    return cleaned

scheduler = AsyncIOScheduler()

def _get_recipient_list():
    import os
    db = SessionLocal()
    try:
        recipients = db.query(ReportRecipient).filter(ReportRecipient.is_active == True).all()
        phones = [r.phone_number for r in recipients]
    except Exception as e:
        logger.error(f"Error fetching report recipients: {e}")
        phones = []
    finally:
        db.close()

    # Append Manager Phone from config
    manager_phone = settings.MANAGER_PHONE
    if manager_phone:
        manager_jid = manager_phone
        if not manager_jid.endswith('@c.us') and not manager_jid.endswith('@g.us') and not manager_jid.endswith('@lid'):
            manager_jid += '@c.us'
        if manager_jid not in phones:
            phones.append(manager_jid)
    return phones

async def _send_reports_to_all(pdf_path, summary_text):
    phones = _get_recipient_list()
    if not phones:
        logger.warning("No active recipients or manager configured to send reports to.")
        return
        
    for phone in phones:
        if summary_text:
            send_waha_message(phone, summary_text)
        if pdf_path:
            send_waha_file(phone, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")

async def scheduled_report_job():
    logger.info("Starting scheduled 10 PM daily report generation...")
    pdf_path, summary_text = generate_daily_reports()
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_godown_report_job():
    logger.info("Starting scheduled 9 PM daily egg godown summary report...")
    try:
        from report_generator_godown import generate_godown_report
        pdf_path, summary_text = generate_godown_report()
        admin_phones = ["917259510983", "919346763549"]
        for phone in admin_phones:
            logger.info(f"Sending daily egg godown summary to {phone}")
            send_waha_message(phone, summary_text)
            if pdf_path and os.path.exists(pdf_path):
                send_waha_file(phone, pdf_path, caption=f"Egg Godown Report - {pdf_path.split('/')[-1]}")
    except Exception as e:
        logger.error(f"Error in scheduled_godown_report_job: {e}")


async def scheduled_weekly_report_job():
    logger.info("Starting scheduled weekly report generation...")
    pdf_path, summary_text = generate_custom_report('weekly')
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_monthly_report_job():
    logger.info("Starting scheduled monthly report generation...")
    pdf_path, summary_text = generate_custom_report('monthly')
    await _send_reports_to_all(pdf_path, summary_text)

async def scheduled_yearly_report_job():
    logger.info("Starting scheduled yearly report generation...")
    pdf_path, summary_text = generate_custom_report('yearly')
    await _send_reports_to_all(pdf_path, summary_text)

def check_missing_reports_for_today() -> dict:
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date()
    
    db = SessionLocal()
    try:
        data = db.query(ProcessedData).filter(
            func.date(ProcessedData.processed_time) == today
        ).all()
        
        received = set()
        for d in data:
            shead = str(d.shead_name or '').replace('Shead', 'Shed').strip()
            if not shead:
                continue
            cat = d.category
            if cat in ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']:
                received.add((shead, 'Production'))
            elif cat in ['feed', 'raw_material']:
                received.add((shead, 'Feed'))
            elif cat in ['medicine', 'expense']:
                received.add((shead, 'Expenditure'))
                
        missing = {}
        for shed in ["Shed 1", "Shed 2", "Shed 3"]:
            shed_missing = []
            if (shed, 'Production') not in received:
                shed_missing.append('Egg Collection')
            if (shed, 'Feed') not in received:
                shed_missing.append('Feed Consumption')
            if (shed, 'Expenditure') not in received:
                shed_missing.append('Shed Expenditure')
            if shed_missing:
                missing[shed] = shed_missing
                
        return missing
    except Exception as e:
        logger.error(f"Error checking missing reports: {e}")
        return {}
    finally:
        db.close()


def get_all_waha_groups_map() -> dict:
    """Fetch all groups from WAHA as a dictionary of JID -> Name."""
    import requests
    import os
    waha_groups_map = {}
    try:
        waha_url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/groups"
        headers = {"Accept": "application/json"}
        api_key = os.getenv("WAHA_API_KEY", "123")
        if api_key:
            headers["X-Api-Key"] = api_key
        response = requests.get(waha_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                for g in data:
                    jid = g.get("id")
                    if jid:
                        waha_groups_map[jid] = g.get("subject") or g.get("name")
            elif isinstance(data, dict):
                for k, v in data.items():
                    if k:
                        waha_groups_map[k] = v.get("subject") or v.get("name")
    except Exception as e:
        logger.error(f"Failed to fetch groups from WAHA in helper: {e}")
    return waha_groups_map


async def group_submission_audit_job():
    """Checks all group reminders at 8:00 PM IST to see if assigned reports were submitted.
    Notifies admin numbers 7259510983 and 9346763549 of any missing reports.
    """
    logger.info("Starting group submission audit report at 8:00 PM IST...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    today = now_ist.date()

    db = SessionLocal()
    try:
        # Fetch all unified reminders that have a group assigned and are recurring
        reminders = db.query(UnifiedReminder).filter(
            UnifiedReminder.whatsapp_group_id != None,
            UnifiedReminder.frequency != 'once'
        ).all()

        if not reminders:
            logger.info("No group reminders found in database for audit.")
            return

        submissions = db.query(ProcessedData).filter(
            func.date(ProcessedData.processed_time) == today
        ).all()

        raw_messages = db.query(RawMessage).filter(
            func.date(RawMessage.timestamp) == today
        ).all()

        groups = db.query(Group).all()
        group_names_by_id = {g.whatsapp_group_id: g.name for g in groups}
        
        # Merge WAHA groups map
        waha_groups_map = get_all_waha_groups_map()
        for jid, name in waha_groups_map.items():
            if jid not in group_names_by_id:
                group_names_by_id[jid] = name

        REPORT_KEYWORDS = {
            'production': ['shead', 'egg', 'lps', 'hrt', 'mortality', 'hitstoke', 'alc', 'production', 'collection', 'week bird', 'bird count'],
            'feed':       ['feed', 'maize', 'soya', 'bran', 'fodder'],
            'sales':      ['sale', 'sold', 'invoice', 'dispatch', 'unload'],
            'sale':       ['sale', 'sold', 'invoice', 'dispatch', 'unload'],
            'expense':    ['expense', 'expenditure', 'payment', 'bill', 'amount paid'],
            'expenditure':['expense', 'expenditure', 'payment', 'bill', 'amount paid'],
            'profit':     ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
            'p&l':        ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
            'p and l':    ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
        }

        # Date formats for flexible matching (e.g. EOD report)
        # e.g., "15-07", "15/07", "15 July", "July 15"
        date_formats = [
            today.strftime("%d-%m"),
            today.strftime("%d/%m"),
            today.strftime("%d %B"),
            today.strftime("%B %d"),
            today.strftime("%dth %B"),
            today.strftime("%B %dth"),
        ]
        # Clean date formats to remove leading zeros (e.g. "5 July" instead of "05 July")
        cleaned_dates = []
        for df in date_formats:
            cleaned_dates.append(df.lower())
            if df.startswith("0"):
                cleaned_dates.append(df[1:].lower())
            cleaned_dates.append(df.replace(" 0", " ").lower())
        date_formats = list(set(cleaned_dates))
        update_keywords = ["update", "updates", "eod", "work update", "daily update"]

        missing_list = []

        for r in reminders:
            assigned_reports = [rep.strip() for rep in str(r.report_types or '').split(',') if rep.strip()]
            if not assigned_reports:
                continue

            group_name = group_names_by_id.get(r.whatsapp_group_id)
            if not group_name:
                continue

            phones = [p.strip() for p in str(r.person_phone or '').split(',') if p.strip()]
            names = [n.strip() for n in str(r.person_name or '').split(',') if n.strip()]

            unsubmitted_reports = []

            for report in assigned_reports:
                submitted = False
                report_lower = report.lower()
                
                # Check category mapping
                categories = []
                if "production" in report_lower or "egg" in report_lower:
                    categories = ["egg_collection", "egg_collection_1", "egg_collection_2", "egg"]
                elif "feed" in report_lower:
                    categories = ["feed", "raw_material"]
                elif "expense" in report_lower or "expenditure" in report_lower or "cost" in report_lower:
                    categories = ["expense", "medicine", "expenditure"]
                elif "sale" in report_lower:
                    categories = ["sales"]

                is_update_report = any(w in report_lower for w in ["update", "eod", "daily report"])

                # 1. Check ProcessedData
                for sub in submissions:
                    match_group = sub.group_name and str(sub.group_name).lower() == group_name.lower()
                    
                    match_sender = False
                    for phone in phones:
                        clean_phone = "".join(filter(str.isdigit, phone))
                        alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                        if clean_phone in str(sub.sender) or alt_phone in str(sub.sender):
                            match_sender = True
                            break

                    if match_sender or match_group:
                        if is_update_report:
                            sub_notes_lower = str(sub.notes or '').lower()
                            if any(kw in sub_notes_lower for kw in update_keywords) or any(df in sub_notes_lower for df in date_formats):
                                submitted = True
                                break
                        
                        if categories:
                            if sub.category in categories:
                                submitted = True
                                break
                        else:
                            if report_lower in str(sub.notes).lower():
                                submitted = True
                                break

                # 2. Check RawMessage fallback
                if not submitted:
                    raw_keywords = []
                    if is_update_report:
                        raw_keywords = update_keywords + date_formats
                    else:
                        for key, kws in REPORT_KEYWORDS.items():
                            if key in report_lower:
                                raw_keywords = kws
                                break
                        if not raw_keywords:
                            raw_keywords = [w for w in report.split() if len(w) > 3]

                    for raw_msg in raw_messages:
                        raw_text_lower = str(raw_msg.raw_text or '').lower()
                        match_group_raw = raw_msg.group_name and str(raw_msg.group_name).lower() == group_name.lower()
                        
                        match_sender_raw = False
                        for phone in phones:
                            clean_phone = "".join(filter(str.isdigit, phone))
                            alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                            if clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender):
                                match_sender_raw = True
                                break

                        if match_sender_raw or match_group_raw:
                            if any(kw.lower() in raw_text_lower for kw in raw_keywords):
                                submitted = True
                                break

                if not submitted:
                    unsubmitted_reports.append(report)

            if unsubmitted_reports:
                missing_reports_str = ", ".join(unsubmitted_reports)
                if names:
                    formatted_names = " & ".join([f"*{n}*" for n in names])
                    missing_list.append(f"- {formatted_names} (*{group_name}*) has not submitted today's *{missing_reports_str}* report(s).")
                else:
                    missing_list.append(f"- *{group_name}* has not submitted today's *{missing_reports_str}* report(s).")

        if missing_list:
            audit_msg = (
                "⏰ *Group Submission Audit Alert (8:00 PM IST)*\n\n"
                "The following group reports are missing for today:\n" +
                "\n".join(missing_list) +
                "\n\nPlease verify."
            )
            
            # Send notification to the 2 admin numbers
            admin_phones = ["917259510983", "919346763549"]
            for admin in admin_phones:
                logger.info(f"Sending group submission audit alert to admin: {admin}")
                send_waha_message(admin, audit_msg)
        else:
            logger.info("Group submission audit complete: All groups submitted successfully.")

    except Exception as e:
        logger.error(f"Error in group_submission_audit_job: {e}")
    finally:
        db.close()

async def scheduled_reminder_job():
    logger.info("Starting scheduled 6 PM data entry reminder...")
    missing = check_missing_reports_for_today()
    if not missing:
        logger.info("All data submitted successfully. No reminders needed.")
        return
        
    # Format message
    msg_lines = []
    msg_lines.append("⏰ *Daily Data Entry Alert (6:00 PM)*")
    msg_lines.append("The following data is missing for today:")
    for shed, items in missing.items():
        msg_lines.append(f"- *{shed}*: {', '.join(items)}")
    msg_lines.append("")
    msg_lines.append("Please submit today's missing reports in the group as soon as possible so that the 11:00 PM Daily Farm Summary report is accurate!")
    
    reminder_text = "\n".join(msg_lines)
    phones = _get_recipient_list()
    
    for phone in phones:
        send_waha_message(phone, reminder_text)

async def scheduled_targeted_reminder_job():
    logger.info("Starting targeted 5:00 PM missed report reminder...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST).date()
    
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        for emp in employees:
            # Check if this employee submitted their assigned report today
            submitted = db.query(ProcessedData).filter(
                func.date(ProcessedData.processed_time) == today,
                ProcessedData.sender.contains(emp.phone_number),
                ProcessedData.category == emp.report_responsibility
            ).first()
            
            if not submitted:
                # Employee missed the report
                group = db.query(Group).filter(Group.id == emp.group_id).first()
                report_friendly_name = emp.report_responsibility.replace('_', ' ').title()
                
                # 1. Send to Employee directly
                emp_phone = emp.phone_number
                if len(emp_phone) == 10 and emp_phone.isdigit():
                    emp_phone = "91" + emp_phone
                    
                emp_msg = f"⏰ *Reminder from Farm Auto*\nHi {emp.name},\nYou have missed submitting the *{report_friendly_name}* report today. Please submit it to the group as soon as possible!"
                send_waha_message(emp_phone + "@c.us", emp_msg)
                
                # 2. Send to Group
                if group:
                    grp_msg = f"⚠️ *Missed Report Alert*\nEmployee *{emp.name}* has not yet submitted the *{report_friendly_name}* report for today."
                    send_waha_message(group.whatsapp_group_id, grp_msg)
    except Exception as e:
        logger.error(f"Error in targeted reminder job: {e}")
    finally:
        db.close()

# Global state to prevent alert spamming and track last status
alert_state = {"is_alerted": False, "last_status": "UNKNOWN", "qr_alerted": False}

# Restart cooldown — only restart WAHA container once per 5 minutes
_last_restart_time = 0
RESTART_COOLDOWN_SEC = 300  # 5 minutes

# ── In-memory settings cache (refreshed every 10 min, NOT every 60 sec) ──────
import time
_settings_cache = {}
_settings_cache_ts = 0
SETTINGS_CACHE_TTL = 600  # 10 minutes

def get_cached_settings():
    """Read alert/SMTP settings from DB once per 10 min, cache rest in memory."""
    global _settings_cache, _settings_cache_ts
    now = time.time()
    if now - _settings_cache_ts < SETTINGS_CACHE_TTL and _settings_cache:
        return _settings_cache
    db = SessionLocal()
    try:
        keys = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_to', 'waha_alert_phone']
        result = {}
        rows = db.query(SystemSetting).filter(SystemSetting.key.in_(keys)).all()
        for row in rows:
            result[row.key] = row.value
        # Defaults
        result.setdefault('smtp_to', 'kusumpakira1@gmail.com')
        result.setdefault('waha_alert_phone', '7259510983')
        _settings_cache = result
        _settings_cache_ts = now
        logger.info("Settings cache refreshed from DB.")
        return _settings_cache
    except Exception as e:
        logger.error(f"Failed to refresh settings cache: {e}")
        return _settings_cache or {'smtp_to': 'kusumpakira1@gmail.com', 'waha_alert_phone': '7259510983'}
    finally:
        db.close()

def send_smtp_email(subject, body, attachment_path=None):
    """Uses in-memory cached settings — NO extra DB connection opened."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    
    cfg = get_cached_settings()
    host     = cfg.get('smtp_host', '')
    port_str = cfg.get('smtp_port', '587')
    user     = cfg.get('smtp_user', '')
    password = cfg.get('smtp_pass', '')
    to_email = cfg.get('smtp_to', 'kusumpakira1@gmail.com')
    port     = int(port_str) if str(port_str).isdigit() else 587
    
    if not host or not user or not password:
        logger.warning("SMTP configuration is incomplete. Skipping email alert.")
        return False
        
    try:
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(attachment_path))
                msg.attach(image)
                
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        logger.info(f"SMTP Email alert sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMTP email: {e}")
        return False

def restart_waha_container():
    logger.info("Triggering automatic WAHA container restart...")
    import socket
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect("/var/run/docker.sock")
        s.sendall(b"POST /containers/waha/restart HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        resp = s.recv(1024)
        s.close()
        logger.info(f"WAHA Container restart signal sent. Docker daemon response: {resp[:100]}")
        return True
    except Exception as e:
        logger.error(f"Failed to restart WAHA container via Docker socket: {e}")
        return False

def log_waha_event(event_type: str, status: str, details: str = None, db=None):
    """Accepts an existing db session to avoid opening a new connection."""
    from datetime import datetime
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        event = WAHAEvent(
            event_type=event_type,
            status=status,
            details=details,
            timestamp=datetime.now()
        )
        db.add(event)
        db.commit()
        logger.info(f"WAHA Event Logged: {event_type} | {status} | {details}")
    except Exception as e:
        logger.error(f"Failed to log WAHA event: {e}")
    finally:
        if own_session:
            db.close()

def sync_status_to_live(status, qr_code_base64=""):
    """Write WAHA status directly to MySQL — no HTTP call to live PHP server."""
    db = SessionLocal()
    try:
        for key, val in [("waha_status", status), ("waha_qr_base64", qr_code_base64)]:
            row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if row:
                row.value = val
            else:
                db.add(SystemSetting(key=key, value=val))
        db.commit()
        logger.info(f"WAHA status updated in DB directly: {status}")
    except Exception as e:
        logger.error(f"Error writing WAHA status to DB: {e}")
    finally:
        db.close()

def get_qr_base64(qr_path):
    if not qr_path or not os.path.exists(qr_path):
        return ""
    try:
        import base64
        with open(qr_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Failed to encode QR code: {e}")
        return ""

async def health_monitor_job():
    logger.info("Running WAHA Health Monitor...")
    primary_session = settings.WAHA_SESSION
    status = get_session_status(primary_session)
    
    # ── ONE single DB session for all reads/writes this run ──────────────────
    db = SessionLocal()
    try:
        # 1. Detect if status changed and log event (reuse same session)
        if status != alert_state["last_status"]:
            log_waha_event("status_changed", status,
                           f"WAHA session status changed from {alert_state['last_status']} to {status}",
                           db=db)
            alert_state["last_status"] = status
    finally:
        db.close()

    # 2. Get alert destinations from MEMORY CACHE (no extra DB connection)
    cfg = get_cached_settings()
    to_email   = cfg.get('smtp_to', 'kusumpakira1@gmail.com')
    alert_phone = cfg.get('waha_alert_phone', '7259510983')
        
    admin_phone = f"91{alert_phone}" if len(alert_phone) == 10 and alert_phone.isdigit() else alert_phone
    if not admin_phone.endswith('@c.us') and not admin_phone.endswith('@g.us') and not admin_phone.endswith('@lid'):
        admin_phone += '@c.us'

    if status in ("STOPPED", "FAILED", "SCAN_QR_CODE"):
        # ── Auto-restart with COOLDOWN (5 min) so WAHA can reach SCAN_QR_CODE ──
        if status in ("STOPPED", "FAILED"):
            global _last_restart_time
            now_ts = time.time()
            if now_ts - _last_restart_time >= RESTART_COOLDOWN_SEC:
                log_waha_event("stopped_restart", status, "WAHA session stopped/failed. Triggering container restart.", db=None)
                restart_waha_container()
                _last_restart_time = now_ts
                logger.info("WAHA restart triggered. Next restart allowed in 5 minutes.")
            else:
                remaining = int(RESTART_COOLDOWN_SEC - (time.time() - _last_restart_time))
                logger.info(f"WAHA is {status} — restart on cooldown ({remaining}s remaining). Waiting for SCAN_QR_CODE...")
        
        qr_path = None
        qr_base64 = ""
        if status == "SCAN_QR_CODE":
            logger.warning(f"Primary WAHA Session '{primary_session}' needs QR scan! Fetching QR...")
            qr_path = get_session_qr(primary_session)
            if qr_path:
                qr_base64 = get_qr_base64(qr_path)
        
        # Push Status and QR to live index.php server
        sync_status_to_live(status, qr_base64)

        # Send disconnect alert (once)
        if not alert_state["is_alerted"]:
            email_body = (
                f"Hello Admin,\n\n"
                f"Your Primary Farm Auto Bot is logged out (Status: {status}).\n\n"
                f"The system has automatically attempted to restart the bot.\n"
                f"A separate email with the QR code will be sent once WAHA is ready to reconnect.\n\n"
                f"You can also check the dashboard for live status and QR code."
            )
            send_smtp_email(f"🚨 URGENT: WAHA WhatsApp Bot disconnected ({status})", email_body, None)
            # NOTE: WhatsApp alert not possible here — WAHA itself is DOWN (status={status})
            logger.info(f"Disconnect email sent. WhatsApp alert skipped (WAHA is {status}, cannot send messages).")
            alert_state["is_alerted"] = True
        
        # Send QR code separately when WAHA is running but needs scan
        if status == "SCAN_QR_CODE" and not alert_state["qr_alerted"]:
            logger.info("WAHA needs QR scan — sending QR code to email...")
            email_body = (
                f"Hello Admin,\n\n"
                f"Your WhatsApp Bot needs to be reconnected. Please scan the attached QR code.\n\n"
                f"How to scan:\n"
                f"  1. Open WhatsApp on your phone\n"
                f"  2. Go to Settings → Linked Devices\n"
                f"  3. Tap 'Link a Device'\n"
                f"  4. Scan the QR code in this email\n\n"
                f"You can also scan directly from the dashboard."
            )
            send_smtp_email("📱 WhatsApp QR Code — Scan to Reconnect Bot", email_body, qr_path)
            alert_state["qr_alerted"] = True
    else:
        # Reconnected / Working fine
        sync_status_to_live(status)
        if alert_state["is_alerted"] and status == "WORKING":
            logger.info(f"Primary WAHA Session '{primary_session}' is back online!")
            # Send recovery email
            email_body = "Hello Admin,\n\nYour Primary Farm Auto Bot is back online and working perfectly!\nNo further action is required."
            send_smtp_email("✅ RECOVERY: WAHA WhatsApp Bot is back online", email_body)
            # Send WhatsApp recovery message via default session (now working)
            try:
                recovery_msg = "✅ *RECOVERY ALERT*\nYour Primary Farm Auto Bot is back online and working perfectly!"
                send_waha_message(admin_phone, recovery_msg, session=primary_session)
            except Exception as e:
                logger.warning(f"Could not send WhatsApp recovery notification: {e}")
            alert_state["is_alerted"] = False
            alert_state["qr_alerted"] = False

def _check_if_report_submitted(db, alarm, today) -> bool:
    report_type = alarm.report_type
    if not report_type:
        return False
        
    sender_phone = None
    group_name = None
    
    if alarm.target_type == 'employee':
        emp = db.query(Employee).filter(Employee.id == alarm.target_id).first()
        if emp:
            sender_phone = emp.phone_number
    elif alarm.target_type == 'group':
        if alarm.target_id:
            grp = db.query(Group).filter(Group.id == alarm.target_id).first()
            if grp:
                group_name = grp.name
        elif alarm.whatsapp_target_id:
            grp = db.query(Group).filter(Group.whatsapp_group_id == alarm.whatsapp_target_id).first()
            if grp:
                group_name = grp.name
                
    # Determine categories
    r_lower = report_type.lower()
    categories = []
    if "production" in r_lower:
        categories = ['production', 'egg_collection', 'egg_collection_1', 'egg_collection_2', 'egg']
    elif "feed" in r_lower:
        categories = ['feed']
    elif "expense" in r_lower:
        categories = ['expense', 'purchase']
    elif "sale" in r_lower:
        categories = ['sales']
    elif "profit" in r_lower or "p&l" in r_lower or "p and l" in r_lower:
        categories = ['sales', 'expense', 'purchase']
        
    # Check ProcessedData
    proc_query = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == today)
    if sender_phone:
        proc_query = proc_query.filter(ProcessedData.sender.contains(sender_phone))
    if group_name:
        proc_query = proc_query.filter(ProcessedData.group_name == group_name)
        
    if categories:
        if proc_query.filter(ProcessedData.category.in_(categories)).first():
            return True
    else:
        # Custom report types match inside notes (processed) or raw message text
        if proc_query.filter(ProcessedData.notes.ilike(f"%{report_type}%")).first():
            return True
            
        raw_query = db.query(RawMessage).filter(func.date(RawMessage.timestamp) == today)
        if sender_phone:
            raw_query = raw_query.filter(RawMessage.sender.contains(sender_phone))
        if group_name:
            raw_query = raw_query.filter(RawMessage.group_name == group_name)
            
        if raw_query.filter(RawMessage.raw_text.ilike(f"%{report_type}%")).first():
            return True
            
    return False

def execute_custom_alarm(alarm_id: int):
    db = SessionLocal()
    try:
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.now(IST).date()
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if not alarm or alarm.status != 'pending':
            return
            
        # Check if the report has already been submitted today
        if alarm.report_type:
            if _check_if_report_submitted(db, alarm, today):
                logger.info(f"Custom Alarm {alarm_id}: Report '{alarm.report_type}' already submitted today. Skipping WhatsApp reminder.")
                if alarm.frequency in ('once', 'timer') or not alarm.frequency:
                    alarm.status = 'sent'
                
                # Remove active nagging job if it exists
                nag_job_id = f"custom_alarm_{alarm_id}_nag"
                try:
                    scheduler.remove_job(nag_job_id)
                except Exception:
                    pass
                    
                db.commit()
                return
            
        target_whatsapp_id = None
        target_name = "Member"
        if alarm.target_type == 'employee':
            emp = db.query(Employee).filter(Employee.id == alarm.target_id).first()
            if emp:
                target_whatsapp_id = f"{emp.phone_number}@c.us"
                target_name = emp.name
        elif alarm.target_type == 'group':
            if alarm.target_id:
                grp = db.query(Group).filter(Group.id == alarm.target_id).first()
                if grp:
                    target_whatsapp_id = grp.whatsapp_group_id
                    target_name = grp.name
            elif alarm.whatsapp_target_id:
                target_whatsapp_id = alarm.whatsapp_target_id
                target_name = "Group"
                
        if target_whatsapp_id:
            if alarm.report_type:
                msg = f"⏰ *Reminder from Farm Auto*\nHi {target_name},\nYou have forgotten to send the *{alarm.report_type}* report today."
                if alarm.task_notes:
                    msg += f"\n\nNotes: {alarm.task_notes}"
            else:
                msg = f"🔔 *Custom Alarm / Task Reminder*\n\n{alarm.task_notes}"
                
            send_waha_message(target_whatsapp_id, msg)
            
        if alarm.frequency in ('once', 'timer') or not alarm.frequency:
            alarm.status = 'sent'
            
        # Schedule next nagging reminder if report is assigned and repeat_interval is set
        if alarm.report_type and alarm.repeat_interval and alarm.repeat_interval != 'none':
            nag_minutes = 0
            if alarm.repeat_interval == '5m': nag_minutes = 5
            elif alarm.repeat_interval == '10m': nag_minutes = 10
            elif alarm.repeat_interval == '15m': nag_minutes = 15
            elif alarm.repeat_interval == '30m': nag_minutes = 30
            elif alarm.repeat_interval == '1h': nag_minutes = 60
            
            if nag_minutes > 0:
                now_ist = datetime.now(IST)
                # Nag between 6 AM and 11 PM IST only
                if now_ist.hour < 23 and now_ist.hour >= 6:
                    next_nag_time = now_ist + timedelta(minutes=nag_minutes)
                    nag_job_id = f"custom_alarm_{alarm_id}_nag"
                    scheduler.add_job(
                        execute_custom_alarm,
                        DateTrigger(run_date=next_nag_time, timezone="Asia/Kolkata"),
                        args=[alarm_id],
                        id=nag_job_id,
                        replace_existing=True,
                        misfire_grace_time=None
                    )
                    logger.info(f"Scheduled nagging reminder for custom alarm {alarm_id} at {next_nag_time} (every {alarm.repeat_interval})")
                else:
                    logger.info(f"Custom Alarm {alarm_id}: Late night reached (11 PM - 6 AM). Stopping nagging reminders for today.")
                    
        db.commit()
    except Exception as e:
        logger.error(f"Error executing custom alarm {alarm_id}: {e}")
    finally:
        db.close()

def schedule_custom_alarm(alarm_id: int, trigger_time):
    global scheduler
    db = SessionLocal()
    try:
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if not alarm:
            return
            
        job_id = f"custom_alarm_{alarm_id}"
        freq = alarm.frequency or 'once'
        
        if freq == 'once':
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_5m':
            trigger = IntervalTrigger(minutes=5, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_10m':
            trigger = IntervalTrigger(minutes=10, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_15m':
            trigger = IntervalTrigger(minutes=15, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_30m':
            trigger = IntervalTrigger(minutes=30, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'every_1h':
            trigger = IntervalTrigger(hours=1, start_date=trigger_time, timezone="Asia/Kolkata")
        elif freq == 'daily':
            trigger = CronTrigger(hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'weekly':
            # trigger_time.weekday() returns 0 (Mon) - 6 (Sun)
            trigger = CronTrigger(day_of_week=trigger_time.weekday(), hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'monthly':
            trigger = CronTrigger(day=trigger_time.day, hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'yearly':
            trigger = CronTrigger(month=trigger_time.month, day=trigger_time.day, hour=trigger_time.hour, minute=trigger_time.minute, timezone="Asia/Kolkata")
        elif freq == 'timer':
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        else:
            trigger = DateTrigger(run_date=trigger_time, timezone="Asia/Kolkata")
        scheduler.add_job(
            execute_custom_alarm,
            trigger,
            args=[alarm_id],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=None
        )
    except Exception as e:
        logger.error(f"Error scheduling custom alarm {alarm_id}: {e}")
    finally:
        db.close()

def get_next_occurrence(base_time, frequency):
    from datetime import timedelta, datetime
    next_time = base_time
    from datetime import timezone
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    while next_time <= now_ist:
        if frequency == 'weekly':
            next_time += timedelta(days=7)
        elif frequency == 'monthly':
            import calendar
            month = next_time.month - 1 + 1
            year = next_time.year + month // 12
            month = month % 12 + 1
            day = min(next_time.day, calendar.monthrange(year, month)[1])
            next_time = next_time.replace(year=year, month=month, day=day)
        elif frequency == 'yearly':
            try:
                next_time = next_time.replace(year=next_time.year + 1)
            except ValueError:
                next_time += timedelta(days=365)
        else:
            next_time += timedelta(days=1)
    return next_time

def format_report_list(reports):
    if not reports:
        return ""
    cleaned = []
    for r in reports:
        rl = r.lower()
        if "production" in rl:
            cleaned.append("production")
        elif "feed" in rl:
            cleaned.append("feed")
        elif "expense" in rl or "expenditure" in rl:
            cleaned.append("expense")
        elif "sale" in rl:
            cleaned.append("sales")
        elif "profit" in rl or "p&l" in rl or "p and l" in rl:
            cleaned.append("Profit & Loss")
        else:
            cleaned.append(r)
            
    if len(cleaned) == 1:
        return cleaned[0]
    elif len(cleaned) == 2:
        return f"{cleaned[0]} & {cleaned[1]}"
    else:
        return ", ".join(cleaned[:-1]) + f" & {cleaned[-1]}"

def format_name_list(names):
    if not names:
        return ""
    bold_names = [f"*{n}*" for n in names]
    if len(bold_names) == 1:
        return bold_names[0]
    elif len(bold_names) == 2:
        return f"{bold_names[0]} & {bold_names[1]}"
    else:
        return ", ".join(bold_names[:-1]) + f" & {bold_names[-1]}"

def poll_and_execute_unified_reminders():
    logger.info("Polling database for pending unified reminders...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    today = now_ist.date()

    # Date formats for flexible matching (e.g. EOD report)
    # e.g., "15-07", "15/07", "15 July", "July 15"
    date_formats = [
        today.strftime("%d-%m"),
        today.strftime("%d/%m"),
        today.strftime("%d %B"),
        today.strftime("%B %d"),
        today.strftime("%dth %B"),
        today.strftime("%B %dth"),
    ]
    # Clean date formats to remove leading zeros (e.g. "5 July" instead of "05 July")
    cleaned_dates = []
    for df in date_formats:
        cleaned_dates.append(df.lower())
        if df.startswith("0"):
            cleaned_dates.append(df[1:].lower())
        cleaned_dates.append(df.replace(" 0", " ").lower())
    date_formats = list(set(cleaned_dates))
    update_keywords = ["update", "updates", "eod", "work update", "daily update", "daily work update", "eod update", "daily report", "report"]

    # ── WAHA guard: don't attempt sends if WhatsApp session is not WORKING ──
    primary_session = settings.WAHA_SESSION
    waha_status = get_session_status(primary_session)
    if waha_status != "WORKING":
        logger.warning(f"WAHA session is {waha_status} — skipping reminder dispatch. Will retry next cycle.")
        return
    
    db = SessionLocal()
    try:
        # (Midnight reset is handled by midnight_reset_job at 00:00 IST)

        pending = db.query(UnifiedReminder).filter(
            UnifiedReminder.status == 'pending',
            UnifiedReminder.trigger_time <= now_ist
        ).all()
        
        if not pending:
            return
            
        submissions = db.query(ProcessedData).filter(
            func.date(ProcessedData.processed_time) == today
        ).all()
        
        raw_messages = db.query(RawMessage).filter(
            func.date(RawMessage.timestamp) == today
        ).all()
        
        groups = db.query(Group).all()
        group_names_by_id = {g.whatsapp_group_id: g.name for g in groups}
        
        # Merge WAHA groups map
        waha_groups_map = get_all_waha_groups_map()
        for jid, name in waha_groups_map.items():
            if jid not in group_names_by_id:
                group_names_by_id[jid] = name
        
        for r in pending:
            phones = [p.strip() for p in str(r.person_phone or '').split(',') if p.strip()]
            names = [n.strip() for n in str(r.person_name or '').split(',') if n.strip()]
            
            # Map of phone -> name
            assignees = {}
            for idx, phone in enumerate(phones):
                name = names[idx] if idx < len(names) else phone
                assignees[phone] = name
                
            assigned_reports = [s.strip().lower() for s in str(r.report_types or '').split(',') if s.strip()]
            
            pending_assignees = []
            
            # Check submissions for each assignee individually
            for phone, name in assignees.items():
                # Clean phone number by keeping only digits
                clean_phone = "".join(c for c in phone if c.isdigit())
                if clean_phone.startswith("0"):
                    clean_phone = clean_phone[1:]
                
                if len(clean_phone) == 10:
                    target_jid = "91" + clean_phone
                else:
                    target_jid = clean_phone
                    
                if not target_jid.endswith('@c.us') and not target_jid.endswith('@g.us') and not target_jid.endswith('@lid'):
                    target_jid += '@c.us'
                
                # Build report-type keyword map for raw message fallback check
                REPORT_KEYWORDS = {
                    'production': ['shead', 'egg', 'lps', 'hrt', 'mortality', 'hitstoke', 'alc', 'production', 'collection', 'week bird', 'bird count'],
                    'feed':       ['feed', 'maize', 'soya', 'bran', 'fodder'],
                    'sales':      ['sale', 'sold', 'invoice', 'dispatch', 'unload'],
                    'sale':       ['sale', 'sold', 'invoice', 'dispatch', 'unload'],
                    'expense':    ['expense', 'expenditure', 'payment', 'bill', 'amount paid'],
                    'expenditure':['expense', 'expenditure', 'payment', 'bill', 'amount paid'],
                    'profit':     ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
                    'p&l':        ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
                    'p and l':    ['sale', 'sold', 'expense', 'expenditure', 'profit', 'loss'],
                }

                missing_reports = []
                for report in assigned_reports:
                    submitted = False
                    categories = []
                    if "production" in report:
                        categories = ['production', 'egg_collection', 'egg_collection_1', 'egg_collection_2', 'egg']
                    elif "feed" in report:
                        categories = ['feed']
                    elif "expense" in report or "expenditure" in report:
                        categories = ['expense', 'purchase']
                    elif "sale" in report:
                        categories = ['sales']
                    elif "profit" in report or "p&l" in report or "p and l" in report:
                        categories = ['sales', 'expense', 'purchase']
                        
                    is_update_report = any(w in report for w in ["update", "eod", "daily report"]) and "egg pricing" not in report.lower()

                    for sub in submissions:
                        # Match by phone — check both with and without country code 91
                        alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                        match_sender = clean_phone in str(sub.sender) or alt_phone in str(sub.sender)
                        group_name = group_names_by_id.get(r.whatsapp_group_id)
                        match_group = r.whatsapp_group_id and group_name and sub.group_name and str(sub.group_name).lower() == group_name.lower()
                        
                        # Fallback for LIDs (Hidden Phone Numbers): Match by Name using fuzzy string matching
                        match_name = False
                        if not match_sender and r.person_name and sub.sender:
                            import difflib
                            sender_name_part = clean_name_string(sub.sender.split(' (')[0])
                            t_names = [clean_name_string(n) for n in r.person_name.split(',')]
                            for t_name in t_names:
                                if len(sender_name_part) >= 3 and len(t_name) >= 3:
                                    ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                                    if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                                        match_name = True
                                        break
                        
                        # Match if sender is the manager (Kusum) satisfying the reminder privately
                        match_waha_sender = False
                        if sub.sender:
                            import difflib
                            sender_name_part = clean_name_string(sub.sender.split(' (')[0])
                            manager_name = clean_name_string("kusum")
                            ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                            if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                                match_waha_sender = True
                        
                        if match_sender or match_group or match_name or match_waha_sender:
                            if "egg pricing" in report.lower():
                                sub_notes_lower = str(sub.notes or '').lower()
                                time_keyword = "morning" if "morning" in report.lower() else "afternoon" if "afternoon" in report.lower() else "evening" if "evening" in report.lower() else None
                                if time_keyword and time_keyword in sub_notes_lower and any(w in sub_notes_lower for w in ["egg", "price", "pricing"]):
                                    submitted = True
                                    break
                            elif is_update_report:
                                sub_notes_lower = str(sub.notes or '').lower()
                                if any(kw in sub_notes_lower for kw in update_keywords) or any(df in sub_notes_lower for df in date_formats):
                                    submitted = True
                                    break
                            elif categories:
                                if sub.category in categories:
                                    submitted = True
                                    break
                            else:
                                if report in str(sub.notes).lower():
                                    submitted = True
                                    break

                    # Fallback: also check raw messages for keyword matches
                    if not submitted:
                        raw_keywords = []
                        if is_update_report:
                            raw_keywords = update_keywords + date_formats
                        else:
                            for key, kws in REPORT_KEYWORDS.items():
                                if key in report:
                                    raw_keywords = kws
                                    break
                            if not raw_keywords:
                                # Generic: match any keyword from report name itself
                                raw_keywords = [w for w in report.split() if len(w) > 3]

                        group_name = group_names_by_id.get(r.whatsapp_group_id)
                        for raw_msg in raw_messages:
                            raw_text_lower = str(raw_msg.raw_text or '').lower()
                            alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                            match_sender_raw = clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender)
                            match_group_raw = (
                                r.whatsapp_group_id and group_name
                                and raw_msg.group_name
                                and str(raw_msg.group_name).lower() == group_name.lower()
                            )
                            # Fallback for LIDs (Hidden Phone Numbers): Match by Name using fuzzy string matching
                            match_name = False
                            if not match_sender_raw and r.person_name and raw_msg.sender:
                                import difflib
                                # raw_msg.sender format: "Name (Phone)" -> Extract Name
                                sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                                t_names = [clean_name_string(n) for n in r.person_name.split(',')]
                                for t_name in t_names:
                                    if len(sender_name_part) >= 3 and len(t_name) >= 3:
                                        ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                                        if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                                            match_name = True
                                            break
                            
                            # Match if sender is the manager (Kusum) satisfying the reminder privately
                            match_waha_sender_raw = False
                            if raw_msg.sender:
                                import difflib
                                sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                                manager_name = clean_name_string("kusum")
                                ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                                if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                                    match_waha_sender_raw = True
                            
                            if match_sender_raw or match_group_raw or match_name or match_waha_sender_raw:
                                if "egg pricing" in report.lower():
                                    time_keyword = "morning" if "morning" in report.lower() else "afternoon" if "afternoon" in report.lower() else "evening" if "evening" in report.lower() else None
                                    if time_keyword and time_keyword in raw_text_lower and any(w in raw_text_lower for w in ["egg", "price", "pricing"]):
                                        submitted = True
                                        logger.info(f"Egg pricing raw message match for '{report}' from {raw_msg.sender} — skipping reminder.")
                                        break
                                else:
                                    if any(kw.lower() in raw_text_lower for kw in raw_keywords):
                                        submitted = True
                                        logger.info(f"Raw message keyword match for '{report}' from {raw_msg.sender} — skipping reminder.")
                                        break

                    if not submitted:
                        missing_reports.append(report)
                
                if not assigned_reports or missing_reports:
                    pending_assignees.append({
                        "name": name,
                        "phone": phone,
                        "jid": target_jid,
                        "missing_reports": missing_reports
                    })
                    
            if pending_assignees:
                # Re-check WAHA is still WORKING right before sending
                if get_session_status(primary_session) != "WORKING":
                    logger.warning(f"WAHA went down before sending reminder for {r.person_name}. Will retry next cycle.")
                    continue

                # 1. Send private reminder to each pending assignee
                for p in pending_assignees:
                    if not assigned_reports:
                        private_body = r.task_notes
                    else:
                        missing_str = format_report_list(p['missing_reports'])
                        private_body = f"Please submit today's *{missing_str}* Report so the daily records and reports can be completed accurately."
                    
                    private_msg = (
                        "⏰Reminder\n\n"
                        f"Hi *{p['name']}*,\n\n"
                        f"{private_body}\n\n"
                        "Thank you! 🌱"
                    )
                    
                    logger.info(f"Sending private reminder to {p['name']} ({p['jid']})")
                    send_waha_message(p['jid'], private_msg)
                
                # 2. Send single group reminder mentioning all pending assignees
                if r.whatsapp_group_id:
                    name_tags = format_name_list([p['name'] for p in pending_assignees])
                    jids = [p['jid'] for p in pending_assignees]
                    
                    if not assigned_reports:
                        group_body = r.task_notes
                    else:
                        all_missing = sorted(list(set([rep for p in pending_assignees for rep in p['missing_reports']])))
                        missing_str = format_report_list(all_missing)
                        group_body = f"Please submit today's *{missing_str}* Report so the daily records and reports can be completed accurately."
                        
                    group_msg = (
                        "⏰Reminder\n\n"
                        f"Hi {name_tags},\n\n"
                        f"{group_body}\n\n"
                        "Thank you! 🌱"
                    )
                        
                    logger.info(f"Sending combined group reminder to {r.whatsapp_group_id} for {', '.join([p['name'] for p in pending_assignees])}")
                    send_waha_message(r.whatsapp_group_id, group_msg, mentions=jids)
                    
                repeat = str(r.repeat_interval).lower()
                if repeat != 'none' and repeat != '':
                    minutes = 0
                    if repeat == '5m': minutes = 5
                    elif repeat == '10m': minutes = 10
                    elif repeat == '15m': minutes = 15
                    elif repeat == '30m': minutes = 30
                    elif repeat == '1h': minutes = 60
                    
                    if minutes > 0 and now_ist.hour >= 6 and now_ist.hour < 23:
                        r.trigger_time = now_ist + timedelta(minutes=minutes)
                        db.commit()
                        logger.info(f"Nagging reminder scheduled for {r.person_name} in {minutes} mins.")
                        continue
                
                # Sent: Actual message(s) sent out
                r.status = 'sent'
                db.commit()
                logger.info(f"Reminder for {r.person_name} marked sent at {r.trigger_time} (frequency: {r.frequency}). Will reset at midnight.")
            else:
                # Skipped: All assignees had already submitted reports
                r.status = 'skipped'
                db.commit()
                logger.info(f"Reminder for {r.person_name} marked skipped at {r.trigger_time} (all reports submitted). Will reset at midnight.")
            
    except Exception as e:
        logger.error(f"Error in poll_and_execute_unified_reminders: {e}")
    finally:
        db.close()

def sync_custom_alarms_job():
    db = SessionLocal()
    try:
        pending_alarms = db.query(CustomAlarm).filter(CustomAlarm.status == 'pending').all()
        for alarm in pending_alarms:
            job_id = f"custom_alarm_{alarm.id}"
            if not scheduler.get_job(job_id):
                logger.info(f"Dynamically scheduling custom alarm {alarm.id} (frequency: {alarm.frequency}) for {alarm.trigger_time}")
                schedule_custom_alarm(alarm.id, alarm.trigger_time)
    except Exception as e:
        logger.error(f"Error in sync_custom_alarms_job: {e}")
    finally:
        db.close()

async def cleanup_old_files_job():
    logger.info("Starting media and report directory cleanup...")
    import os
    import time
    now = time.time()
    cutoff_time = now - (2 * 24 * 3600)  # 2 days ago
    
    # Clean /app/media/ for files older than 2 days
    media_dir = "/app/media"
    if os.path.exists(media_dir):
        for item in os.listdir(media_dir):
            item_path = os.path.join(media_dir, item)
            if os.path.isfile(item_path):
                # Don't delete QR session images or persistent keys
                if item.startswith("qr_") or item == "keys.json":
                    continue
                try:
                    if os.path.getmtime(item_path) < cutoff_time:
                        os.remove(item_path)
                except Exception as e:
                    logger.error(f"Error removing old media file {item_path}: {e}")
                    
    # Clean /app/media/reports for files older than 7 days
    reports_dir = "/app/media/reports"
    cutoff_reports = now - (7 * 24 * 3600)  # 7 days ago
    if os.path.exists(reports_dir):
        for item in os.listdir(reports_dir):
            item_path = os.path.join(reports_dir, item)
            if os.path.isfile(item_path):
                try:
                    if os.path.getmtime(item_path) < cutoff_reports:
                        os.remove(item_path)
                except Exception as e:
                    logger.error(f"Error removing old report file {item_path}: {e}")

def sync_groups_to_live():
    logger.info("Syncing local WAHA groups to live server...")
    try:
        import os
        import requests
        waha_url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/groups"
        headers = {"Accept": "application/json"}
        api_key = os.getenv("WAHA_API_KEY", "123")
        if api_key: headers["X-Api-Key"] = api_key
        
        response = requests.get(waha_url, headers=headers, timeout=10)
        if response.status_code == 200:
            groups = []
            data = response.json()
            if isinstance(data, list):
                for g in data:
                    groups.append({"id": g.get("id"), "name": g.get("subject") or g.get("name")})
            elif isinstance(data, dict):
                for k, v in data.items():
                    groups.append({"id": k, "name": v.get("subject") or v.get("name")})
            
            payload = {"status": "success", "groups": groups}
            sync_resp = requests.post("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=waha/groups/sync", json=payload, timeout=10)
            if sync_resp.status_code == 200:
                logger.info(f"Successfully synced {len(groups)} groups to live server.")
            else:
                logger.error(f"Failed to sync groups to live server. Status: {sync_resp.status_code}")
        else:
            logger.error(f"Failed to fetch groups from local WAHA. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error syncing groups: {e}")

def poll_live_alarms():
    """Read and execute custom alarms directly from MySQL — no HTTP call to live PHP server."""
    logger.info("Checking DB for pending custom alarms...")
    db = SessionLocal()
    try:
        from datetime import datetime, timezone, timedelta
        IST = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(IST).replace(tzinfo=None)

        pending = db.query(CustomAlarm).filter(
            CustomAlarm.status == 'pending',
            CustomAlarm.trigger_time <= now_ist
        ).all()

        if not pending:
            logger.debug("No pending custom alarms.")
            return

        for alarm in pending:
            target_id = alarm.whatsapp_target_id
            if not target_id:
                continue
            notes = alarm.task_notes or ''
            logger.info(f"Triggering custom alarm {alarm.id} to {target_id}")
            msg = f"🔔 *Custom Alarm*\n\n{notes}"
            send_waha_message(target_id, msg)
            alarm.status = 'sent'

        db.commit()
    except Exception as e:
        logger.error(f"Error processing custom alarms: {e}")
    finally:
        db.close()


def midnight_reset_job():
    """Runs at 00:00 IST every night.
    Advances trigger_time for sent recurring reminders and tasks to the next occurrence
    and resets their status to 'pending'.
    """
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    logger.info(f"Running midnight reset job at {now_ist}")

    db = SessionLocal()
    try:
        # 1. Reset reminders
        sent_recurring = db.query(UnifiedReminder).filter(
            UnifiedReminder.status.in_(['sent', 'skipped']),
            UnifiedReminder.frequency != 'once'
        ).all()

        reset_count = 0
        for r in sent_recurring:
            freq = str(r.frequency).lower()
            r.trigger_time = get_next_occurrence(r.trigger_time, freq)
            r.status = 'pending'
            reset_count += 1
            logger.info(f"Midnight reset reminder: {r.person_name} → next trigger: {r.trigger_time} (freq: {freq})")

        # 2. Reset tasks
        completed_tasks = db.query(Task).filter(
            Task.status == 'completed',
            Task.frequency != 'once'
        ).all()

        for t in completed_tasks:
            freq = str(t.frequency).lower()
            t.due_time = get_next_occurrence(t.due_time, freq)
            t.status = 'pending'
            reset_count += 1
            logger.info(f"Midnight reset task: {t.task_name} → next trigger: {t.due_time} (freq: {freq})")

        db.commit()
        logger.info(f"Midnight reset complete: {reset_count} items reset to pending.")
    except Exception as e:
        logger.error(f"Error in midnight_reset_job: {e}")
    finally:
        db.close()


def get_interval_minutes(interval):
    if not interval or interval == 'none':
        return 0
    interval = str(interval).lower()
    if interval.endswith('m'):
        try: return int(interval[:-1])
        except: return 0
    if interval.endswith('h'):
        try: return int(interval[:-1]) * 60
        except: return 0
    return 0


async def poll_and_remind_tasks_job():
    """Polls database for overdue/pending tasks and sends alerts/reminders with custom nagging intervals."""
    logger.info("Polling database for pending/overdue tasks...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)

    db = SessionLocal()
    try:
        # 1. Update status to overdue if deadline passed and still pending
        overdue_tasks = db.query(Task).filter(
            Task.status == 'pending',
            Task.due_time <= now_ist
        ).all()
        for t in overdue_tasks:
            t.status = 'overdue'
            db.commit()
            logger.info(f"Task ID {t.id} ('{t.task_name}') marked overdue.")

        # 1.5 AUTO-COMPLETE TASKS (Python background equivalent of index.php logic)
        try:
            pending_tasks = db.query(Task).filter(Task.status.in_(['pending', 'overdue'])).all()
            default_keywords = ['done', 'completed', 'finish', 'finished', 'ok done', 'complete', 'ho gaya', 'ho gya', 'kar diya', '✅', 'done✅']
            
            group_task_counts = {}
            phone_task_counts = {}
            for t in pending_tasks:
                if t.whatsapp_group_id:
                    gid = t.whatsapp_group_id
                    group_task_counts[gid] = group_task_counts.get(gid, 0) + 1
                if t.assigned_person_phone:
                    for ph in [x.strip() for x in t.assigned_person_phone.split(',') if x.strip()]:
                        digits = "".join(filter(str.isdigit, ph))
                        if len(digits) == 10: digits = "91" + digits
                        if digits: phone_task_counts[digits] = phone_task_counts.get(digits, 0) + 1
            
            for t in pending_tasks:
                keywords = list(default_keywords)
                if t.completion_keywords:
                    keywords.extend([x.strip().lower() for x in t.completion_keywords.split(',')])
                
                import re
                task_name_words = re.sub(r'[^a-zA-Z0-9\s]', '', t.task_name).lower().split()
                task_identifiers = [w for w in task_name_words if len(w) > 3 and w not in ['task', 'check', 'please', 'update', 'submit', 'report']]
                
                # Look back up to 24 hours to catch early completions!
                since = now_ist - timedelta(hours=24)
                if t.created_at and t.created_at > since:
                    since = t.created_at
                
                all_messages = []
                is_ambiguous = False
                matched = False
                
                # Check group messages
                if t.whatsapp_group_id:
                    grp_id = t.whatsapp_group_id
                    if group_task_counts.get(grp_id, 0) > 1: is_ambiguous = True
                    if '@' not in grp_id: grp_id += '@g.us'
                    
                    msgs = db.query(WhatsAppMessage.message_text).filter(
                        WhatsAppMessage.group_id == grp_id,
                        WhatsAppMessage.timestamp >= since
                    ).order_by(WhatsAppMessage.timestamp.desc()).limit(30).all()
                    all_messages.extend([m[0] for m in msgs if m[0]])
                
                # Check individual messages
                if t.assigned_person_phone:
                    phones_raw = [x.strip() for x in t.assigned_person_phone.split(',')]
                    phone_patterns = []
                    for ph in phones_raw:
                        digits = "".join(filter(str.isdigit, ph))
                        if len(digits) == 10: digits = "91" + digits
                        if digits:
                            phone_patterns.append(digits)
                            if phone_task_counts.get(digits, 0) > 1: is_ambiguous = True
                    
                    if phone_patterns:
                        from sqlalchemy import or_
                        conditions = [RawMessage.sender.like(f"%{p}%") for p in phone_patterns]
                        msgs = db.query(RawMessage.raw_text).filter(
                            RawMessage.timestamp >= since,
                            or_(*conditions)
                        ).order_by(RawMessage.timestamp.desc()).limit(20).all()
                        all_messages.extend([m[0] for m in msgs if m[0]])
                
                if not all_messages: continue
                
                for msg_text in all_messages:
                    msg_lower = msg_text.lower().strip()
                    has_completion = any(kw in msg_lower for kw in keywords if kw)
                    if has_completion:
                        if is_ambiguous and task_identifiers:
                            has_identifier = any(id_kw in msg_lower for id_kw in task_identifiers)
                            if has_identifier:
                                matched = True
                                break
                        else:
                            matched = True
                            break
                            
                if matched:
                    t.status = 'completed'
                    t.completion_details = 'Auto-completed: WhatsApp reply detected'
                    db.commit()
                    logger.info(f"Task ID {t.id} ('{t.task_name}') auto-completed from WhatsApp reply.")
        except Exception as e:
            logger.error(f"Error in auto-completing tasks: {e}")

        # 2. Get all overdue tasks and trigger reminders
        tasks = db.query(Task).filter(Task.status == 'overdue').all()
        for t in tasks:
            diff = now_ist - t.due_time
            if diff.total_seconds() < 0:
                continue
                
            minutes_ago = int(diff.total_seconds() / 60.0)
            interval_min = get_interval_minutes(t.repeat_interval)
            
            should_remind = False
            if interval_min:
                # If they set "every 5m", it triggers at 0, 5, 10, etc.
                if minutes_ago % interval_min == 0:
                    should_remind = True
            else:
                # NAG ONCE: If no repeat interval, just send ONCE
                if minutes_ago == 0:
                    should_remind = True

            if should_remind:
                targets = []
                if t.whatsapp_group_id:
                    target_jid = t.whatsapp_group_id
                    if not target_jid.endswith('@g.us') and not target_jid.endswith('@c.us'):
                        target_jid += '@g.us'
                    targets.append((target_jid, t.assigned_person_name or "Team Members"))
                elif t.assigned_person_phone:
                    phones = [p.strip() for p in t.assigned_person_phone.split(',') if p.strip()]
                    names = [n.strip() for n in (t.assigned_person_name or "").split(',') if n.strip()]
                    for idx, phone in enumerate(phones):
                        clean = "".join(filter(str.isdigit, phone))
                        if not clean:
                            continue
                        if len(clean) == 10:
                            target_jid = "91" + clean + "@c.us"
                        else:
                            target_jid = clean + "@c.us"
                        name = names[idx] if idx < len(names) else "Team Member"
                        targets.append((target_jid, name))

                for target, target_name in targets:
                    is_personal = t.task_type and 'Personal' in t.task_type
                    if is_personal:
                        msg = f"🔔 *Task Reminder* 🔔\n\n{t.task_name}"
                    else:
                        is_feed_formula = t.task_type and ('approval' in t.task_type.lower() or 'feed formula' in t.task_name.lower())
                        if is_feed_formula:
                            msg = (
                                f"⚠️ *Task Overdue Alert*\n\n"
                                f"Hi Team,\n"
                                f"The deadline for task *\"{t.task_name}\"* has passed.\n\n"
                                f"Please complete this work and reply to this message with *\"updated\"* & *\"approved\"* once finished."
                            )
                        else:
                            msg = (
                                f"⚠️ *Task Overdue Alert*\n\n"
                                f"Hi {target_name},\n"
                                f"The deadline for task *\"{t.task_name}\"* has passed.\n\n"
                                f"Please complete this work and reply to this message with *\"done\"* or *\"completed\"* once finished."
                            )
                    logger.info(f"Sending overdue task alert to {target} for '{t.task_name}'")
                    send_waha_message(target, msg)
    except Exception as e:
        logger.error(f"Error in poll_and_remind_tasks_job: {e}")
    finally:
        db.close()


async def create_wednesday_meeting_tasks():
    """Runs every Wednesday at 6:00 AM to create the standard weekly meeting follow-up tasks."""
    logger.info("Generating standard Wednesday meeting follow-up tasks...")
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)

    meetings = [
        "Meeting conducted with shed worker's",
        "Meeting conducted with feed plant worker's",
        "Meeting conducted with egg godown worker's",
        "Meeting conducted with shed supervisors",
        "Morning feed and water medicine incharges"
    ]

    db = SessionLocal()
    try:
        due = now_ist.replace(hour=17, minute=0, second=0, microsecond=0)
        
        for m in meetings:
            existing = db.query(Task).filter(
                Task.task_name == m,
                func.date(Task.due_time) == due.date()
            ).first()
            if not existing:
                new_task = Task(
                    task_name=m,
                    task_type='meeting',
                    assigned_person_name="Supervisors",
                    whatsapp_group_id="120363428417403024@g.us", # Farm Supervisors group
                    due_time=due,
                    completion_keywords="points, minutes, checklist, discussed",
                    status='pending'
                )
                db.add(new_task)
        db.commit()
        logger.info("Wednesday meeting tasks successfully generated.")
    except Exception as e:
        logger.error(f"Error in create_wednesday_meeting_tasks: {e}")
    finally:
        db.close()


async def manager_escalation_job():
    logger.info("Starting 8:00 PM Manager Escalation Check...")
    manager_phone = settings.MANAGER_PHONE
    if not manager_phone:
        logger.warning("No manager phone configured for escalation.")
        return
        
    manager_jid = manager_phone
    if not manager_jid.endswith('@c.us') and not manager_jid.endswith('@g.us') and not manager_jid.endswith('@lid'):
        manager_jid += '@c.us'

    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)
    start_of_day = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)

    db = SessionLocal()
    escalation_lines = []
    waha_groups_map = get_all_waha_groups_map()
    
    try:
        raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()
        processed_today_all = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == start_of_day.date()).all()
        
        # 1. Check Tasks
        overdue_tasks = db.query(Task).filter(
            Task.status.in_(['pending', 'overdue']),
            Task.due_time <= now_ist
        ).all()
        
        if overdue_tasks:
            escalation_lines.append("*[Missed Tasks]*")
            for t in overdue_tasks:
                assignee = t.assigned_person_name
                if not assignee and t.whatsapp_group_id:
                    clean_jid = t.whatsapp_group_id.replace('@g.us', '') + '@g.us'
                    grp = db.query(Group).filter(Group.whatsapp_group_id == clean_jid).first()
                    if grp:
                        assignee = f"[{grp.name}]"
                    elif clean_jid in waha_groups_map:
                        assignee = f"[{waha_groups_map[clean_jid]}]"
                    else:
                        assignee = f"[{t.whatsapp_group_id}]"
                elif not assignee:
                    assignee = t.assigned_person_phone or "Unknown"
                    
                escalation_lines.append(f"- ❌ {assignee} failed to complete task: *{t.task_name}* (Due: {t.due_time.strftime('%I:%M %p')})")

        # 2. Check Unified Reminders (Reports)
        reminders_today = db.query(UnifiedReminder).filter(
            UnifiedReminder.trigger_time >= start_of_day,
            UnifiedReminder.trigger_time <= now_ist
        ).all()
        
        missed_reports = []
        for r in reminders_today:
            if r.status == 'skipped':
                continue
                
            clean_group_jid = None
            group_name_display = None
            if r.whatsapp_group_id:
                clean_group_jid = r.whatsapp_group_id
                if not clean_group_jid.endswith('@g.us'):
                    clean_group_jid += '@g.us'
                    
                # Get group name for display
                group = db.query(Group).filter(Group.whatsapp_group_id == clean_group_jid).first()
                if group:
                    group_name_display = group.name
                elif clean_group_jid in waha_groups_map:
                    group_name_display = waha_groups_map[clean_group_jid]
                else:
                    group_name_display = clean_group_jid
            
            # Filter raw messages today for this assignee/group matching JID or NameFallback in python
            msgs_today = []
            for raw_msg in raw_messages_today:
                clean_phone = "".join(c for c in r.person_phone if c.isdigit())
                if clean_phone.startswith("0"):
                    clean_phone = clean_phone[1:]
                alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                
                match_sender_raw = clean_phone in str(raw_msg.sender) or alt_phone in str(raw_msg.sender)
                match_group_raw = False
                if clean_group_jid:
                    group_name = waha_groups_map.get(clean_group_jid)
                    match_group_raw = (
                        raw_msg.group_name
                        and group_name
                        and str(raw_msg.group_name).lower() == group_name.lower()
                    )
                
                # Name fallback for LIDs
                match_name = False
                if not match_sender_raw and r.person_name and raw_msg.sender:
                    import difflib
                    sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                    t_names = [clean_name_string(n) for n in r.person_name.split(',')]
                    for t_name in t_names:
                        if len(sender_name_part) >= 3 and len(t_name) >= 3:
                            ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                            if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                                match_name = True
                                break
                
                # Match if sender is the manager (Kusum) satisfying the reminder privately
                match_waha_sender_raw = False
                if raw_msg.sender:
                    import difflib
                    sender_name_part = clean_name_string(raw_msg.sender.split(' (')[0])
                    manager_name = clean_name_string("kusum")
                    ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                    if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                        match_waha_sender_raw = True
                                
                if match_sender_raw or match_group_raw or match_name or match_waha_sender_raw:
                    msgs_today.append(raw_msg)
            
            report_keywords = []
            if r.report_types:
                rt_lower = r.report_types.lower()
                if 'production' in rt_lower: report_keywords.extend(['production', 'eggs', 'shed', 'trays', 'collection'])
                if 'feed' in rt_lower: report_keywords.extend(['feed', 'bags', 'formula', 'intake', 'kg'])
                if 'mortality' in rt_lower: report_keywords.extend(['mortality', 'dead', 'birds'])
                if 'sales' in rt_lower or 'expenses' in rt_lower or 'profit' in rt_lower or 'loss' in rt_lower: 
                    report_keywords.extend(['sales', 'expenses', 'expense', 'profit', 'loss', 'amount', 'rs'])
            
            if not report_keywords:
                report_keywords = ['update', 'report', 'done', 'completed']
                
            is_egg_pricing = "egg pricing" in r.report_types.lower()
            submitted = False
            for m in msgs_today:
                text_lower = (m.raw_text or "").lower()
                if is_egg_pricing:
                    time_keyword = "morning" if "morning" in r.report_types.lower() else "afternoon" if "afternoon" in r.report_types.lower() else "evening" if "evening" in r.report_types.lower() else None
                    if time_keyword and time_keyword in text_lower and any(w in text_lower for w in ["egg", "price", "pricing"]):
                        submitted = True
                        break
                else:
                    if any(kw in text_lower for kw in report_keywords):
                        submitted = True
                        break
                    
            if not submitted:
                    # Filter processed data for AI-categorized images/documents in python (NameFallback included)
                processed_today = []
                for p in processed_today_all:
                    clean_phone = "".join(c for c in r.person_phone if c.isdigit())
                    if clean_phone.startswith("0"):
                        clean_phone = clean_phone[1:]
                    alt_phone = ("91" + clean_phone) if len(clean_phone) == 10 else clean_phone[2:] if clean_phone.startswith("91") else clean_phone
                    
                    match_sender = clean_phone in str(p.sender) or alt_phone in str(p.sender)
                    match_group = False
                    if clean_group_jid:
                        group_name = waha_groups_map.get(clean_group_jid)
                        match_group = (
                            p.group_name
                            and group_name
                            and str(p.group_name).lower() == group_name.lower()
                        )
                        
                    match_name = False
                    if not match_sender and r.person_name and p.sender:
                        import difflib
                        sender_name_part = clean_name_string(p.sender.split(' (')[0])
                        t_names = [clean_name_string(n) for n in r.person_name.split(',')]
                        for t_name in t_names:
                            if len(sender_name_part) >= 3 and len(t_name) >= 3:
                                ratio = difflib.SequenceMatcher(None, sender_name_part, t_name).ratio()
                                if ratio > 0.75 or sender_name_part in t_name or t_name in sender_name_part:
                                    match_name = True
                                    break
                    
                    # Match if sender is the manager (Kusum) satisfying the reminder privately
                    match_waha_sender = False
                    if p.sender:
                        import difflib
                        sender_name_part = clean_name_string(p.sender.split(' (')[0])
                        manager_name = clean_name_string("kusum")
                        ratio = difflib.SequenceMatcher(None, sender_name_part, manager_name).ratio()
                        if ratio > 0.75 or manager_name in sender_name_part or sender_name_part in manager_name:
                            match_waha_sender = True
                                    
                    if match_sender or match_group or match_name or match_waha_sender:
                        processed_today.append(p)

                for p in processed_today:
                    p_cat = (p.category or "").lower()
                    p_notes = (p.notes or "").lower()
                    if is_egg_pricing:
                        time_keyword = "morning" if "morning" in r.report_types.lower() else "afternoon" if "afternoon" in r.report_types.lower() else "evening" if "evening" in r.report_types.lower() else None
                        if time_keyword and time_keyword in p_notes and any(w in p_notes for w in ["egg", "price", "pricing"]):
                            submitted = True
                            break
                    else:
                        if any(kw in p_cat for kw in report_keywords) or any(kw in p_notes for kw in report_keywords):
                            submitted = True
                            break
                        
            if not submitted:
                display_name = f"[{group_name_display}]" if group_name_display else r.person_name
                missed_reports.append(f"- ❌ {display_name} failed to submit report: *{r.report_types}*")
                
        if missed_reports:
            if escalation_lines:
                escalation_lines.append("")
            escalation_lines.append("*[Missed Reports]*")
            escalation_lines.extend(missed_reports)
            
        if escalation_lines:
            msg = "🚨 *Daily Escalation Report (8:00 PM)*\n\nThe following items have not been updated today:\n\n" + "\n".join(escalation_lines)
            send_waha_message(manager_jid, msg)
            logger.info(f"Manager Escalation sent to {manager_jid}")
        else:
            logger.info("Manager Escalation: All tasks and reports for today are completed!")
            
    except Exception as e:
        logger.error(f"Error in manager_escalation_job: {e}")
    finally:
        db.close()


def setup_scheduler():

    global scheduler
    
    # Schedule Health Monitor every 1 minute
    scheduler.add_job(health_monitor_job, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=60)
    
    # Schedule Task Overdue Checker & Nagging alert every 1 minute
    scheduler.add_job(poll_and_remind_tasks_job, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=60)
    
    # Schedule Wednesday meetings checklist generation every Wednesday at 6:00 AM IST
    scheduler.add_job(create_wednesday_meeting_tasks, CronTrigger(day_of_week='wed', hour=6, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule Manager Escalation check every day at 8:00 PM IST (20:00)
    scheduler.add_job(manager_escalation_job, CronTrigger(hour=20, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)

    # Schedule Daily Egg Godown report daily at 9:00 PM IST
    scheduler.add_job(scheduled_godown_report_job, CronTrigger(hour=21, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)

    # Midnight reset: advance trigger_time and reset sent recurring reminders to pending at 00:00 IST
    scheduler.add_job(midnight_reset_job, CronTrigger(hour=0, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)

    # Schedule media/report cleanup daily at 12:05 AM IST
    scheduler.add_job(cleanup_old_files_job, CronTrigger(hour=0, minute=5, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule 6:00 PM data entry reminders everyday
    scheduler.add_job(scheduled_reminder_job, CronTrigger(hour=18, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule group submission audit report daily at 8:00 PM IST
    scheduler.add_job(group_submission_audit_job, CronTrigger(hour=20, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule daily report at 10:00 PM IST everyday
    scheduler.add_job(scheduled_report_job, CronTrigger(hour=22, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule weekly report at 11:00 PM IST on Sunday
    scheduler.add_job(scheduled_weekly_report_job, CronTrigger(day_of_week='sun', hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    # Schedule monthly report at 11:00 PM IST on the 1st day of every month
    scheduler.add_job(scheduled_monthly_report_job, CronTrigger(day='1', hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)

    # Schedule yearly report at 11:00 PM IST on Dec 31
    scheduler.add_job(scheduled_yearly_report_job, CronTrigger(month=12, day=31, hour=23, minute=0, timezone="Asia/Kolkata"), misfire_grace_time=3600)
    
    import os
    if os.getenv("USE_N8N", "false").lower() == "true":
        logger.info("USE_N8N is enabled. Live Alarms, Group Sync, and Unified Reminders are delegated to n8n.")
    else:
        # Schedule live alarms polling every 1 minute
        scheduler.add_job(poll_live_alarms, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
        # Schedule group syncing to live PHP server every 5 minutes
        scheduler.add_job(sync_groups_to_live, CronTrigger(minute="*/5", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
        # Schedule database polling for unified reminders every 1 minute
        scheduler.add_job(poll_and_execute_unified_reminders, CronTrigger(minute="*", timezone="Asia/Kolkata"), misfire_grace_time=300)
        
    scheduler.start()
    logger.info("APScheduler started.")
