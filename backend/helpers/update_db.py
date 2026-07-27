import pymysql
import os

# 1. Update MySQL Table
conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cursor = conn.cursor()

# Add live_birds column if not exists
try:
    cursor.execute("ALTER TABLE sunfra_flocks ADD COLUMN live_birds INT DEFAULT NULL AFTER initial_chicks;")
    print("Added live_birds column to sunfra_flocks")
except Exception as e:
    print("Column status:", e)

# Populate live_birds in MySQL
cursor.execute("SELECT id, shed_name, initial_chicks, hatch_date FROM sunfra_flocks")
flocks = cursor.fetchall()

for f in flocks:
    fid, sname, initial, hatch = f
    shed_norm = sname.replace('Shead', 'Shed').strip()
    shed_alt = sname.replace('Shed', 'Shead').strip()
    
    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0) 
        FROM sunfra_processed_data 
        WHERE category = 'mortality' AND (shead_name = %s OR shead_name = %s) AND processed_time >= %s
    """, (shed_norm, shed_alt, hatch))
    mort = float(cursor.fetchone()[0])
    
    if 'chick' in sname.lower():
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM sunfra_processed_data WHERE category = 'mortality' AND shead_name LIKE 'Chick%%' AND processed_time >= %s", (hatch,))
        mort += float(cursor.fetchone()[0])
        
    live = max(0, int(initial - mort))
    cursor.execute("UPDATE sunfra_flocks SET live_birds = %s WHERE id = %s", (live, fid))

conn.commit()
conn.close()
print("Successfully updated live_birds column in MySQL database.")

# 2. Update database.php configuration files
db_php = """<?php
// Hostinger MySQL Connection
$host = '145.223.17.70';
$db   = 'u632391467_kusumpakira';
$user = 'u632391467_kusumpakira';
$pass = 'Kusum@2026Bb!';
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
     $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\\PDOException $e) {
     throw new \\PDOException($e->getMessage(), (int)$e->getCode());
}
"""

paths = [
    r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\database.php',
    r'c:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\database.php',
    r'c:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\Whatsapp_Rem\database.php'
]

for p in paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(db_php)
    print(f"Wrote database.php to {p}")
