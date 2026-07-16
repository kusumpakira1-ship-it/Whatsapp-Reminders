import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import RawMessage, WhatsAppMessage

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
db = sessionmaker(bind=engine)()

print("--- Raw Messages containing 917259510983 ---")
msgs = db.query(RawMessage).filter(RawMessage.sender.like('%917259510983%')).order_by(RawMessage.timestamp.desc()).limit(10).all()
for m in msgs:
    print(f"[{m.timestamp}] {m.sender}: {m.raw_text}")

print("\n--- WhatsApp Group Messages from 917259510983 ---")
msgs2 = db.query(WhatsAppMessage).filter(WhatsAppMessage.sender_id.like('%917259510983%')).order_by(WhatsAppMessage.timestamp.desc()).limit(10).all()
for m in msgs2:
    print(f"[{m.timestamp}] Group: {m.group_id}: {m.message_text}")
