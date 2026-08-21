"""
Compare root index.php vs frontend/index.php.
"""
import sys, difflib
sys.stdout.reconfigure(encoding='utf-8')

f1 = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'
f2 = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

with open(f1, 'r', encoding='utf-8', errors='ignore') as fp1:
    lines1 = fp1.readlines()

with open(f2, 'r', encoding='utf-8', errors='ignore') as fp2:
    lines2 = fp2.readlines()

print(f"root index.php line count: {len(lines1)}")
print(f"frontend/index.php line count: {len(lines2)}")

diff = list(difflib.unified_diff(lines1, lines2, fromfile='root/index.php', tofile='frontend/index.php'))
print(f"\nTotal diff lines: {len(diff)}")
if len(diff) > 0:
    print("Diff snippet (first 30 lines):")
    for d in diff[:30]:
        print(d.rstrip())

