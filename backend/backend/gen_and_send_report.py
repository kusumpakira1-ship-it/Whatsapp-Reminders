import sys, os, base64, requests, datetime
app_dir = '/app' if os.path.exists('/app') else r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend'
sys.path.insert(0, app_dir)
os.chdir(app_dir)
from dotenv import load_dotenv
env_file = os.path.join(app_dir, '.env')
if os.path.exists(env_file): load_dotenv(env_file)

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

# Fetch weekly bird weight measurements (last 7 days lookback) if not reported today
weight_cats = ['hen_weight', 'weight', 'body_weight', 'bird_weight', 'avg_weight']
today_weight_sheds = {d.shead_name for d in data if d.category in weight_cats}
recent_weights = db.query(ProcessedData).filter(
    ProcessedData.category.in_(weight_cats),
    ProcessedData.processed_time >= f"{target_date - timedelta(days=7)} 00:00:00",
    ProcessedData.processed_time <= f"{target_date} 23:59:59"
).order_by(ProcessedData.processed_time.desc()).all()

added_weight_sheds = set()
extra_weight_records = []
for rw in recent_weights:
    if rw.shead_name not in today_weight_sheds and rw.shead_name not in added_weight_sheds:
        extra_weight_records.append(rw)
        added_weight_sheds.add(rw.shead_name)

data = list(data) + extra_weight_records
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
from report_formatter import build_whatsapp_summary
summary_caption = build_whatsapp_summary(df, 'daily', target_date, target_date, birds_map, 5.80, 27500)

payload_ops = {
    'chatId': '917259510983@c.us',
    'file': {
        'mimetype': 'application/pdf',
        'filename': f'Operations_{target_date}.pdf',
        'data': ops_b64
    },
    'caption': summary_caption,
    'session': WAHA_SESSION
}
r1 = requests.post(f'{WAHA_URL}/api/sendFile', json=payload_ops, headers=headers, timeout=30)
print(f'Ops PDF Send Status: {r1.status_code}')

# Financial Report PDF disabled per user directive ("no need to send this report ok na")
# generate_pdf(fin_pdf, df, 'daily', target_date, target_date, birds_map, 5.80, 27500)
# r2 = requests.post(f'{WAHA_URL}/api/sendFile', json=payload_fin, headers=headers, timeout=30)
