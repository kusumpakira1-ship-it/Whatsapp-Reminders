from db.database import engine, Base
from db.models import CustomAlarm
import logging

logging.basicConfig(level=logging.INFO)
print("Creating CustomAlarm table...")
CustomAlarm.__table__.create(bind=engine, checkfirst=True)
print("Done.")
