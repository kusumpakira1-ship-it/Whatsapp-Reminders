"""
DB Migration Script — Expand category ENUM in processed_data table.
Run this once after updating models.py:
    docker exec fastapi_backend python update_db.py
"""
import sys
import os
sys.path.append(os.path.abspath("app"))

from sqlalchemy import text
from db.database import engine


NEW_ENUM = (
    "'egg_collection_1','egg_collection_2','egg_collection',"
    "'hen_weight','mortality','egg_loaded','egg_unloaded','production',"
    "'sales','feed','raw_material','medicine','expense','purchase','egg','unknown'"
)


def main():
    print("Starting DB migration: expanding category ENUM...")
    with engine.begin() as con:
        try:
            # Modify the ENUM column to include all new values
            sql = text(f"""
                ALTER TABLE php_processed_data
                MODIFY COLUMN category ENUM({NEW_ENUM}) NOT NULL DEFAULT 'unknown';
            """)
            con.execute(sql)
            print("✅ Successfully expanded category ENUM in php_processed_data table.")
        except Exception as e:
            print(f"❌ Error modifying ENUM: {e}")

        try:
            # Add group_name column if it doesn't exist yet
            con.execute(text(
                "ALTER TABLE php_processed_data ADD COLUMN IF NOT EXISTS group_name VARCHAR(255);"
            ))
            print("✅ group_name column ensured.")
        except Exception as e:
            print(f"ℹ️  group_name: {e}")


if __name__ == "__main__":
    main()
