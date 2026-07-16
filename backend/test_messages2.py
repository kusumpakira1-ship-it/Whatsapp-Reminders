import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import RawMessage, WhatsAppMessage

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
db = sessionmaker(bind=engine)()

with open("test_output3.txt", "w", encoding="utf-8") as f:
    f.write("--- Any messages with 'done' or 'silo' ---\n")
    msgs = db.query(RawMessage).filter(RawMessage.raw_text.like('%done%') | RawMessage.raw_text.like('%silo%')).order_by(RawMessage.timestamp.desc()).limit(10).all()
    for m in msgs:
        f.write(f"[{m.timestamp}] {m.sender}: {m.raw_text}\n")

    f.write("\n--- Group messages ---\n")
    msgs2 = db.query(WhatsAppMessage).filter(WhatsAppMessage.message_text.like('%done%') | WhatsAppMessage.message_text.like('%silo%')).order_by(WhatsAppMessage.timestamp.desc()).limit(10).all()
    for m in msgs2:
        f.write(f"[{m.timestamp}] Group {m.group_id}: {m.message_text}\n")
