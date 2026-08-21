import sys
sys.path.append('/app')
from waha_service import send_waha_message

group_jid = '120363111757096162@g.us'
msg = '⚠️ *Task Overdue Alert*\n\nHi Team,\nThe task *"Silo Empty and Cleaning"* is overdue.\n\nPlease complete this work and reply with *"done"* or *"completed"* once finished.'

print(f"Sending test overdue alert to group {group_jid}...")
res = send_waha_message(group_jid, msg)
print("WAHA response:", res)
