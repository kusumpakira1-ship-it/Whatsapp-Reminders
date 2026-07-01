from db.database import engine, Base
from db.models import SystemSetting
import logging

logging.basicConfig(level=logging.INFO)
print("Creating SystemSetting table...")
SystemSetting.__table__.create(bind=engine, checkfirst=True)
print("Done.")
