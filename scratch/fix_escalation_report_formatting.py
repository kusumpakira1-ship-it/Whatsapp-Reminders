"""
Fix company categorization in generate_escalation_report.py
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\generate_escalation_report.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace get_company_category implementation
old_func = """def get_company_category(display_name: str) -> str:
    name_lower = display_name.lower()
    if "jataayu" in name_lower:
        return "Jataayu Jewellers"
    elif "p&l" in name_lower or "p & l" in name_lower or "corporate" in name_lower or "hyperscale" in name_lower:
        return "Corporate Company (P&L)"
    elif "feed" in name_lower or "raw material" in name_lower or "vendor" in name_lower or "ordering" in name_lower:
        return "Sunfra Feeds"
    else:
        return "Sunfra Farms\""""

new_func = """def get_company_category(display_name: str) -> str:
    name_lower = (display_name or '').lower()
    if "jataayu" in name_lower:
        return "Jataayu Jewellers"
    elif "p&l" in name_lower or "p & l" in name_lower or "corporate" in name_lower or "hyperscale" in name_lower:
        return "Corporate Company (P&L)"
    elif any(k in name_lower for k in ["feed", "feeds", "raw material", "ordering", "vendor", "silo", "dorb", "soya", "maize"]):
        return "Sunfra Feeds"
    else:
        return "Sunfra Farms\""""

code = code.replace(old_func, new_func)

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\generate_escalation_report.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated get_company_category in generate_escalation_report.py!")
