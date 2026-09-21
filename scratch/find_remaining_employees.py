import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

employees_to_check = [
    ("Kusum", "7975209680", ["kusum", "kusumpakira", "7975209680", "183300681367688"]),
    ("Poornima", "7204484516", ["poornima", "poorna", "207627359363311", "92282304913416", "7204484516"]),
    ("Akshay (AI & IOT)", "9019713446", ["akshay i h", "206686828683301", "9019713446"]),
    ("Yashaswini", "9573630573", ["yashaswini", "124798881513608", "9573630573"]),
    ("Bharath", "7989525010", ["bharath", "g r bharath", "166683486466210", "7989525010"]),
    ("Krishna", "9182535260", ["krishna", "chaitanya bandaru", "96074157031436", "9182535260"]),
    ("Prasad", "7204021105", ["prasad", "vara prasad", "123622194712585", "7204021105"]),
    ("Ganga", "213795016290432", ["ganga", "213795016290432"]),
    ("Jagadish", "7676711899", ["jagadish", "7676711899"]),
    ("Prajwal", "9036597989", ["prajwal", "68195624992799", "9036597989"])
]

print("================ SEARCHING ALL TODAY'S MESSAGES FOR REMAINING EMPLOYEES ================")

query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-17 00:00:00'
    ORDER BY timestamp ASC
""")

rows = db.execute(query).fetchall()
print(f"Total raw messages on 17 Sep 2026: {len(rows)}\n")

for emp_name, phone, aliases in employees_to_check:
    print(f"\n--- Checking '{emp_name}' (Phone: {phone}, Aliases: {aliases}) ---")
    matched = []
    for r in rows:
        m_id, grp, sender, text_c, ts = r
        s_low = (sender or "").lower()
        g_low = (grp or "").lower()
        
        # Check if phone or alias is in sender string OR text string
        if phone in s_low or any(al in s_low for al in aliases) or any(al in text_c.lower() for al in aliases if len(al) > 3):
            matched.append((ts, grp, sender, text_c))
            
    if matched:
        print(f"  FOUND {len(matched)} messages for {emp_name}:")
        for ts, grp, sender, text_c in matched:
            clean = (text_c or "").replace('\n', ' | ')
            print(f"    [{ts}] Group: [{grp}] | Sender: {sender} | Text: '{clean}'")
    else:
        print(f"  NO messages found for {emp_name} today.")

db.close()
