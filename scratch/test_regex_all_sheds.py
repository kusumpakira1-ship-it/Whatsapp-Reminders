"""
Test updated regex for parsing all 8 sheds production data.
"""
import re, pymysql, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

sample_text = """
SED_AGE_PRODUCTION-AP-BP
     1._ 55_ 596.20_93%-93%
      2._55_626.3_94%_93%
      3._25_653.22_92%_96%
      4._67_623.2_92%_89%
      5_18_11.18_1.49%
      6_73_594.3_89%_87%
      7_81_573.12_87%_84%
      8_37_683.2_98%_97%
"""

production_data = {}

lines = sample_text.strip().split('\n')
for line in lines:
    p_match = re.search(r'^\s*([1-8])[\._\s]*(\d+)[\._\s]+(\d+)(?:\.(\d+))?', line)
    if p_match:
        snum = p_match.group(1)
        age = int(p_match.group(2))
        trays = int(p_match.group(3))
        loose = int(p_match.group(4)) if p_match.group(4) else 0
        total_eggs = (trays * 30) + loose
        production_data[f"Shead {snum}"] = {
            'trays': trays,
            'loose': loose,
            'total_eggs': total_eggs,
            'age_wks': age
        }

print("=== PARSED PRODUCTION DATA FOR ALL 8 SHEDS ===")
for sname, pinfo in production_data.items():
    print(f"  {sname}: {pinfo['trays']} Trays, {pinfo['loose']} Loose (Total: {pinfo['total_eggs']} eggs, Age: {pinfo['age_wks']} wks)")

conn.close()

