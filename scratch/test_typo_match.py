import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage

db = SessionLocal()

# Check raw messages in Corporate group on Sept 3
raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp.like('2026-09-03%')).all()
corp_msgs = [m.raw_text for m in raw_msgs if 'corporate' in (m.group_name or '').lower()]

print("Corporate messages sent yesterday (03 Sep 2026):")
for txt in corp_msgs:
    print(" -", repr(txt))

print("\n--- Testing keyword matches for Total Receivables ---")
target_text = "Recievables.pdf"
kw_list = ['total receivables', 'total receivable', 'receivable', 'receivables', 'recevable', 'receivables report', 'receivable report', 'receivables update', 'recevable update', 'due from', 'ar aging', 'ar-aging', 'ar_aging', 'receivable.pdf', 'receivables.pdf', 'receivable pdf', 'receivables pdf']

match = any(kw.lower() in target_text.lower() for kw in kw_list)
print(f"Does '{target_text}' match current kw_list for 'total receivables'? -> {match}")

print("\n--- Testing with 'recievables' (ie typo) included ---")
kw_list_fixed = kw_list + ['recievables', 'recievable', 'recievables.pdf', 'recievable.pdf']
match_fixed = any(kw.lower() in target_text.lower() for kw in kw_list_fixed)
print(f"Does '{target_text}' match fixed kw_list for 'total receivables'? -> {match_fixed}")
