import sys, re
sys.path.append('/app')

from database import SessionLocal
from models import ProcessedData
import pandas as pd

db = SessionLocal()
data = db.query(ProcessedData).filter(
    ProcessedData.processed_time >= '2026-07-31 00:00:00',
    ProcessedData.processed_time <= '2026-07-31 23:59:59'
).all()

df = pd.DataFrame([{
    'shead_name': d.shead_name or '',
    'category': d.category or 'unknown',
    'quantity': float(d.quantity) if d.quantity else 0
} for d in data])

def _norm_shead(name):
    n = str(name or '').strip().lower()
    if 'chick' in n: return 'Chick'
    if 'grower' in n: return 'Grower'
    nums = re.findall(r'\d+', n)
    if nums: return f"Shed {nums[0]}"
    return name

df['shead_name'] = df['shead_name'].apply(_norm_shead)
FIXED_SHEDS = ["Shed 1", "Shed 2", "Shed 3", "Shed 4", "Shed 5", "Shed 6", "Shed 7", "Shed 8", "Shed 9", "Grower", "Chick"]

print("=== CALCULATED SHED-WISE MORTALITY FOR 2026-07-31 ===")
tot = 0
for shed in FIXED_SHEDS:
    mort_df = df[(df['shead_name'] == shed) & (df['category'] == 'mortality')]
    m = int(max([float(r['quantity'] or 0) for _, r in mort_df.iterrows()], default=0))
    tot += m
    print(f"{shed:<10}: {m}")
print(f"TOTAL MORTALITY: {tot}")
