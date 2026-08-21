"""
Search for backup JSON/SQL files of reminders and tasks
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import os
import glob

print("=== SEARCHING FOR BACKUP FILES ===")
files = glob.glob(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\**\*.json', recursive=True)
files += glob.glob(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\**\*.sql', recursive=True)
files += glob.glob(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\**\*.sqlite', recursive=True)

for f in files:
    if 'brain' not in f and 'node_modules' not in f and '.git' not in f:
        print(f"File: {f} | Size: {os.path.getsize(f)} bytes")
