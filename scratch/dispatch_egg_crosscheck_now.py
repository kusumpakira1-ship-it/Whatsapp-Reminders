import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from egg_production_crosscheck import generate_and_send_egg_production_crosscheck_report

print("=== DISPATCHING EGG PRODUCTION CROSS-CHECK REPORT NOW ===")
res = generate_and_send_egg_production_crosscheck_report("917259510983@c.us")
print("Dispatch result:", res)
