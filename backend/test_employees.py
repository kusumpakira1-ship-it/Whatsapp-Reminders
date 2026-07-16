import urllib.parse
from sqlalchemy import create_engine
from config import settings
import textwrap

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")

with engine.connect() as con:
    rs = con.execute("SELECT name, phone_number FROM sunfra_employees")
    for row in rs:
        print(row)
