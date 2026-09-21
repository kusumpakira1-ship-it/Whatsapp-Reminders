import sys

sys.path.append('backend')
from database import SessionLocal
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = SessionLocal()

print("================ SEARCHING ALL RAW MESSAGES TODAY FOR ANY LOGIN/MORNING PATTERN ================")

query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-17 00:00:00'
    ORDER BY timestamp ASC
""")

rows = db.execute(query).fetchall()

login_kws = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "sign in", "signing in", "signed in", "morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]

for r in rows:
    sender = r[2] or ""
    grp = r[1] or ""
    text_str = r[3] or ""
    
    t_clean = text_str.strip().lower()
    
    # Check if message contains login keyword
    if any(kw == t_clean or t_clean.startswith(kw + " ") or t_clean.endswith(" " + kw) or kw in t_clean for kw in login_kws):
        print(f"[{r[4]}] Group: [{grp}] | Sender: {sender} | Text: '{text_str}'")

db.close()
