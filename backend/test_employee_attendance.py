from database import SessionLocal
from models import RawMessage, WhatsAppMessage
from datetime import datetime, date

db = SessionLocal()
employees = [
    ('AI & IOT', 'Kusum', '7975209680'),
    ('AI & IOT', 'Poornima', '7204484516'),
    ('AI & IOT', 'Akshay', '9019713446'),
    ('AI & IOT', 'Ramya', '7019063646'),
    ('Sunfra OLX CEE', 'Asif', '6364063475'),
    ('Sunfra OLX CEE', 'Prasanna', '9618803740'),
    ('Sunfra OLX CEE', 'Yashaswini', '9573630573'),
    ('Jataayu', 'Roopa', '8686856459'),
    ('Sunfra Corporate', 'Divya', '9381255565'),
    ('Sunfra Corporate', 'Prajwal', '9036597989'),
    ('Sunfra Mudah', 'Akshay (tester)', '8123466671'),
    ('Sunfra Mudah', 'Bharath', '7989525010'),
    ('Sunfra Mudah', 'Krishna', '9182535260'),
    ('Sunfra Mudah', 'Nisha', '9740828621'),
    ('Sunfra Mudah', 'Ravi Teja', '7981745785'),
    ('Sunfra Mudah', 'Thanuja', '8978331872'),
    ('Sunfra Mudah', 'Aishwarya', '8495004826'),
    ('Sunfra HR Team', 'Parvati', '7995452523'),
    ('Indus', 'Girija', '8618580633'),
    ('Indus', 'Jagadish', '7676711899'),
    ('Sunfra Farms', 'Mahalakshmi', '6364817749'),
    ('Sunfra Feeds', 'Venkat', '8247586860'),
    ('Management Team', 'Balaji', '9493928388'),
    ('Management Team', 'Prathiba', '8951520293'),
    ('Management Team', 'Vamsi', '9677277787'),
    ('Management Team', 'Nikhil', '9010889837'),
    ('Management Team', 'Nani', '7204041105'),
    ('Management Team', 'Prasad', '7204021105'),
]

target_date_str = date.today().strftime('%Y-%m-%d')
print(f"=== CHECKING DATABASE FOR {len(employees)} EMPLOYEES ON {target_date_str} ===\n")

raws = db.query(RawMessage).filter(RawMessage.timestamp >= f'{target_date_str} 00:00:00').all()
w_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= f'{target_date_str} 00:00:00').all()

results = []

for grp, name, phone in employees:
    # Match messages from this employee
    emp_raws = []
    for r in raws:
        s = str(r.sender or '')
        # Check phone match or clean name match
        clean_s = s.lower()
        if phone in s or ('91' + phone) in s or (len(name) >= 4 and name.lower() in clean_s):
            emp_raws.append(r)
            
    # Also check w_msgs
    login_time = None
    logout_time = None
    
    # Sort chronological
    emp_raws.sort(key=lambda x: x.timestamp)
    
    for r in emp_raws:
        txt = (r.raw_text or '').strip().lower()
        # Check login
        if any(txt.startswith(w) or txt == w for w in ['login', 'log in', 'logged in', 'in']):
            if not login_time:
                login_time = r.timestamp
        # Check logout
        if any(txt.startswith(w) or txt == w for w in ['logout', 'log out', 'logged out', 'out']):
            logout_time = r.timestamp

    # Determine status
    if not login_time:
        status = "🔴 Absent"
        status_detail = "No login message"
    elif login_time.hour > 11 or (login_time.hour == 11 and login_time.minute > 0):
        status = "🟡 Half Day (Late Login)"
        status_detail = f"Logged in at {login_time.strftime('%I:%M %p')} (> 11:00 AM)"
    elif not logout_time:
        status = "🟡 Half Day (Missing Logout)"
        status_detail = f"Logged in at {login_time.strftime('%I:%M %p')}, No logout yet"
    else:
        status = "🟢 Present"
        status_detail = f"In: {login_time.strftime('%I:%M %p')} | Out: {logout_time.strftime('%I:%M %p')}"

    results.append({
        'group': grp,
        'name': name,
        'phone': phone,
        'status': status,
        'detail': status_detail,
        'login': login_time.strftime('%I:%M %p') if login_time else None,
        'logout': logout_time.strftime('%I:%M %p') if logout_time else None,
        'total_msgs': len(emp_raws)
    })

# Print summary by group
current_grp = ""
for r in results:
    if r['group'] != current_grp:
        current_grp = r['group']
        print(f"\n🏢 *{current_grp}*")
    print(f"  • {r['name']} ({r['phone']}): {r['status']} ({r['detail']}) [Total Msgs: {r['total_msgs']}]")

db.close()
