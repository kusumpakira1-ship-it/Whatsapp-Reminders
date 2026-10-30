import sys
import os
import requests
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from zoho_4company_pandl import (
    fetch_today_sales_and_purchases,
    fetch_inventory_stock_data,
    fetch_balance_sheet_cash_and_equivalents,
    fetch_historical_net_positions
)
from zoho_reconciliation import (
    format_indian_currency,
    format_reconciliation_block,
    format_today_sales_purchases_breakdown,
    format_receivables_breakdown,
    format_payables_breakdown,
    format_loans_breakdown
)
from zoho_service import get_chart_of_accounts, get_receivables_summary, get_payables_summary

token = '1000.8d220264e57b0769d33d563af8ad6e60.00c8c5adc99a673bed450fe928460800'
org_id = '904503869'

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST)
today_str = now_ist.strftime("%d %b %Y")
today_date_str = now_ist.strftime("%Y-%m-%d")

# 1. Fetch Balances
accounts = get_chart_of_accounts(token, org_id)
receivables = get_receivables_summary(token, org_id)
payables = get_payables_summary(token, org_id)
sales_total, purch_total, sales_cnt, purch_cnt, sales_list, purch_list = fetch_today_sales_and_purchases(token, org_id, today_date_str)
stock_val, neg_items = fetch_inventory_stock_data(token, org_id)
bank_and_cash_total, bs_cash, bs_bank = fetch_balance_sheet_cash_and_equivalents(token, org_id)

rec_total = receivables.get('total_receivable', 0.0) or receivables.get('total_amount', 0.0)
pay_total = payables.get('total_payable', 0.0) or payables.get('total_amount', 0.0)
net_financial_position = (stock_val + rec_total + bank_and_cash_total) - pay_total

msg_lines = [
    "🌱 *Raj Farms — Daily Comprehensive Report*",
    f"📅 *Date:* {today_str}",
    "==================================================",
    "💰 *Active Account Balances (Raj Farms)*:"
]

# Add specific accounts for Raj Farms
for acc in accounts.get('details', []):
    msg_lines.append(f"  • *{acc['name']}*: *{format_indian_currency(acc['balance'])}*")

msg_lines.extend([
    "",
    format_today_sales_purchases_breakdown(sales_total, purch_total, sales_cnt, purch_cnt, sales_list, purch_list),
    "",
    format_receivables_breakdown(receivables),
    "",
    format_payables_breakdown(payables),
    "--------------------------------------------------",
    f"📦 *Stock Valuation (Inventory Asset):* *{format_indian_currency(stock_val)}*",
    f"💰 *Bank & Cash Balance:* *{format_indian_currency(bank_and_cash_total)}*"
])

net_pos_status = "✅ Profit" if net_financial_position >= 0 else "⚠️ Deficit"
msg_lines.append(f"⚖️ *Overall Net Financial Position:* *{format_indian_currency(net_financial_position)}* ({net_pos_status})")

hist_positions = fetch_historical_net_positions(token, org_id, net_financial_position, today_date_str, "Raj Farms")
hist_lines = [f"  • {lbl}: *{format_indian_currency(pos)}*" for lbl, pos in hist_positions]
msg_lines.append("📊 *Net Position Breakdown (History):*\n" + "\n".join(hist_lines))

if neg_items:
    neg_strs = [f"• {item_name}: *{qty:,.2f} units*" for item_name, qty in neg_items]
    msg_lines.append(f"⚠️ *Negative Stock Warning ({len(neg_items)} items):*\n  " + "\n  ".join(neg_strs))
else:
    msg_lines.append("⚠️ *Negative Stock:* *None* ✅")

msg_lines.append("")
msg_lines.append(format_loans_breakdown(token, org_id))
msg_lines.append("==================================================")

report_text = "\n".join(msg_lines)
print("\n" + report_text)
