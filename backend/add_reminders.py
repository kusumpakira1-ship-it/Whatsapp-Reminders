import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.append('/app')
from database import SessionLocal
from models import UnifiedReminder, Group, RawMessage

db = SessionLocal()

def get_or_create_group(name):
    g = db.query(Group).filter(Group.name == name).first()
    if not g:
        rm = db.query(RawMessage).filter(RawMessage.group_name == name).order_by(RawMessage.timestamp.desc()).first()
        jid = f"group_{name.lower().replace(' ', '_')}"
        g = Group(name=name, whatsapp_group_id=jid)
        db.add(g)
        db.commit()
        db.refresh(g)
    return g

g_corp = get_or_create_group('Sunfra Corporate P&L')
g_pnl = get_or_create_group('Sunfra P&L')
g_hyper = get_or_create_group('Sunfra Hyperscale')

def add_reminder_if_missing(person, phone, group_id, report_type, time_str):
    existing = db.query(UnifiedReminder).filter(
        UnifiedReminder.whatsapp_group_id == group_id,
        UnifiedReminder.report_types == report_type
    ).first()
    if not existing:
        r = UnifiedReminder(
            person_name=person,
            person_phone=phone,
            whatsapp_group_id=group_id,
            report_types=report_type,
            trigger_time=datetime.strptime(f'2026-07-21 {time_str}', '%Y-%m-%d %H:%M:%S'),
            status='pending'
        )
        db.add(r)
        db.commit()
        print(f"Added new reminder for '{report_type}' (Group JID: {group_id})")
    else:
        print(f"Reminder already exists for '{report_type}'")

add_reminder_if_missing('Team', '1234567890', g_corp.whatsapp_group_id, 'Corporate P&L Update', '18:00:00')
add_reminder_if_missing('Team', '1234567890', g_pnl.whatsapp_group_id, 'Sunfra P&L Update', '18:00:00')
add_reminder_if_missing('Team', '1234567890', g_hyper.whatsapp_group_id, 'Sunfra Hyperscale Update', '18:00:00')
