import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from zoho_service import (
    get_access_token,
    get_organization_id,
    get_chart_of_accounts,
    get_egg_godown_stock,
    get_receivables_summary,
    get_payables_summary,
    get_today_zoho_sales_out
)
from database import SessionLocal
from models import ProcessedData
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST)
today_str = now_ist.strftime("%d %b %Y, %I:%M %p")

access_token = get_access_token()
if not access_token:
    print("⚠️ Unable to connect to Zoho Books API because no valid OAuth token was found.")
    sys.exit(0)

org_id = get_organization_id(access_token)

# 1. Fetch Zoho Balances & Sales
accounts = get_chart_of_accounts(access_token, org_id)
egg_stock = get_egg_godown_stock(access_token, org_id)
receivables = get_receivables_summary(access_token, org_id)
payables = get_payables_summary(access_token, org_id)
zoho_sales_today = get_today_zoho_sales_out(access_token, org_id)

# 2. Fetch WhatsApp Farm Data
db = SessionLocal()
wa_egg_trays = 0.0
try:
    today_date = now_ist.date()
    egg_records = db.query(ProcessedData).filter(
        ProcessedData.category.in_(['egg_collection_1', 'egg_collection_2', 'egg_collection_3', 'egg_collection', 'egg_loaded']),
        ProcessedData.processed_time >= today_date
    ).all()
    for r in egg_records:
        qty = float(r.quantity or 0)
        unit = str(r.unit or '').lower()
        trays = qty if 'tray' in unit else qty / 30.0
        wa_egg_trays += trays
except Exception as e:
    pass
finally:
    db.close()

rec_cnt = receivables.get("count", 0) if isinstance(receivables, dict) else 0
rec_amt = receivables.get("total_amount", 0.0) if isinstance(receivables, dict) else float(receivables or 0.0)

pay_cnt = payables.get("count", 0) if isinstance(payables, dict) else 0
pay_amt = payables.get("total_amount", 0.0) if isinstance(payables, dict) else float(payables or 0.0)

zoho_trays = float(egg_stock.get('total_trays', 0.0) or 0.0)
zoho_eggs = int(egg_stock.get('total_eggs', 0) or 0)
wa_total_eggs = int(wa_egg_trays * 30)

zoho_sales_trays = float(zoho_sales_today.get('total_trays_out', 0.0))
zoho_sales_eggs = int(zoho_sales_today.get('total_eggs_out', 0))

diff_trays = round(abs(zoho_trays - wa_egg_trays), 1)
diff_eggs = abs(zoho_eggs - wa_total_eggs)

if diff_eggs == 0:
    match_line = "• Stock Reconciliation Status: *MATCHING ✅*"
else:
    match_line = f"• Stock Reconciliation Status: *MISMATCH ⚠️*\n  └ *Difference:* *{diff_trays:,.1f} Trays* (*{diff_eggs:,} Eggs*)"

msg_lines = [
    "📊 *ZOHO BOOKS & FARM RECONCILIATION REPORT*",
    f"📅 *Date:* {today_str}",
    "--------------------------------------------------",
    "💰 *Active Account Balances (Sunfra Farms)*:",
    f"• Petty Cash: *Rs. {accounts.get('petty_cash', 0.0):,.2f}*",
    f"• Sunfra Indian Bank (3514): *Rs. {accounts.get('sunfra_indian_bank', 0.0):,.2f}*",
    f"• SUNFRA FARMS Bank (5698): *Rs. {accounts.get('sunfra_farms_bank', 0.0):,.2f}*",
    f"• Total Available Bank Balance: *Rs. {accounts.get('total_bank_balance', 0.0):,.2f}*",
    f"• SBI TERM LOAN ACCOUNT (5637): *Rs. {abs(accounts.get('sbi_term_loan', 0.0)):,.2f}* (Loan)",
    f"• SUNFRA FARM OD-0718 (0718): *Rs. {abs(accounts.get('sunfra_farm_od', 0.0)):,.2f}* (OD)",
    "",
    "🥚 *Egg Godown Stock Reconciliation*:",
    f"• Zoho Books Stock: *{zoho_trays:,.1f} Trays* (*{zoho_eggs:,} Eggs*)",
    f"• WhatsApp Farm Reports Today: *{wa_egg_trays:,.1f} Trays* (*{wa_total_eggs:,} Eggs*)",
    match_line,
    "",
    "🚚 *Today's Zoho Sales Out (Invoices)*:",
    f"• Total Egg Sales Invoiced: *{zoho_sales_trays:,.1f} Trays* (*{zoho_sales_eggs:,} Eggs*)",
    "",
    "📋 *Outstanding Summary*:",
    f"• Total Unpaid Receivables: *Rs. {rec_amt:,.2f}* ({rec_cnt} Invoices)",
    f"• Total Unpaid Payables: *Rs. {pay_amt:,.2f}* ({pay_cnt} Bills)",
    "--------------------------------------------------",
    "✨ *Sunfra Automations - Zoho Books Sync*"
]

print("\n".join(msg_lines))
