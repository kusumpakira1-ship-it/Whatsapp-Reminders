import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from egg_production_crosscheck import generate_egg_production_crosscheck_report

report = generate_egg_production_crosscheck_report()
print("=== EGG PRODUCTION CROSS-CHECK REPORT TEST ===")
print(report)
