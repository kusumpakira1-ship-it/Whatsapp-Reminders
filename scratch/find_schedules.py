import re

with open('backend/scheduler.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find all function definitions or schedule definitions or times in scheduler.py
lines = content.split('\n')
for i, line in enumerate(lines):
    if any(k in line.lower() for k in ['cron', 'schedule', 'trigger', 'at ', 'time', '20:', '21:', '22:', '23:', '8pm', '8 pm', '9pm', '10pm', '11pm', 'night']):
        if len(line.strip()) < 120 and not line.strip().startswith('#'):
            print(f"Line {i+1}: {line.strip()}")
