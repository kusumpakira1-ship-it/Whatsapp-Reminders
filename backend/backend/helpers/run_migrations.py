import pymysql
import os
import sys

# Load environment variables if run directly
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "145.223.17.70")
DB_NAME = os.getenv("DB_NAME", "u632391467_kusumpakira")
DB_USER = os.getenv("DB_USER", "u632391467_kusumpakira")
DB_PASS = os.getenv("DB_PASS", "Kusum@2026Bb!")

def run_migrations():
    print("Connecting to remote database to run migrations...")
    conn = pymysql.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()

    # 1. Run schema_update.sql
    sql_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "sql", "schema_update.sql")
    if os.path.exists(sql_file_path):
        print(f"Reading migration file from {sql_file_path}...")
        with open(sql_file_path, "r", encoding="utf-8") as f:
            statements = f.read().split(";")
            for statement in statements:
                stmt_clean = statement.strip()
                if stmt_clean:
                    cursor.execute(stmt_clean)
        print("Schema update statements executed successfully.")
    else:
        print(f"Error: Migration file not found at {sql_file_path}")
        conn.close()
        return

    # 2. Seed Flock configuration
    print("Seeding initial flock data...")
    initial_flocks = [
        ("Chick 1", "2026-07-04", 27800, "22"),
        ("Grower 1", "2026-07-04", 27800, None),
        ("Shead 1", "2025-07-25", 19000, "17"),
        ("Shead 2", "2025-07-25", 24000, "18"),
        ("Shead 3", "2026-02-12", 22800, "20"),
        ("Shead 4", "2025-05-10", 22500, "16"),
        ("Shead 5", "2026-04-13", 23000, "21"),
        ("Shead 6", "2025-03-12", 22000, "15"),
        ("Shead 7", "2025-01-25", 22000, "14"),
        ("Shead 8", "2025-12-01", 23500, "19"),
        ("Shead 9", "2025-12-01", 23500, None)
    ]

    for name, hatch_date, initial_chicks, batch_id in initial_flocks:
        cursor.execute("""
            INSERT INTO sunfra_flocks (shed_name, hatch_date, initial_chicks, batch_id, status)
            VALUES (%s, %s, %s, %s, 'active')
            ON DUPLICATE KEY UPDATE
                hatch_date = VALUES(hatch_date),
                initial_chicks = VALUES(initial_chicks),
                batch_id = VALUES(batch_id)
        """, (name, hatch_date, initial_chicks, batch_id))
    
    conn.commit()
    print("Flock configuration seeded successfully.")
    conn.close()

if __name__ == "__main__":
    # Add parent paths to import config properly
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    run_migrations()
