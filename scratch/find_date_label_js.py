"""
Search JS code in frontend/index.php for reminders-date-label and date filtering.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

idx = html.find('reminders-date-label')
if idx != -1:
    print("Found 'reminders-date-label':")
    print(html[max(0, idx-200):min(len(html), idx+800)])

