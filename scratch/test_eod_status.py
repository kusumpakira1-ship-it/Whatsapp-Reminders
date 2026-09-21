import sys

sys.path.append('backend')
from get_reports_text import get_company_reports_text

sys.stdout.reconfigure(encoding='utf-8')

print("================ EOD REPORT STATUS FOR SUNFRA FARMS (16 SEP 2026) ================")
farms_text = get_company_reports_text("Sunfra Farms", target_date="2026-09-16")
print(farms_text)
