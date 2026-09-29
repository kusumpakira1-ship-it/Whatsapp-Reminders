import sqlite3
import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_reminders.sqlite')
cursor = conn.cursor()

def dump_query(title, query, params=()):
    print(f"\n================ {title} ================")
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print(f"Columns: {cols}")
        print(f"Total rows: {len(rows)}")
        for i, r in enumerate(rows):
            print(f"--- Row {i+1} ---")
            for col, val in zip(cols, r):
                print(f"  {col}: {val}")
    except Exception as e:
        print(f"Error executing query: {e}")

# Check sunfra_papaak_egg_rates
dump_query("sunfra_papaak_egg_rates", "SELECT * FROM sunfra_papaak_egg_rates ORDER BY id DESC LIMIT 20")

# Check sunfra_whatsapp_messages for today or recent
dump_query("sunfra_whatsapp_messages (Recent)", "SELECT * FROM sunfra_whatsapp_messages ORDER BY id DESC LIMIT 20")

# Check sunfra_raw_messages
dump_query("sunfra_raw_messages (Recent)", "SELECT * FROM sunfra_raw_messages ORDER BY id DESC LIMIT 20")

# Check sunfra_waha_events
dump_query("sunfra_waha_events (Recent)", "SELECT * FROM sunfra_waha_events ORDER BY id DESC LIMIT 20")

# Check sunfra_processed_data
dump_query("sunfra_processed_data (Recent)", "SELECT * FROM sunfra_processed_data ORDER BY id DESC LIMIT 20")

# Check sunfra_reminder_logs
dump_query("sunfra_reminder_logs (Recent)", "SELECT * FROM sunfra_reminder_logs ORDER BY id DESC LIMIT 20")

