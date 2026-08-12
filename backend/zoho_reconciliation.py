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

        # Fetch today's physical Egg Godown stock typed by staff
        from models import EggGodownInventory
        today_godown = db.query(EggGodownInventory).filter(
            EggGodownInventory.date == today_date
        ).first()
        godown_physical_eggs = int(today_godown.closing_balance) if today_godown else None
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
    
    # Reconcile Zoho stock vs physical godown stock (from staff entry)
    if godown_physical_eggs is None:
        godown_trays_display = "Not Updated"
        godown_eggs_display = "Not Updated"
        match_line = "• Stock Reconciliation Status: *Godown Count Not Updated* ⚠️"
    else:
        godown_physical_trays = round(godown_physical_eggs / 30.0, 1)
        diff_trays = round(abs(zoho_trays - godown_physical_trays), 1)
        diff_eggs = abs(zoho_eggs - godown_physical_eggs)
        godown_trays_display = f"{godown_physical_trays:,.1f} Trays"
        godown_eggs_display = f"{godown_physical_eggs:,} Eggs"
        if diff_eggs == 0:
            match_line = "• Stock Reconciliation Status: *MATCHING ✅*"
        else:
            match_line = f"• Stock Reconciliation Status: *MISMATCH ⚠️*\n  └ *Difference:* *{diff_trays:,.1f} Trays* (*{diff_eggs:,} Eggs*)"

    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    # 3. Format WhatsApp Message Report
    msg_lines = [
        "📊 *ZOHO BOOKS & FARM RECONCILIATION REPORT*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Farms)*:",
        f"• Petty Cash: *{fmt_curr(accounts.get('petty_cash', 0.0))}*",
        f"• Sunfra Indian Bank (3514): *{fmt_curr(accounts.get('sunfra_indian_bank', 0.0))}*",
        f"• SUNFRA FARMS Bank (5698): *{fmt_curr(accounts.get('sunfra_farms_bank', 0.0))}*",
        f"• Total Available Bank Balance: *{fmt_curr(accounts.get('total_bank_balance', 0.0))}*",
        f"• SBI TERM LOAN ACCOUNT (5637): *{fmt_curr(accounts.get('sbi_term_loan', 0.0))}* (Loan)",
        f"• SUNFRA FARM OD-0718 (0718): *{fmt_curr(accounts.get('sunfra_farm_od', 0.0))}* (OD)",
        "",
        "🥚 *Egg Godown Stock Comparison*:",
        f"• Live Zoho Inventory Stock: *{zoho_trays:,.1f} Trays* ({zoho_eggs:,} Eggs)",
        f"• Total Stocks in Egg Godown: *{godown_trays_display}* ({godown_eggs_display})",
        f"• Today's Zoho Billed Sales OUT: *{zoho_sales_trays:,.1f} Trays* ({zoho_sales_eggs:,} Eggs) | *Rs. {zoho_sales_today.get('total_sales_amount', 0.0):,.2f}*",
        match_line,
        "",
        "📈 *Receivables & Payables Summary (Sunfra Farms)*:",
        f"• Customer Receivables: *{rec_cnt} Pending Invoices* | Balance: *{fmt_curr(rec_amt)}*",
        f"• Vendor Payables: *{pay_cnt} Pending Bills* | Balance: *{fmt_curr(pay_amt)}*",
        "--------------------------------------------------",
        "✅ *Extracted live from Zoho Books API & WhatsApp*"
    ]

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Zoho Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success


def generate_and_send_sunfra_feeds_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances for Sunfra Feeds (Org ID 932776276) and sends report to recipient."""
    target_phone = recipient_phone or settings.ZOHO_RECIPIENT_PHONE or "917259510983"
    if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
        target_phone = f"{target_phone}@c.us"
        
    logger.info(f"Generating Sunfra Feeds Zoho Reconciliation Report for target recipient {target_phone}...")
    
    access_token = get_access_token()
    if not access_token:
        error_msg = (
            "⚠️ *Zoho Books Integration Alert (Sunfra Feeds)*\n\n"
            "Unable to connect to Zoho Books API because no valid OAuth token was found."
        )
        send_waha_message(target_phone, error_msg)
        return False

    feeds_org_id = "932776276"
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%d %b %Y, %I:%M %p")
    
    # 1. Fetch Zoho Balances for Sunfra Feeds
    accounts = get_chart_of_accounts(access_token, feeds_org_id)
    receivables = get_receivables_summary(access_token, feeds_org_id)
    payables = get_payables_summary(access_token, feeds_org_id)
    
    rec_cnt = receivables.get("count", 0) if isinstance(receivables, dict) else 0
    rec_amt = receivables.get("total_amount", 0.0) if isinstance(receivables, dict) else float(receivables or 0.0)
    
    pay_cnt = payables.get("count", 0) if isinstance(payables, dict) else 0
    pay_amt = payables.get("total_amount", 0.0) if isinstance(payables, dict) else float(payables or 0.0)

    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    msg_lines = [
        "📊 *ZOHO BOOKS & FEEDS RECONCILIATION REPORT*",
        "🏭 *Company: Sunfra Feeds*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Feeds)*:",
        f"• Petty Cash: *{fmt_curr(accounts.get('petty_cash', 0.0))}*",
        f"• Sunfra Feeds Bank Account: *{fmt_curr(accounts.get('sunfra_feeds_bank', 0.0))}*",
        f"• Total Available Bank Balance: *{fmt_curr(accounts.get('total_bank_balance', 0.0))}*",
        "",
        "📈 *Receivables & Payables Summary (Sunfra Feeds)*:",
        f"• Customer Receivables: *{rec_cnt} Pending Invoices* | Balance: *{fmt_curr(rec_amt)}*",
        f"• Vendor Payables: *{pay_cnt} Pending Bills* | Balance: *{fmt_curr(pay_amt)}*",
        "--------------------------------------------------",
        "✅ *Extracted live from Zoho Books API & WhatsApp*"
    ]

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Sunfra Feeds Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success


def generate_and_send_sunfra_corporate_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances for Sunfra Corporate (Org ID 929124131) and sends report to recipient."""
    target_phone = recipient_phone or settings.ZOHO_RECIPIENT_PHONE or "917259510983"
    if not target_phone.endswith("@c.us") and not target_phone.endswith("@g.us"):
        target_phone = f"{target_phone}@c.us"
        
    logger.info(f"Generating Sunfra Corporate Zoho Reconciliation Report for target recipient {target_phone}...")
    
    access_token = get_access_token()
    if not access_token:
        error_msg = (
            "⚠️ *Zoho Books Integration Alert (Sunfra Corporate)*\n\n"
            "Unable to connect to Zoho Books API because no valid OAuth token was found."
        )
        send_waha_message(target_phone, error_msg)
        return False

    corp_org_id = "929124131"
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%d %b %Y, %I:%M %p")
    
    # 1. Fetch Zoho Balances for Sunfra Corporate
    accounts = get_chart_of_accounts(access_token, corp_org_id)
    receivables = get_receivables_summary(access_token, corp_org_id)
    payables = get_payables_summary(access_token, corp_org_id)
    
    rec_cnt = receivables.get("count", 0) if isinstance(receivables, dict) else 0
    rec_amt = receivables.get("total_amount", 0.0) if isinstance(receivables, dict) else float(receivables or 0.0)
    
    pay_cnt = payables.get("count", 0) if isinstance(payables, dict) else 0
    pay_amt = payables.get("total_amount", 0.0) if isinstance(payables, dict) else float(payables or 0.0)

    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    msg_lines = [
        "📊 *ZOHO BOOKS & CORPORATE RECONCILIATION REPORT*",
        "🏢 *Company: Sunfra Corporate*",
        f"📅 *Date:* {today_str}",
        "--------------------------------------------------",
        "💰 *Active Account Balances (Sunfra Corporate)*:",
        f"• Petty Cash (Cash In Hand): *{fmt_curr(accounts.get('petty_cash', 0.0))}*",
        f"• Total Available Bank Balance: *{fmt_curr(accounts.get('total_bank_balance', 0.0))}*",
        "",
        "📈 *Receivables & Payables Summary (Sunfra Corporate)*:",
        f"• Customer Receivables: *{rec_cnt} Pending Invoices* | Balance: *{fmt_curr(rec_amt)}*",
        f"• Vendor Payables: *{pay_cnt} Pending Bills* | Balance: *{fmt_curr(pay_amt)}*",
        "--------------------------------------------------",
        "✅ *Extracted live from Zoho Books API & WhatsApp*"
    ]

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Sunfra Corporate Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success
