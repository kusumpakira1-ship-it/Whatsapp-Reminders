import pymysql
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
db = os.getenv("DB_NAME")

print(f"Connecting to MySQL on {host}...")
connection = pymysql.connect(host=host, user=user, password=password, database=db)

try:
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wa_employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            group_id INT,
            report_responsibility VARCHAR(100),
            whatsapp_group_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wa_alarms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            target_type VARCHAR(50),
            target_id INT,
            whatsapp_target_id VARCHAR(255),
            task_notes TEXT,
            trigger_time DATETIME,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # In case they were created previously without the new whatsapp columns
        try:
            cursor.execute("ALTER TABLE wa_employees ADD COLUMN whatsapp_group_id VARCHAR(255);")
        except Exception:
            pass
            
        try:
            cursor.execute("ALTER TABLE wa_alarms ADD COLUMN whatsapp_target_id VARCHAR(255);")
        except Exception:
            pass
            
    connection.commit()
    print("Tables created and verified successfully!")
finally:
    connection.close()
