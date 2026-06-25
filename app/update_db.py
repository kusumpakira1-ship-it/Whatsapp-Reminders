import sys
import os
sys.path.append(os.path.abspath("app"))

from sqlalchemy import text
from db.database import engine

def main():
    try:
        with engine.begin() as con:
            con.execute(text("ALTER TABLE processed_data ADD COLUMN group_name VARCHAR(255);"))
            print("Successfully added group_name to processed_data")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
