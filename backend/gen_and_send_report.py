import sys, os, base64, requests, datetime
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

# Generate using local path directly
from database import SessionLocal
from models import ProcessedData, Flock
import pandas as pd
from datetime import date, timedelta, timezone
from report_formatter import generate_operations_pdf, generate_pdf
import re

IST = timezone(timedelta(hours=5, minutes=30))
target_date = (datetime.datetime.now(IST) - timedelta(days=1)).date()
print(f"Generating reports for {target_date.strftime('%d/%m/%Y')} ({target_date})...")

db = SessionLocal()
data = db.query(ProcessedData).filter(
    ProcessedData.processed_time >= f"{target_date} 00:00:00",
    ProcessedData.processed_time <= f"{target_date} 23:59:59"
).all()
flocks = db.query(Flock).filter(Flock.status == 'active').all()

birds_map = {}
for flock in flocks:
    shed_key = flock.shed_name.strip() if flock.shed_name else ''
    shed_key_lower = shed_key.lower()
    if 'chick' in shed_key_lower:
        normalized = 'Chick'
    elif 'grower' in shed_key_lower:
        normalized = 'Grower'
    else:
        nums = re.findall(r'\d+', shed_key)
        if nums:
            normalized = f"Shed {nums[0]}"
        else:
            normalized = shed_key
    live = getattr(flock, 'live_birds', None) or getattr(flock, 'current_birds', None) or getattr(flock, 'initial_chicks', None) or 0
    birds_map[normalized] = live
db.close()

print(f"Found {len(data)} records for {target_date}")

if data:
    df = pd.DataFrame([{
        'shead_name': d.shead_name or '',
        'category': d.category or 'unknown',
        'quantity': float(d.quantity) if d.quantity else 0,
        'unit': d.unit or '',
        'amount': float(d.amount) if d.amount else 0.0,
        'notes': d.notes or ''
    } for d in data])
else:
    df = pd.DataFrame()

os.makedirs(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\media\reports', exist_ok=True)
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
ops_pdf = fr'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\media\reports\Operations_{target_date}_{ts}.pdf'
fin_pdf = fr'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\media\reports\Financial_{target_date}_{ts}.pdf'

print(f"Generating Ops PDF to: {ops_pdf}")
generate_operations_pdf(ops_pdf, df, 'daily', target_date, target_date, birds_map)
print(f"Generating Fin PDF to: {fin_pdf}")
generate_pdf(fin_pdf, df, 'daily', target_date, target_date, birds_map, 5.80, 27500)

WAHA_URL = os.getenv('WAHA_URL', 'http://localhost:3000')
WAHA_SESSION = os.getenv('WAHA_SESSION', 'default')
WAHA_API_KEY = os.getenv('WAHA_API_KEY', '')
headers = {'X-Api-Key': WAHA_API_KEY, 'Content-Type': 'application/json'}

# Send Ops Report
with open(ops_pdf, 'rb') as f:
    ops_b64 = base64.b64encode(f.read()).decode('utf-8')
payload_ops = {
    'chatId': '917259510983@c.us',
    'file': {
        'mimetype': 'application/pdf',
        'filename': f'Operations_{target_date}.pdf',
        'data': ops_b64
    },
    'caption': f'Farm Operations Report - {target_date.strftime("%d %b %Y")}\nIncludes: Shed-Wise Mortality | Trays Produced | Actual vs Expected Production % | Bird Weight vs Book Standard',
    'session': WAHA_SESSION
}
r1 = requests.post(f'{WAHA_URL}/api/sendFile', json=payload_ops, headers=headers, timeout=30)
print(f'Ops PDF Send Status: {r1.status_code}')

# Send Fin Report
with open(fin_pdf, 'rb') as f:
    fin_b64 = base64.b64encode(f.read()).decode('utf-8')
payload_fin = {
    'chatId': '917259510983@c.us',
    'file': {
        'mimetype': 'application/pdf',
        'filename': f'Financial_{target_date}.pdf',
        'data': fin_b64
    },
    'caption': f'Farm Financial Report - {target_date.strftime("%d %b %Y")}\nIncludes: Production Overview | Feed Consumption | Shed Expenditure | Common Expenses | P&L Summary',
    'session': WAHA_SESSION
}
r2 = requests.post(f'{WAHA_URL}/api/sendFile', json=payload_fin, headers=headers, timeout=30)
print(f'Fin PDF Send Status: {r2.status_code}')
