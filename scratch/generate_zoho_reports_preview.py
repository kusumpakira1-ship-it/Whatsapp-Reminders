"""
Generate and print preview of all 3 10:00 PM Zoho Reconciliation Reports
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timezone, timedelta
from zoho_service import (
    get_access_token,
    get_organization_id,
    get_chart_of_accounts,
    get_receivables_summary,
    get_payables_summary
)
from zoho_reconciliation import (
    extract_physical_balances_from_whatsapp,
    format_reconciliation_block,
    format_receivables_breakdown,
    format_payables_breakdown
)

IST = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(IST).strftime("%d %b %Y, 10:00 PM")

access_token = get_access_token()
farms_org_id = get_organization_id(access_token)
feeds_org_id = "932776276"
corp_org_id = "929124131"

print("=" * 80)
print("🌾 1. SUNFRA FARMS ZOHO RECONCILIATION REPORT (10:00 PM DISPATCH)")
print("=" * 80)
try:
    accounts = get_chart_of_accounts(access_token, farms_org_id)
    receivables = get_receivables_summary(access_token, farms_org_id)
    payables = get_payables_summary(access_token, farms_org_id)
    physical = extract_physical_balances_from_whatsapp('Accounts Poultry')

    msg_lines = [
        "🌾 *Sunfra Farms Reports & Balances*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Farms)*:",
        format_reconciliation_block("Petty Cash", physical.get('petty_cash'), accounts.get('petty_cash', 0.0)),
        "",
        format_reconciliation_block("SUNFRA FARMS Bank", physical.get('sunfra_farms_bank'), accounts.get('sunfra_farms_bank', 0.0)),
        "",
        format_reconciliation_block("Sunfra Indian Bank", physical.get('sunfra_indian_bank'), accounts.get('sunfra_indian_bank', 0.0)),
        "",
        format_reconciliation_block("Total Available Bank Balance", physical.get('bank_balance'), accounts.get('total_bank_balance', 0.0)),
        "",
        format_reconciliation_block("SBI TERM LOAN ACCOUNT (5637)", physical.get('sbi_term_loan'), accounts.get('sbi_term_loan', 0.0)),
        "",
        format_reconciliation_block("SUNFRA FARM OD-0718 (0718)", physical.get('sunfra_farm_od'), accounts.get('sunfra_farm_od', 0.0)),
        "",
        format_receivables_breakdown(receivables),
        "",
        format_payables_breakdown(payables)
    ]
    print("\n".join(msg_lines))
except Exception as e:
    print(f"Error generating Farms Report: {e}")

print("\n" + "=" * 80)
print("🏭 2. SUNFRA FEEDS ZOHO RECONCILIATION REPORT (10:00 PM DISPATCH)")
print("=" * 80)
try:
    accounts = get_chart_of_accounts(access_token, feeds_org_id)
    receivables = get_receivables_summary(access_token, feeds_org_id)
    payables = get_payables_summary(access_token, feeds_org_id)
    physical = extract_physical_balances_from_whatsapp('Summary - Sunfra Feeds')

    msg_lines = [
        "🏭 *Company: Sunfra Feeds*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Feeds)*:",
        format_reconciliation_block("Petty Cash", physical.get('petty_cash'), accounts.get('petty_cash', 0.0)),
        "",
        format_reconciliation_block("Sunfra Feeds Bank Account", physical.get('bank_balance'), accounts.get('total_bank_balance', 0.0)),
        "",
        format_receivables_breakdown(receivables),
        "",
        format_payables_breakdown(payables)
    ]
    print("\n".join(msg_lines))
except Exception as e:
    print(f"Error generating Feeds Report: {e}")

print("\n" + "=" * 80)
print("🏢 3. SUNFRA CORPORATE ZOHO RECONCILIATION REPORT (10:00 PM DISPATCH)")
print("=" * 80)
try:
    accounts = get_chart_of_accounts(access_token, corp_org_id)
    receivables = get_receivables_summary(access_token, corp_org_id)
    payables = get_payables_summary(access_token, corp_org_id)
    physical = extract_physical_balances_from_whatsapp('Sunfra Corporate P&L')

    msg_lines = [
        "🏢 *Company: Sunfra Corporate*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Corporate)*:",
        format_reconciliation_block("Farm Petty Cash", physical.get('farm_petty_cash'), accounts.get('farm_petty_cash', 0.0)),
        "",
        format_reconciliation_block("Petty Cash", physical.get('petty_cash'), accounts.get('petty_cash', 0.0)),
        "",
        format_reconciliation_block("Undeposited Funds", physical.get('undeposited_funds'), accounts.get('undeposited_funds', 0.0)),
        "",
        format_reconciliation_block("Total Available Bank Balance", physical.get('bank_balance'), accounts.get('total_bank_balance', 0.0)),
        "",
        format_receivables_breakdown(receivables),
        "",
        format_payables_breakdown(payables)
    ]
    print("\n".join(msg_lines))
except Exception as e:
    print(f"Error generating Corporate Report: {e}")
