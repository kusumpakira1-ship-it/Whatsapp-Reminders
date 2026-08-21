"""
Capture and print all 3 Zoho Reconciliation Report messages without sending to WhatsApp
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

# Mock send_waha_message to capture report_text
captured_messages = []

import waha_service
def mock_send_waha_message(phone, msg):
    captured_messages.append((phone, msg))
    return True

waha_service.send_waha_message = mock_send_waha_message

import zoho_reconciliation
zoho_reconciliation.send_waha_message = mock_send_waha_message

print("Generating 3 Zoho Reconciliation Reports...")
zoho_reconciliation.generate_and_send_zoho_reconciliation_report("917259510983@c.us")
zoho_reconciliation.generate_and_send_sunfra_feeds_reconciliation_report("917259510983@c.us")
zoho_reconciliation.generate_and_send_sunfra_corporate_reconciliation_report("917259510983@c.us")

for idx, (phone, text) in enumerate(captured_messages, 1):
    print(f"\n============================================================")
    print(f"REPORT #{idx}")
    print(f"============================================================")
    print(text)

