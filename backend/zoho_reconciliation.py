import logging
from datetime import datetime, timezone, timedelta
from config import settings
from waha_service import send_waha_message
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

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def generate_and_send_zoho_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances, reconciles with WhatsApp farm data, and sends exclusively to 7259510983."""
    target_phone = recipient_phone or settings.ZOHO_RECIPIENT_PHONE or "917259510983"
    if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
        target_phone = f"{target_phone}@c.us"
        
    logger.info(f"Generating Zoho Reconciliation Report for target recipient {target_phone}...")
    
    access_token = get_access_token()
    if not access_token:
        error_msg = (
            "⚠️ *Zoho Books Integration Alert*\n\n"
            "Unable to connect to Zoho Books API because no valid OAuth token was found.\n"
            "Please complete 1-time Zoho authorization using your Client ID and Client Secret."
        )
        send_waha_message(target_phone, error_msg)
        return False

    org_id = get_organization_id(access_token)
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%d %b %Y, %I:%M %p")
    
    # 1. Fetch Zoho Balances & Sales
    accounts = get_chart_of_accounts(access_token, org_id)
    egg_stock = get_egg_godown_stock(access_token, org_id)
    receivables = get_receivables_summary(access_token, org_id)
    payables = get_payables_summary(access_token, org_id)
    zoho_sales_today = get_today_zoho_sales_out(access_token, org_id)
    
    # 2. Fetch WhatsApp Farm Data for comparison
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
        logger.error(f"Error fetching WhatsApp egg records for reconciliation: {e}")
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

    # 3. Format WhatsApp Message Report
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
        "🥚 *Egg Godown Stock Comparison*:",
        f"• Live Zoho Inventory Stock: *{zoho_trays:,.1f} Trays* ({zoho_eggs:,} Eggs)",
        f"• Today's WhatsApp Production IN: *{wa_egg_trays:,.1f} Trays* ({wa_total_eggs:,} Eggs)",
        f"• Today's Zoho Billed Sales OUT: *{zoho_sales_trays:,.1f} Trays* ({zoho_sales_eggs:,} Eggs) | *Rs. {zoho_sales_today.get('total_sales_amount', 0.0):,.2f}*",
        match_line,
        "",
        "📈 *Receivables & Payables Summary (Sunfra Farms)*:",
        f"• Customer Receivables: *{rec_cnt} Pending Invoices* | Balance: *Rs. {rec_amt:,.2f}*",
        f"• Vendor Payables: *{pay_cnt} Pending Bills* | Balance: *Rs. {pay_amt:,.2f}*",
        "--------------------------------------------------",
        "✅ *Extracted live from Zoho Books API & WhatsApp*"
    ]

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Zoho Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success
