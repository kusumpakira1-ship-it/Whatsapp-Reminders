import sys
sys.path.append('/app')

from database import engine, SessionLocal
from sqlalchemy import text
from models import Flock

# 1. Update Hostinger MySQL via engine
with engine.connect() as conn:
    # Set Grower 1 live_birds = 0, status = 'inactive', batch_id = NULL
    conn.execute(text("UPDATE sunfra_flocks SET live_birds = 0, status = 'inactive', batch_id = NULL WHERE shed_name = 'Grower 1'"))
    
    # Set Shead 9 live_birds = 0, status = 'inactive', batch_id = NULL
    conn.execute(text("UPDATE sunfra_flocks SET live_birds = 0, status = 'inactive', batch_id = NULL WHERE shed_name = 'Shead 9'"))
    
    conn.commit()
    print("Hostinger MySQL updated Grower 1 to inactive / 0 live birds successfully!")

# 2. Verify all flock rows
db = SessionLocal()
flocks = db.query(Flock).all()
print("\n=== UPDATED FLOCK DATA ===")
for f in flocks:
    live = f.live_birds if f.live_birds is not None else f.initial_chicks
    print(f"ID: {f.id:<2} | Shed: {f.shed_name:<10} | Status: {f.status:<8} | Live: {live:<6} | Batch: {f.batch_id}")

db.close()
