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
    pool_recycle=1800,  # 30 minutes connection reuse to minimize Hostinger connection handshakes
    pool_size=3,        # Tight pool size to keep connections far below the 500/hr limit
    max_overflow=2,
    connect_args={"connect_timeout": 10}
)
_RawSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

import time
import logging
logger = logging.getLogger(__name__)

sqlite_path = os.path.join(os.path.dirname(__file__), "whatsapp_reminders.sqlite")
if not os.path.exists(sqlite_path) and os.path.exists("whatsapp_reminders.sqlite"):
    sqlite_path = "whatsapp_reminders.sqlite"
sqlite_engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=sqlite_engine)
SqliteSession = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

_mysql_cooldown_until = 0

def _is_mysql_in_cooldown() -> bool:
    global _mysql_cooldown_until
    return time.time() < _mysql_cooldown_until

def _set_mysql_cooldown(seconds: int = 1200):
    global _mysql_cooldown_until
    _mysql_cooldown_until = time.time() + seconds
    logger.warning(f"Hostinger MySQL circuit breaker active: using SQLite fallback for {seconds//60} minutes to allow hourly connection quota to reset.")

def get_db():
    if _is_mysql_in_cooldown():
        db = SqliteSession()
        try:
            yield db
        finally:
            try: db.close()
            except Exception: pass
        return

    db = None
    try:
        db = _RawSessionLocal()
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        if db:
            try: db.close()
            except Exception: pass
        err_str = str(e)
        if "1226" in err_str or "max_connections_per_hour" in err_str:
            _set_mysql_cooldown(1200) # 20 minutes cooldown to allow Hostinger quota to reset cleanly
        elif "2003" in err_str or "2013" in err_str or "Can't connect" in err_str or "Lost connection" in err_str:
            _set_mysql_cooldown(180) # 3 minutes cooldown
        else:
            _set_mysql_cooldown(60)
        logger.warning(f"MySQL unavailable ({e}). Switched to SQLite fallback session...")
        db = SqliteSession()
        try:
            yield db
        finally:
            try: db.close()
            except Exception: pass
    finally:
        if db:
            try: db.close()
            except Exception: pass

def get_db_session():
    """Returns a valid DB session (MySQL if available, or SQLite fallback with circuit breaker)."""
    if _is_mysql_in_cooldown():
        return SqliteSession()

    try:
        db = _RawSessionLocal()
        db.execute(text("SELECT 1"))
        return db
    except Exception as e:
        err_str = str(e)
        if "1226" in err_str or "max_connections_per_hour" in err_str:
            _set_mysql_cooldown(1200) # 20 minutes cooldown
        elif "2003" in err_str or "2013" in err_str or "Can't connect" in err_str or "Lost connection" in err_str:
            _set_mysql_cooldown(180)
        else:
            _set_mysql_cooldown(60)
        logger.warning(f"MySQL unavailable ({e}). Switched to SQLite fallback session...")
        return SqliteSession()

class SmartSessionFactory:
    """Smart session factory that replaces SessionLocal() everywhere with automatic circuit breaker and SQLite fallback."""
    def __call__(self, *args, **kwargs):
        return get_db_session()

SessionLocal = SmartSessionFactory()




