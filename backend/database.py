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
    pool_recycle=3600, 
    pool_size=1, 
    max_overflow=0
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

import time
import logging
logger = logging.getLogger(__name__)

def get_db():
    retries = 3
    delay = 2
    for attempt in range(retries):
        try:
            db = SessionLocal()
            # Run a dummy query to verify connection is healthy (pre-ping check)
            db.execute(text("SELECT 1"))
            yield db
            db.close()
            return
        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Database connection failed (attempt {attempt+1}/{retries}): {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"Database connection failed after {retries} attempts: {e}")
                raise

