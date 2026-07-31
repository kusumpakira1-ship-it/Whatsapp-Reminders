import mysql.connector

try:
    conn = mysql.connector.connect(
        host="145.223.17.70",
        user="u632391467_kusumpakira",
        password="Kusum@2026Bb!",
        database="u632391467_kusumpakira",
        connect_timeout=10
    )
    cursor = conn.cursor()
    sql = "UPDATE sunfra_unified_reminders SET status = 'pending' WHERE id = 189 OR whatsapp_group_id LIKE '%120363427856964756%'"
    cursor.execute(sql)
    conn.commit()
    print(f"Hostinger MySQL updated successfully! Affected rows: {cursor.rowcount}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error updating Hostinger MySQL: {e}")
