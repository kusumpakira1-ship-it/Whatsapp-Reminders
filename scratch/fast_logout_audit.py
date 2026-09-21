import sys, requests, json
from datetime import datetime
sys.path.insert(0, 'backend')
from database import SqliteSession
from models import RawMessage
from attendance_tracker import COMMUNITY_EMPLOYEES, evaluate_attendance_for_date

db = SqliteSession()

groups = [
    ('AI & IOT', ['120363429469512014@g.us']),
    ('Sunfra OLX CEE', ['120363428895707621@g.us']),
    ('Jataayu', ['120363428872126006@g.us', '120363428881117777@g.us', '120363422729608263@g.us']),
    ('Sunfra Corporate', ['120363428349268084@g.us', '120363427470582988@g.us', '120363426659667927@g.us']),
    ('Sunfra Mudah', ['120363410545216320@g.us']),
    ('Sunfra HR Team', ['120363431222906850@g.us']),
    ('Indus', ['120363431080782528@g.us']),
    ('Sunfra Farms', ['120363429481469212@g.us', '120363221285198390@g.us', '120363221211615047@g.us']),
    ('Sunfra Feeds', ['120363413108636132@g.us', '120363412616266332@g.us', '120363410508859526@g.us']),
    ('Management Team', ['120363410684018393@g.us', '120363406924564250@g.us']),
    ('Tendered', ['120363411380848761@g.us'])
]

today_str = '2026-09-17'

# Quick fetch WAHA messages with short timeout
for grp_name, jids in groups:
    for jid in jids:
        try:
            resp = requests.get(f'http://localhost:3000/api/default/chats/{jid}/messages?limit=100', headers={'X-Api-Key': '123'}, timeout=2)
            if resp.status_code == 200:
                for m in resp.json():
                    ts = m.get('timestamp')
                    dt_obj = datetime.fromtimestamp(ts)
                    if dt_obj.strftime('%Y-%m-%d').startswith(today_str):
                        part = m.get('participant') or m.get('author') or m.get('_data', {}).get('author') or m.get('_data', {}).get('key', {}).get('participant') or m.get('from') or ''
                        body = m.get('body') or ''
                        msg_id = m.get('id', {}).get('_serialized') if isinstance(m.get('id'), dict) else (m.get('id') or f'waha_{int(ts)}_{part}')
                        
                        ex = db.query(RawMessage).filter(RawMessage.sender == str(part), RawMessage.raw_text == body, RawMessage.timestamp == dt_obj).first()
                        if not ex:
                            db.add(RawMessage(message_id=str(msg_id), sender=str(part), group_name=str(jid), message_type='chat', raw_text=body, timestamp=dt_obj, full_webhook_json=json.dumps(m)))
        except Exception:
            pass

db.commit()

data = evaluate_attendance_for_date(today_str)

print("\n" + "="*80)
print(f"STRICT GROUP-SCOPED LOGOUT AUDIT FOR ALL 31 EMPLOYEES ({today_str}):")
print("="*80 + "\n")

for grp in data['groups']:
    gname = grp['group_name']
    print(f"🏢 *{gname}*")
    for emp in grp['employees']:
        ename = emp['name']
        ltime = emp['login_time']
        otime = emp['logout_time']
        badge = emp['status_badge']
        detail = emp['detail']
        print(f"  • {ename:<12} | Login: {ltime:<10} | Logout: {otime:<10} | Status: {badge:<32} | {detail}")
    print("-" * 80)
