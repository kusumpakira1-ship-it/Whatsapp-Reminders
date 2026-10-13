import os
import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

db_pass = getattr(settings, "DB_PASS", os.getenv("DB_PASS", "Kusum@2026Bb!"))
encoded_password = urllib.parse.quote_plus(db_pass)
DATABASE_URL = f"mysql+pymysql://{getattr(settings, 'DB_USER', 'u632391467_kusumpakira')}:{encoded_password}@{getattr(settings, 'DB_HOST', '145.223.17.70')}/{getattr(settings, 'DB_NAME', 'u632391467_kusumpakira')}"

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=300, 
    pool_size=5, 
    max_overflow=5,
    connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

import time
import logging
logger = logging.getLogger(__name__)

sqlite_engine = create_engine("sqlite:///whatsapp_reminders.sqlite", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=sqlite_engine)
SqliteSession = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

def get_db():
    db = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        if db:
            try: db.close()
            except Exception: pass
        logger.warning(f"MySQL connection unavailable ({e}). Using SQLite fallback session...")
        try:
            Base.metadata.create_all(bind=sqlite_engine)
            db = SqliteSession()
            yield db
        except Exception as sqle:
            logger.error(f"SQLite fallback failed: {sqle}")
            raise e
    finally:
        if db:
            try: db.close()
            except Exception: pass

def get_db_session():
    """Returns a valid DB session (MySQL if available, or SQLite fallback if MySQL connection limit reached)."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return db
    except Exception as e:
        logger.warning(f"MySQL unavailable ({e}). Using SQLite fallback session...")
        Base.metadata.create_all(bind=sqlite_engine)
        return SqliteSession()



