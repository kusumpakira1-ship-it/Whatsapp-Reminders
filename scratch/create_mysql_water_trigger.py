"""
Create MySQL BEFORE INSERT trigger to block Water Monitoring rows at the Database Engine level
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    print("=== 1. PURGING ALL EXISTING WATER / DEVICE ALERT ROWS ===")
    sql_purge = """
    DELETE FROM sunfra_unified_reminders 
    WHERE LOWER(COALESCE(person_name,'')) LIKE '%water%' 
       OR LOWER(COALESCE(report_types,'')) LIKE '%water%' 
       OR LOWER(COALESCE(task_notes,'')) LIKE '%water%' 
       OR LOWER(COALESCE(task_notes,'')) LIKE '%mac:%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%location:%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%power status%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%alert%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%120363409544891824%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%water%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%lid%'
    """
    purged_count = cursor.execute(sql_purge)
    conn.commit()
    print(f"Purged {purged_count} Water/Device alert rows!")

    print("\n=== 2. CREATING MYSQL BEFORE INSERT TRIGGER ===")
    cursor.execute("DROP TRIGGER IF EXISTS block_water_monitoring_inserts")
    
    trigger_sql = """
    CREATE TRIGGER block_water_monitoring_inserts
    BEFORE INSERT ON sunfra_unified_reminders
    FOR EACH ROW
    BEGIN
        IF LOWER(COALESCE(NEW.person_name,'')) LIKE '%water%'
           OR LOWER(COALESCE(NEW.report_types,'')) LIKE '%water%'
           OR LOWER(COALESCE(NEW.task_notes,'')) LIKE '%water%'
           OR LOWER(COALESCE(NEW.task_notes,'')) LIKE '%mac:%'
           OR LOWER(COALESCE(NEW.task_notes,'')) LIKE '%location:%'
           OR LOWER(COALESCE(NEW.task_notes,'')) LIKE '%power status%'
           OR LOWER(COALESCE(NEW.whatsapp_group_id,'')) LIKE '%120363409544891824%'
           OR LOWER(COALESCE(NEW.whatsapp_group_id,'')) LIKE '%water%'
        THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Water Monitoring and Device Alerts are blocked permanently.';
        END IF;
    END;
    """
    cursor.execute(trigger_sql)
    conn.commit()
    print("Successfully created MySQL Trigger `block_water_monitoring_inserts`! Database engine will now abort any water insert attempt!")

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
