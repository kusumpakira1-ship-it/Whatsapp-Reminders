"""
Find verify_reminder_submission or matching logic in index.php
"""
with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'verify_reminder' in line or 'sub_reports_status' in line:
        print(f"Line {idx+1}: {line.strip()[:150]}")
