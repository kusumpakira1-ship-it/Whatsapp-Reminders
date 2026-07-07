from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import urllib.parse

# URL-encode the password to handle special characters like '@'
encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=1800, 
    pool_size=2, 
    max_overflow=1
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
