import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Group

engine = create_engine(f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")
Session = sessionmaker(bind=engine)
session = Session()

group = session.query(Group).filter_by(name='Ai_developers_sunfra').first()
if group:
    group.whatsapp_group_id = '120363427726701686@g.us'
    session.commit()
    print("Database updated!")
else:
    print("Group not found!")
