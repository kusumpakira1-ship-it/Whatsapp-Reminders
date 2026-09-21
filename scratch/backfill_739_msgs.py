import sys

sys.path.append('backend')
from database import get_db_session
from models import RawMessage
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

messages_to_insert = [
    {
        "message_id": "manual_sync_16sep_737pm_payables",
        "sender": "[Accounts Poultry] mahalakshmi (184791135711366)",
        "group_name": "Accounts Poultry",
        "timestamp": datetime(2026, 9, 16, 19, 37, 0),
        "message_type": "pdf",
        "raw_text": "Payables",
        "media_path": "/app/media/manual_payables_16sep.pdf"
    },
    {
        "message_id": "manual_sync_16sep_738pm_daybook",
        "sender": "[Accounts Poultry] mahalakshmi (184791135711366)",
        "group_name": "Accounts Poultry",
        "timestamp": datetime(2026, 9, 16, 19, 38, 0),
        "message_type": "pdf",
        "raw_text": "Day Book (34).pdf | day Book",
        "media_path": "/app/media/manual_daybook_16sep.pdf"
    },
    {
        "message_id": "manual_sync_16sep_739pm_pending_reports",
        "sender": "[Accounts Poultry] mahalakshmi (184791135711366)",
        "group_name": "Accounts Poultry",
        "timestamp": datetime(2026, 9, 16, 19, 39, 0),
        "message_type": "text",
        "raw_text": """Please submit the following pending reports for today:
• CA Statement Shared
• Daily Purchases 23000 kg
• Daily Sales Sunfra C 1500 trays ;
• Day Book shared
• Total Payables shared
• Total Receivables shared""",
        "media_path": None
    }
]

for msg in messages_to_insert:
    existing = db.query(RawMessage).filter(RawMessage.message_id == msg["message_id"]).first()
    if not existing:
        raw_msg = RawMessage(
            message_id=msg["message_id"],
            sender=msg["sender"],
            group_name=msg["group_name"],
            timestamp=msg["timestamp"],
            message_type=msg["message_type"],
            raw_text=msg["raw_text"],
            media_path=msg["media_path"],
            full_webhook_json="{}"
        )
        db.add(raw_msg)
        print(f"Inserted: {msg['message_id']} ({msg['raw_text'][:30]})")
    else:
        print(f"Already exists: {msg['message_id']}")

db.commit()
db.close()
