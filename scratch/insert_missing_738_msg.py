import sys

sys.path.append('backend')
from database import get_db_session
from models import RawMessage
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

# Check if message already exists
text_to_insert = """Active Account Balances (Sunfra Farms)
• Petty Cash:₹1,56,501.00
• Undeposited Funds: 0
• SUNFRA FARMS Bank: ₹11,28,661.04
• Sunfra Indian Bank: 0
• SBI TERM LOAN ACCOUNT: ₹-2,21,92,630.77
• SUNFRA FARM OD: ₹-3,50,67,882.90"""

msg_time = datetime(2026, 9, 16, 19, 38, 0)
message_id = "manual_sync_16sep_738pm_farms"

existing = db.query(RawMessage).filter(RawMessage.message_id == message_id).first()
if not existing:
    raw_msg = RawMessage(
        message_id=message_id,
        sender="[Accounts Poultry] mahalakshmi (184791135711366)",
        group_name="Accounts Poultry",
        timestamp=msg_time,
        message_type="text",
        raw_text=text_to_insert,
        full_webhook_json="{}"
    )
    db.add(raw_msg)
    db.commit()
    print("Successfully inserted missing 7:38 PM Accounts Poultry balance message for 16 Sep 2026!")
else:
    print("Message already exists in DB.")

db.close()
