import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models import SystemSetting
import logging

logging.basicConfig(level=logging.INFO)
print("Creating SystemSetting table...")
SystemSetting.__table__.create(bind=engine, checkfirst=True)
print("Done.")
