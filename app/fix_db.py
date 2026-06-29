from sqlalchemy import text
from db.database import engine

con = engine.connect()

# Fix empty category rows
r = con.execute(text("UPDATE processed_data SET category='unknown' WHERE category='' OR category IS NULL"))
con.commit()
print(f"Fixed {r.rowcount} rows with empty/null category")

# Show today's breakdown
rows = con.execute(text("SELECT category, COUNT(*) as cnt FROM processed_data WHERE DATE(processed_time) = CURDATE() GROUP BY category ORDER BY cnt DESC")).fetchall()
print("Today's category breakdown:")
for x in rows:
    print(f"  {x[0] or '(empty)'}: {x[1]}")

con.close()
