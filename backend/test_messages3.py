import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import RawMessage

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
db = sessionmaker(bind=engine)()

msgs = db.query(RawMessage).filter(RawMessage.raw_text.like('%CA%')).order_by(RawMessage.timestamp.desc()).limit(5).all()
with open("ca_output.txt", "w", encoding="utf-8") as f:
    for m in msgs:
        f.write(f"[{m.timestamp}] {m.sender}: {m.raw_text}\n")
