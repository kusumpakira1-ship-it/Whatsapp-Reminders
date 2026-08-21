"""
Inspect index.php for syntax issue
"""
import sys

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in index.php: {len(lines)}")
for idx in range(1080, 1185):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx]}", end="")
