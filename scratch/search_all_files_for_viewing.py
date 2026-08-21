"""
Search ALL files in workspace for 'Viewing:' or 'Back to Today'.
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

root_dir = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders'
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(('.php', '.html', '.js')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'viewing' in content.lower() or 'back to today' in content.lower():
                        print(f"FOUND IN: {filepath}")
            except Exception as e:
                pass

