import pymysql
import os
import sys
import math
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "145.223.17.70")
DB_NAME = os.getenv("DB_NAME", "u632391467_kusumpakira")
DB_USER = os.getenv("DB_USER", "u632391467_kusumpakira")
DB_PASS = os.getenv("DB_PASS", "Kusum@2026Bb!")

def load_standards():
    read_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "read")
    if not os.path.exists(read_file_path):
        print(f"Error: read file not found at {read_file_path}")
        return

    print("Connecting to database to upload standards...")
    conn = pymysql.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()

    # Clear old standards
    cursor.execute("TRUNCATE TABLE sunfra_book_standards")
    print("Truncated old standards table.")

    print(f"Parsing standards from {read_file_path}...")
    
    current_ep = 0.0
    current_bw = 0
    current_feed = 0

    with open(read_file_path, "r", encoding="utf-8") as f:
        # Skip header
        header = f.readline()
        
        for idx, line in enumerate(f):
            parts = line.strip('\n').split('\t')
            if len(parts) < 2:
                continue
                
            day_str = parts[1].strip()
            if not day_str.isdigit():
                continue
                
            day = int(day_str)
            week = math.ceil(day / 7)
            
            # Parse vaccine/medicine
            vaccine_parts = []
            if len(parts) > 2 and parts[2].strip():
                vaccine_parts.append(parts[2].strip())
            if len(parts) > 4 and parts[4].strip():
                vaccine_parts.append(parts[4].strip())
            vaccine_text = " | ".join(vaccine_parts) if vaccine_parts else None

            # Look up standard values
            # Index 11: eggs As per book
            if len(parts) > 11 and parts[11].strip():
                try:
                    current_ep = float(parts[11].strip())
                except ValueError:
                    pass
            # Index 12: As per book body weight
            if len(parts) > 12 and parts[12].strip():
                try:
                    current_bw = int(float(parts[12].strip()))
                except ValueError:
                    pass
            # Index 13: Feed Consumption
            if len(parts) > 13 and parts[13].strip():
                try:
                    current_feed = int(float(parts[13].strip()))
                except ValueError:
                    pass

            cursor.execute("""
                INSERT INTO sunfra_book_standards (week, day, vaccine, expected_production_pct, expected_body_weight_g, expected_feed_g)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (week, day, vaccine_text, current_ep, current_bw, current_feed))

    conn.commit()
    print("Book standards loaded successfully.")
    conn.close()

if __name__ == "__main__":
    load_standards()
