import sys, os, datetime
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

from database import SessionLocal
from models import RawMessage, ProcessedData, Group, WhatsAppMessage

sys.stdout.reconfigure(encoding='utf-8')

db = SessionLocal()

# Target date: 27th July 2026
target_date = datetime.date(2026, 7, 27)
start_dt = datetime.datetime(2026, 7, 27, 0, 0, 0)
end_dt = datetime.datetime(2026, 7, 27, 23, 59, 59)

# Group JIDs
groups = {
    "Sunfra Hyperscale": ["120363428417403024@g.us", "group_sunfra_hyperscale"],
    "Sunfra P&L": ["120363427856964756@g.us", "group_sunfra_p&l"]
}

print(f"Checking submissions for {target_date}...")

for g_name, jids in groups.items():
    print(f"\n=================== {g_name} ===================")
    
    # 1. Look for raw messages matching this group (via sender/group_name or via WhatsAppMessage linkage)
    # Let's find WhatsAppMessage entries for this group
    wa_msgs = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.group_id.in_(jids),
        WhatsAppMessage.timestamp >= start_dt,
        WhatsAppMessage.timestamp <= end_dt
    ).all()
    
    wa_msg_ids = [m.message_id for m in wa_msgs]
    
    # Find matching RawMessage
    raw_msgs = db.query(RawMessage).filter(
        (RawMessage.message_id.in_(wa_msg_ids)) | 
        (RawMessage.group_name.ilike(f"%{g_name.split()[1]}%"))
    ).filter(
        RawMessage.timestamp >= start_dt,
        RawMessage.timestamp <= end_dt
    ).order_by(RawMessage.timestamp).all()
    
    print(f"Found {len(raw_msgs)} Raw Messages:")
    for r in raw_msgs:
        print(f"  [{r.timestamp.strftime('%H:%M:%S')}] Sender: {r.sender} | Group: {r.group_name}")
        # Print a snippet of the text
        txt = r.raw_text or ""
        snippet = (txt[:150] + "...") if len(txt) > 150 else txt
        print(f"    Text: {snippet}")
        print("-" * 50)
        
    # 2. Look for ProcessedData entries matching this group
    # Usually ProcessedData matches via sender phone / name
    # Let's check any ProcessedData created on this date
    processed = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{target_date} 00:00:00",
        ProcessedData.processed_time <= f"{target_date} 23:59:59"
    ).all()
    
    # Let's filter processed data by sender/group matching
    print(f"Processed report records matching {g_name} keywords:")
    match_count = 0
    for p in processed:
        # Check if the message_id is linked to the group
        msg_link = db.query(WhatsAppMessage).filter(WhatsAppMessage.message_id == p.message_id).first()
        is_group_match = msg_link and msg_link.group_id in jids
        
        # Or if group name contains the company word
        is_name_match = p.group_name and any(word.lower() in p.group_name.lower() for word in g_name.split())
        
        if is_group_match or is_name_match:
            match_count += 1
            print(f"  Category: {p.category} | Quantity: {p.quantity} {p.unit} | Sender: {p.sender} | Time: {p.processed_time}")
            print(f"    Notes: {p.notes}")
            print("-" * 50)
    if match_count == 0:
        print("  No processed data entries found.")

db.close()
