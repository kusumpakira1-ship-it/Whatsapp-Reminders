import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('backend/scheduler.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's search for all add_job calls or cron triggers or scheduled functions in scheduler.py
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'add_job' in line or 'CronTrigger' in line or 'IntervalTrigger' in line or 'DateTrigger' in line or 'def ' in line:
        print(f"Line {i+1}: {line.strip()}")
