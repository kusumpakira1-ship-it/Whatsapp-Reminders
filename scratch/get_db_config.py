"""
Connect to Hostinger MySQL and inspect all tables and recent incoming submissions/reports.
"""
import pymysql, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# Hostinger MySQL Credentials from earlier scripts or database.php
DB_HOST = '193.203.184.162' # or localhost or sunfragroup IP, let's check database.php
DB_USER = 'u632391467_kusum1' # let's check exact user from DB config
DB_PASS = 'h3>R~fQ*z?m'

# Let's read database.php first if available or test connection
try:
    with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\database.php', 'r', encoding='utf-8', errors='ignore') as f:
        print("database.php content:")
        print(f.read())
except Exception as e:
    print("Error reading database.php:", e)

