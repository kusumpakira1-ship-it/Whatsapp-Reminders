import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models import CustomAlarm
import logging

logging.basicConfig(level=logging.INFO)
print("Creating CustomAlarm table...")
CustomAlarm.__table__.create(bind=engine, checkfirst=True)
print("Done.")
