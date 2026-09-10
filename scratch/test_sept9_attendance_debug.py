import sys
import os
sys.path.append("backend")

from database import SessionLocal
from models import RawMessage
from attendance_tracker import COMMUNITY_EMPLOYEES, evaluate_attendance_for_date
from datetime import datetime

db = SessionLocal()
try:
    raws = db.query(RawMessage).filter(
        RawMessage.timestamp >= "2026-09-09 00:00:00",
        RawMessage.timestamp <= "2026-09-09 23:59:59"
    ).all()
    print(f"Total RawMessages in DB for 2026-09-09: {len(raws)}")

    # Let's inspect matched messages for Kusum
    kusum_emp = None
    for grp in COMMUNITY_EMPLOYEES:
        for e in grp["employees"]:
            if e["name"] == "Kusum":
                kusum_emp = e
                break

    print("\nKusum config:", kusum_emp)
    kusum_matched = []
    for r in raws:
        s_str = str(r.sender or "").lower()
        txt = str(r.raw_text or "").lower()
        if "7975209680" in s_str or "183300681367688" in s_str or "kusum" in s_str:
            kusum_matched.append(r)
            print(f"  Matched Kusum raw: [{r.timestamp}] sender={r.sender} group={r.group_name} text={repr(r.raw_text)}")

    print("\nRunning evaluate_attendance_for_date('2026-09-09')...")
    res = evaluate_attendance_for_date("2026-09-09")
    for g in res["groups"]:
        for e in g["employees"]:
            if e["name"] in ["Kusum", "Thanuja"]:
                print(f"Result for {g['group_name']} - {e['name']}: badge={e['status_badge']} | detail={e['detail']} | login={e['login_time']} | logout={e['logout_time']}")

finally:
    db.close()
