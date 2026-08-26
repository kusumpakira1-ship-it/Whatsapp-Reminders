import os

php_files = [
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\send_reminder_api.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\trigger_reminder.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\api\trigger_reminder.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\api\send_reminder_api.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\app\static\send_reminder_api.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\app\static\trigger_reminder.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\app\static\index.php',
    r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\send_reminder_api.php',
    r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\Whatsapp_Rem\send_reminder_api.php',
    r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\index.php',
    r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\Whatsapp_Rem\index.php'
]

for p in php_files:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        updated = code.replace(
            "['Content-Type: application/json']",
            "['Content-Type: application/json', 'X-Api-Key: 123']"
        )
        
        if updated != code:
            with open(p, 'w', encoding='utf-8') as f:
                f.write(updated)
            print(f"Updated X-Api-Key header in {p}")
        else:
            print(f"No changes needed or header already present in {p}")
