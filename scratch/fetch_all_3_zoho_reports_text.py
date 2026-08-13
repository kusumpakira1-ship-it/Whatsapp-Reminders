"""
Fetch and print text for all 3 Zoho Books Reconciliation Reports (Farms, Feeds, Corporate)
"""

import sys, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from zoho_service import (
    get_access_token,
    get_organization_id,
    get_chart_of_accounts,
    get_receivables_summary,
    get_payables_summary
)

access_token = get_access_token()
print("OAuth Token Acquired:", "YES ✅" if access_token else "NO ❌")

def fmt_curr(val):
    v = float(val or 0.0)
    if v < 0:
        return f"-Rs. {abs(v):,.2f}"
    return f"Rs. {v:,.2f}"

today_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

# 1. Sunfra Farms (Org ID 905812487)
farms_org_id = "905812487"
accounts1 = get_chart_of_accounts(access_token, farms_org_id)
rec1 = get_receivables_summary(access_token, farms_org_id)
pay1 = get_payables_summary(access_token, farms_org_id)

rec1_cnt = rec1.get("count", 0) if isinstance(rec1, dict) else 0
rec1_amt = rec1.get("total_amount", 0.0) if isinstance(rec1, dict) else float(rec1 or 0.0)
pay1_cnt = pay1.get("count", 0) if isinstance(pay1, dict) else 0
pay1_amt = pay1.get("total_amount", 0.0) if isinstance(pay1, dict) else float(pay1 or 0.0)

report_farms = f"""📊 *ZOHO BOOKS & FARM RECONCILIATION REPORT*
📅 *Date:* {today_str}
--------------------------------------------------
💰 *Active Account Balances (Sunfra Farms)*:
• Petty Cash: *{fmt_curr(accounts1.get('petty_cash', 0.0))}*
• Sunfra Indian Bank (3514): *{fmt_curr(accounts1.get('sunfra_indian_bank', 0.0))}*
• SUNFRA FARMS Bank (5698): *{fmt_curr(accounts1.get('sunfra_farms_bank', 0.0))}*
• Total Available Bank Balance: *{fmt_curr(accounts1.get('total_bank_balance', 0.0))}*
• SBI TERM LOAN ACCOUNT (5637): *{fmt_curr(accounts1.get('sbi_term_loan', 0.0))}* (Loan)
• SUNFRA FARM OD-0718 (0718): *{fmt_curr(accounts1.get('sunfra_farm_od', 0.0))}* (OD)

📈 *Receivables & Payables Summary (Sunfra Farms)*:
• Customer Receivables: *{rec1_cnt} Pending Invoices* | Balance: *{fmt_curr(rec1_amt)}*
• Vendor Payables: *{pay1_cnt} Pending Bills* | Balance: *{fmt_curr(pay1_amt)}*
--------------------------------------------------
✅ *Extracted live from Zoho Books API & WhatsApp*"""


# 2. Sunfra Feeds (Org ID 932776276)
feeds_org_id = "932776276"
accounts2 = get_chart_of_accounts(access_token, feeds_org_id)
rec2 = get_receivables_summary(access_token, feeds_org_id)
pay2 = get_payables_summary(access_token, feeds_org_id)

rec2_cnt = rec2.get("count", 0) if isinstance(rec2, dict) else 0
rec2_amt = rec2.get("total_amount", 0.0) if isinstance(rec2, dict) else float(rec2 or 0.0)
pay2_cnt = pay2.get("count", 0) if isinstance(pay2, dict) else 0
pay2_amt = pay2.get("total_amount", 0.0) if isinstance(pay2, dict) else float(pay2 or 0.0)

report_feeds = f"""📊 *ZOHO BOOKS & FEEDS RECONCILIATION REPORT*
🏭 *Company: Sunfra Feeds*
📅 *Date:* {today_str}
--------------------------------------------------
💰 *Active Account Balances (Sunfra Feeds)*:
• Petty Cash: *{fmt_curr(accounts2.get('petty_cash', 0.0))}*
• Sunfra Feeds Bank Account: *{fmt_curr(accounts2.get('sunfra_feeds_bank', 0.0))}*
• Total Available Bank Balance: *{fmt_curr(accounts2.get('total_bank_balance', 0.0))}*

📈 *Receivables & Payables Summary (Sunfra Feeds)*:
• Customer Receivables: *{rec2_cnt} Pending Invoices* | Balance: *{fmt_curr(rec2_amt)}*
• Vendor Payables: *{pay2_cnt} Pending Bills* | Balance: *{fmt_curr(pay2_amt)}*
--------------------------------------------------
✅ *Extracted live from Zoho Books API & WhatsApp*"""


# 3. Sunfra Corporate (Org ID 929124131)
corp_org_id = "929124131"
accounts3 = get_chart_of_accounts(access_token, corp_org_id)
rec3 = get_receivables_summary(access_token, corp_org_id)
pay3 = get_payables_summary(access_token, corp_org_id)

rec3_cnt = rec3.get("count", 0) if isinstance(rec3, dict) else 0
rec3_amt = rec3.get("total_amount", 0.0) if isinstance(rec3, dict) else float(rec3 or 0.0)
pay3_cnt = pay3.get("count", 0) if isinstance(pay3, dict) else 0
pay3_amt = pay3.get("total_amount", 0.0) if isinstance(pay3, dict) else float(pay3 or 0.0)

report_corp = f"""📊 *ZOHO BOOKS & CORPORATE RECONCILIATION REPORT*
🏢 *Company: Sunfra Corporate*
📅 *Date:* {today_str}
--------------------------------------------------
💰 *Active Account Balances (Sunfra Corporate)*:
• Petty Cash (Cash In Hand): *{fmt_curr(accounts3.get('petty_cash', 0.0))}*
• Total Available Bank Balance: *{fmt_curr(accounts3.get('total_bank_balance', 0.0))}*

📈 *Receivables & Payables Summary (Sunfra Corporate)*:
• Customer Receivables: *{rec3_cnt} Pending Invoices* | Balance: *{fmt_curr(rec3_amt)}*
• Vendor Payables: *{pay3_cnt} Pending Bills* | Balance: *{fmt_curr(pay3_amt)}*
--------------------------------------------------
✅ *Extracted live from Zoho Books API & WhatsApp*"""

print("\n=========================================================================")
print("REPORT 1: SUNFRA FARMS")
print("=========================================================================")
print(report_farms)

print("\n=========================================================================")
print("REPORT 2: SUNFRA FEEDS")
print("=========================================================================")
print(report_feeds)

print("\n=========================================================================")
print("REPORT 3: SUNFRA CORPORATE")
print("=========================================================================")
print(report_corp)
