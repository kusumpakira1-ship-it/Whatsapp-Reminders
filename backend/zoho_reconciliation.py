import logging
import re
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
from models import ProcessedData, RawMessage

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def extract_physical_balances_from_whatsapp(exact_group_name: str):
    """
    Parses WhatsApp messages ONLY from the 1 exact designated group for each company:
    - 'Accounts Poultry' for Sunfra Farms
    - 'Summary - Sunfra Feeds' for Sunfra Feeds
    - 'Sunfra Corporate P&L' for Sunfra Corporate
    to extract reported physical balances for Petty Cash and Bank.
    """
    from sqlalchemy import or_, desc
    from models import Group, WhatsAppMessage
    db = SessionLocal()
    res = {
        'petty_cash': None,
        'farm_petty_cash': None,
        'undeposited_funds': None,
        'sunfra_farms_bank': None,
        'sunfra_indian_bank': None,
        'bank_balance': None,
        'sbi_term_loan': None,
        'sunfra_farm_od': None
    }
    try:
        # Find exact group JIDs and exact name from sunfra_groups
        target_name_lower = exact_group_name.strip().lower()
        group_rows = db.query(Group).all()
        target_jids = set()
        for g in group_rows:
            gname = (g.name or '').strip().lower()
            gjid = (g.whatsapp_group_id or '').replace('@g.us', '').strip().lower()
            if gname == target_name_lower or target_name_lower in gname:
                if gjid:
                    target_jids.add(gjid)
                    target_jids.add(g.whatsapp_group_id.strip().lower())

        kw_pattern = f"%{exact_group_name}%"
        
        # Fetch ONLY from the designated group in RawMessage
        raw_msgs = db.query(RawMessage).filter(
            or_(
                RawMessage.group_name.ilike(kw_pattern),
                RawMessage.group_name.in_(list(target_jids))
            ) if target_jids else RawMessage.group_name.ilike(kw_pattern)
        ).order_by(desc(RawMessage.timestamp)).limit(30).all()

        # Fetch ONLY from the designated group in WhatsAppMessage
        wa_msgs = db.query(WhatsAppMessage).filter(
            or_(
                WhatsAppMessage.group_id.ilike(kw_pattern),
                WhatsAppMessage.group_id.in_(list(target_jids))
            ) if target_jids else WhatsAppMessage.group_id.ilike(kw_pattern)
        ).order_by(desc(WhatsAppMessage.timestamp)).limit(30).all()

        combined = []
        for m in raw_msgs:
            combined.append({'text': (m.raw_text or '').lower(), 'ts': m.timestamp})
        for m in wa_msgs:
            combined.append({'text': (m.message_text or '').lower(), 'ts': m.timestamp})

        combined.sort(key=lambda x: x['ts'], reverse=True)

        for m in combined:
            text = m['text']

            # Extract Farm Petty Cash (Strict format: "Farm Petty Cash : 1000")
            if res['farm_petty_cash'] is None:
                fp_match = re.search(r'(?:farm\s*petty\s*cash)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if fp_match:
                    try:
                        res['farm_petty_cash'] = float(fp_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Petty Cash / Cash in hand (Strict format: "Petty Cash : 1000" or "Cash in hand - 1000")
            if res['petty_cash'] is None:
                p_match = re.search(r'(?<!farm\s)(?:petty\s*cash|cash\s*in\s*hand|closing\s*cash|day\s*book)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if p_match:
                    try:
                        res['petty_cash'] = float(p_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Undeposited Funds (Strict format: "Undeposited Funds : 1000")
            if res['undeposited_funds'] is None:
                uf_match = re.search(r'(?:undeposited\s*funds?)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if uf_match:
                    try:
                        res['undeposited_funds'] = float(uf_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract SUNFRA FARMS Bank (Strict format: "SUNFRA FARMS Bank : 861742.99")
            if res['sunfra_farms_bank'] is None:
                sf_match = re.search(r'(?:sunfra\s*farms?\s*bank|farms?\s*bank)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if sf_match:
                    try:
                        res['sunfra_farms_bank'] = float(sf_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Sunfra Indian Bank (Strict format: "Sunfra Indian Bank : 1000")
            if res['sunfra_indian_bank'] is None:
                ib_match = re.search(r'(?:indian\s*bank|sunfra\s*indian\s*bank)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if ib_match:
                    try:
                        res['sunfra_indian_bank'] = float(ib_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Total Available Bank Balance (Strict format: "Bank Balance : 1000")
            if res['bank_balance'] is None:
                b_match = re.search(r'(?:total\s*available\s*bank|available\s*bank|bank\s*balance|total\s*bank)\s*[:=\-]\s*([\d,]+(?:\.\d+)?)', text)
                if b_match:
                    try:
                        res['bank_balance'] = float(b_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract SBI Term Loan (e.g. "SBI TERM LOAN ACCOUNT: -22673573.77" or "SBI Term Loan : 22823573.77")
            if res['sbi_term_loan'] is None:
                loan_match = re.search(r'(?:sbi\s*term\s*loan(?:\s*account)?|term\s*loan(?:\s*account)?|5637)\s*[:=\-]?\s*(-?[\d,]+(?:\.\d+)?)', text)
                if loan_match:
                    try:
                        val = float(loan_match.group(1).replace(',', ''))
                        res['sbi_term_loan'] = -abs(val)
                    except ValueError:
                        pass

            # Extract SUNFRA FARM OD (e.g. "SUNFRA FARM OD: -27096358.90" or "SUNFRA FARM OD:-28712530.90")
            if res['sunfra_farm_od'] is None:
                od_match = re.search(r'(?:sunfra\s*farm\s*od|farm\s*od|od\s*balance|od-0718|0718)\s*[:=\-]?\s*(-?[\d,]+(?:\.\d+)?)', text)
                if od_match:
                    try:
                        val = float(od_match.group(1).replace(',', ''))
                        res['sunfra_farm_od'] = -abs(val)
                    except ValueError:
                        pass
    except Exception as e:
        logger.error(f"Error extracting physical balances for group {exact_group_name}: {e}")
    finally:
        db.close()
    return res


def format_reconciliation_block(name: str, physical_val: float, zoho_val: float):
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    if physical_val is None:
        return f"• *{name}*:\n  Physical: *Not Updated*  Zoho: *{fmt_curr(zoho_val)}* ⚠️"
    else:
        diff = physical_val - zoho_val
        if abs(diff) < 0.01:
            return f"• *{name}*:\n  Physical: *{fmt_curr(physical_val)}*  Zoho: *{fmt_curr(zoho_val)}* ✅"
        else:
            diff_sign = "+" if diff > 0 else "-"
            return f"• *{name}*:\n  Physical: *{fmt_curr(physical_val)}*  Zoho: *{fmt_curr(zoho_val)}* ⚠️ (Diff: {diff_sign}Rs. {abs(diff):,.2f})"


def format_receivables_breakdown(receivables_dict: dict):
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    cnt = receivables_dict.get("count", 0) if isinstance(receivables_dict, dict) else 0
    tot = receivables_dict.get("total_amount", 0.0) if isinstance(receivables_dict, dict) else float(receivables_dict or 0.0)
    details = receivables_dict.get("details", []) if isinstance(receivables_dict, dict) else []

    lines = [f"📈 *Customer Receivables Breakdown*:"]
    lines.append(f"• Total Pending: *{cnt} Invoices* | Balance: *{fmt_curr(tot)}*")

    if details:
        total_items = len(details)
        for idx, item in enumerate(details, 1):
            c_name = item.get("customer_name", "Customer")
            amt = item.get("balance", 0.0)
            days = item.get("aging_days", 0)
            connector = "└" if idx == total_items else "├"
            lines.append(f"  {connector} {idx}. *{c_name}*: *{fmt_curr(amt)}* (OD {days})")
    return "\n".join(lines)


def format_payables_breakdown(payables_dict: dict):
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    cnt = payables_dict.get("count", 0) if isinstance(payables_dict, dict) else 0
    tot = payables_dict.get("total_amount", 0.0) if isinstance(payables_dict, dict) else float(payables_dict or 0.0)
    details = payables_dict.get("details", []) if isinstance(payables_dict, dict) else []

    lines = [f"📋 *Vendor Payables Summary*: *{cnt} Pending Bills* | Balance: *{fmt_curr(tot)}*"]

    if details:
        total_items = len(details)
        for idx, item in enumerate(details, 1):
            v_name = item.get("vendor_name", "Vendor")
            amt = item.get("balance", 0.0)
            days = item.get("aging_days", 0)
            connector = "└" if idx == total_items else "├"
            lines.append(f"  {connector} {idx}. *{v_name}*: *{fmt_curr(amt)}* (OD {days})")
    return "\n".join(lines)


def generate_and_send_zoho_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances, reconciles with WhatsApp farm data, and sends exclusively to recipient."""
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
    
    # 1. Fetch Zoho Balances & Receivables/Payables
    accounts = get_chart_of_accounts(access_token, org_id)
    receivables = get_receivables_summary(access_token, org_id)
    payables = get_payables_summary(access_token, org_id)
    
    # 2. Extract Physical Balances ONLY from WhatsApp Group 'Accounts Poultry'
    physical = extract_physical_balances_from_whatsapp('Accounts Poultry')
    
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

    # 3. Format WhatsApp Message Report
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
        format_reconciliation_block("SBI TERM LOAN ACCOUNT (5637)", physical.get('sbi_term_loan'), accounts.get('sbi_term_loan', 0.0)),
        "",
        format_reconciliation_block("SUNFRA FARM OD-0718 (0718)", physical.get('sunfra_farm_od'), accounts.get('sunfra_farm_od', 0.0)),
        "",
        format_receivables_breakdown(receivables),
        "",
        format_payables_breakdown(payables)
    ]

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Zoho Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success


def generate_and_send_sunfra_feeds_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances for Sunfra Feeds and reconciles ONLY with WhatsApp group 'Summary - Sunfra Feeds'."""
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
    
    # 2. Extract Physical Balances ONLY from WhatsApp Group 'Summary - Sunfra Feeds'
    physical = extract_physical_balances_from_whatsapp('Summary - Sunfra Feeds')
    
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

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

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Sunfra Feeds Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success


def generate_and_send_sunfra_corporate_reconciliation_report(recipient_phone: str = None) -> bool:
    """Fetches live Zoho Books balances for Sunfra Corporate and reconciles ONLY with WhatsApp group 'Sunfra Corporate P&L'."""
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
    
    # 2. Extract Physical Balances ONLY from WhatsApp Group 'Sunfra Corporate P&L'
    physical = extract_physical_balances_from_whatsapp('Sunfra Corporate P&L')
    
    def fmt_curr(val):
        v = float(val or 0.0)
        if v < 0:
            return f"-Rs. {abs(v):,.2f}"
        return f"Rs. {v:,.2f}"

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

    report_text = "\n".join(msg_lines)
    logger.info(f"Sending Sunfra Corporate Reconciliation Report to {target_phone}...")
    success = send_waha_message(target_phone, report_text)
    return success
