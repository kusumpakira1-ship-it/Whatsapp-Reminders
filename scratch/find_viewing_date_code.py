"""
Search frontend/index.php for 'Viewing' or date picker handling.
"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'viewing' in line.lower() or 'back to today' in line.lower() or 'fetchreminders' in line.lower():
        print(f"Line {idx+1}: {line.strip()}")

