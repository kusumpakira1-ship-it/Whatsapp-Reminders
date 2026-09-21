import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scheduler import scheduled_4company_consolidated_reports_job, scheduled_egg_production_crosscheck_650pm_job

print("=== TRIGGERING 6:50 PM SCHEDULED REPORTS NOW ===")

print("\n1. Triggering 4-Company Consolidated Reports...")
scheduled_4company_consolidated_reports_job()

print("\n2. Triggering Egg Production vs Godown Stock Crosscheck...")
scheduled_egg_production_crosscheck_650pm_job()

print("\nDone executing 6:50 PM scheduled reports.")
