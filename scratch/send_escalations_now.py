import sys
import os

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

print("==================================================")
print("DISPATCHING ESCALATION REPORTS NOW TO 7259510983")
print("==================================================")

target_phone = "917259510983@c.us"

# 1. Manager Escalation Job
print("\n[1/2] Executing Manager Escalation Job...")
try:
    from scheduler import manager_escalation_job
    manager_escalation_job()
    print("  ✅ Manager Escalation Job executed!")
except Exception as e:
    print(f"  ❌ Error executing Manager Escalation Job: {e}")

# 2. Company-Wise Escalation Job
print("\n[2/2] Executing Company-Wise Escalation Job...")
try:
    from scheduler import company_wise_escalation_job
    company_wise_escalation_job()
    print("  ✅ Company-Wise Escalation Job executed!")
except Exception as e:
    print(f"  ❌ Error executing Company-Wise Escalation Job: {e}")

print("\n==================================================")
print("ESCALATION REPORTS DISPATCH COMPLETED!")
print("==================================================")
