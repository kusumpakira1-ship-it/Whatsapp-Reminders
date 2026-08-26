from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
import urllib.parse

# URL-encode the password to handle special characters like '@'
encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=180, 
    pool_size=2, 
    max_overflow=0
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

import time
import logging
logger = logging.getLogger(__name__)

def get_db():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.warning(f"MySQL connection issue ({e}). Trying SQLite fallback...")
        try:
            sqlite_engine = create_engine("sqlite:///whatsapp_reminders.sqlite")
            SqliteSession = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
            db = SqliteSession()
            yield db
        except Exception as sqle:
            logger.error(f"SQLite fallback failed: {sqle}")
            raise e
    finally:
        try:
            db.close()
        except Exception:
            pass


