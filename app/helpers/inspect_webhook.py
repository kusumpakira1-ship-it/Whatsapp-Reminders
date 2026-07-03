import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import ProcessedData

db = SessionLocal()
try:
    processed = db.query(ProcessedData).order_by(ProcessedData.id.desc()).limit(5).all()
    print("Last 5 processed messages in database:")
    for p in processed:
        print("-" * 50)
        print(f"ID: {p.id} | MsgID: {p.message_id}")
        print(f"Shead: {p.shead_name} | Category: {p.category}")
        print(f"Quantity: {p.quantity} | Unit: {p.unit} | Amount: {p.amount}")
        print(f"Sender: {p.sender} | GroupName: {p.group_name}")
        print(f"ProcessedTime: {p.processed_time} | CreatedAt: {p.created_at}")
finally:
    db.close()
