"""
Sync old folder c:\\Users\\sunfra\\Desktop\\Whatsapp Reminders\\frontend\\index.php
"""
import shutil, os, sys
sys.stdout.reconfigure(encoding='utf-8')

src = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
dest_folder = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\frontend'

if os.path.exists(dest_folder):
    dest = os.path.join(dest_folder, 'index.php')
    shutil.copy2(src, dest)
    print("✅ Synced old folder index.php as well!")
else:
    print("Old folder not found, skipped.")

