import sys
import os
sys.path.append("backend")

from database import get_db_session
from models import RawMessage
from datetime import datetime

db = get_db_session()
try:
    raws = db.query(RawMessage).filter(
        RawMessage.timestamp >= "2026-09-09 00:00:00",
        RawMessage.timestamp <= "2026-09-09 23:59:59"
    ).all()

    print(f"Total raw messages on 2026-09-09: {len(raws)}")

    print("\n--- MESSAGES FROM THANUJA (or aliases / phone 8978331872) ---")
    for r in raws:
        s = str(r.sender or "").lower()
        txt = str(r.raw_text or "").lower()
        if "thanuja" in s or "8978331872" in s or "thanuja" in txt:
            print(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}")

    print("\n--- MESSAGES FROM KUSUM (or aliases / phone 7975209680 / LID 183300681367688) ---")
    for r in raws:
        s = str(r.sender or "").lower()
        txt = str(r.raw_text or "").lower()
        if "kusum" in s or "7975209680" in s or "183300681367688" in s or "kusum" in txt:
            print(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}")

    print("\n--- ALL MESSAGES CONTAINING 'LOGOUT' or 'SIGN OUT' or 'SIGNING OFF' or 'LEAVE' or 'HALF DAY' ---")
    for r in raws:
        txt = str(r.raw_text or "").lower()
        if any(k in txt for k in ["logout", "log out", "sign out", "signing off", "signed off", "leave", "half day", "half-day"]):
            print(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}")

finally:
    db.close()
