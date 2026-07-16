import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import UnifiedReminder

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
db = sessionmaker(bind=engine)()

rems = db.query(UnifiedReminder).order_by(UnifiedReminder.id.desc()).all()
for r in rems:
    print(f"[{r.id}] Reports: '{r.report_types}', Notes: '{r.task_notes}' - Status: {r.status} - Due: {r.trigger_time} - Repeat: {r.repeat_interval}")
