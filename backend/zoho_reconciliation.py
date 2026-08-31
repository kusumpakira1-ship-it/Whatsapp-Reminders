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
    Parses WhatsApp messages from designated group names and sender LIDs for each company:
    - 'Accounts Poultry' for Sunfra Farms
    - 'Summary - Sunfra Feeds' / 'Accounts - Sunfra Feeds' for Sunfra Feeds
    - 'Sunfra Corporate P&L' for Sunfra Corporate
    to extract reported physical balances for Petty Cash, Bank, Term Loan, and OD.
    """
    from sqlalchemy import desc
    from models import RawMessage, WhatsAppMessage
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
        company_targets = {
            'accounts poultry': ['accounts poultry', 'sunfra farms', 'payments - sunfra farms', '120363042907512705', '184791135711366'],
            'summary - sunfra feeds': ['summary - sunfra feeds', 'accounts - sunfra feeds', 'sunfra feeds', 'payments - sunfra feeds', 'feeds', '120363428748481277', '45586833240126'],
            'sunfra corporate p&l': ['sunfra corporate p&l', 'sunfra corporate', 'corporate', '120363425581380088', '56556230058144']
        }
        
        target_name_lower = exact_group_name.strip().lower()
        targets = company_targets.get(target_name_lower, [target_name_lower])

        raw_msgs = db.query(RawMessage).order_by(desc(RawMessage.timestamp)).limit(3000).all()
        wa_msgs = db.query(WhatsAppMessage).order_by(desc(WhatsAppMessage.timestamp)).limit(3000).all()

        combined = []
        for m in raw_msgs:
            grp = (m.group_name or '').lower()
            snd = (m.sender or '').lower()
            if any(t in grp or t in snd for t in targets):
                combined.append({'text': m.raw_text or '', 'ts': m.timestamp})
                
        for m in wa_msgs:
            grp = (m.group_id or '').lower()
            snd = (m.sender_id or '').lower()
            if any(t in grp or t in snd for t in targets):
                combined.append({'text': m.message_text or '', 'ts': m.timestamp})

        now_ist = datetime.now(IST)
        today_date = now_ist.date()
        
        # Filter strictly to messages posted TODAY ONLY per user explicit directive
        today_combined = [m for m in combined if m['ts'] and m['ts'].astimezone(IST).date() == today_date]
        today_combined.sort(key=lambda x: x['ts'], reverse=True)

        for m in today_combined:
            text = m['text']
            if not text:
                continue

            # Extract Farm Petty Cash
            if res['farm_petty_cash'] is None:
                fp_match = re.search(r'(?:farm\s*petty\s*cash|farm\s*cash|farm\s*pettycash)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if fp_match:
                    try:
                        res['farm_petty_cash'] = float(fp_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Petty Cash / Cash in hand / Day Book
            if res['petty_cash'] is None:
                p_match = re.search(r'(?<!farm\s)(?:petty\s*cash|pettycash|cash\s*in\s*hand|closing\s*cash|cash\s*balance|cash\s*bal|day\s*book|daybook)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if p_match:
                    try:
                        res['petty_cash'] = float(p_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Undeposited Funds
            if res['undeposited_funds'] is None:
                uf_match = re.search(r'(?:undeposited\s*funds?|undeposited\s*fund|undeposited)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if uf_match:
                    try:
                        res['undeposited_funds'] = float(uf_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract SUNFRA FARMS Bank
            if res['sunfra_farms_bank'] is None:
                sf_match = re.search(r'(?:sunfra\s*farms?\s*bank|farms?\s*bank|sunfra\s*farm\s*bank|farm\s*bank|sunfra\s*bank)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if sf_match:
                    try:
                        res['sunfra_farms_bank'] = float(sf_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Sunfra Indian Bank
            if res['sunfra_indian_bank'] is None:
                ib_match = re.search(r'(?:indian\s*bank|sunfra\s*indian\s*bank|indian\s*bank\s*bal)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if ib_match:
                    try:
                        res['sunfra_indian_bank'] = float(ib_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Total Available Bank Balance / Bank Balance
            if res['bank_balance'] is None:
                b_match = re.search(r'(?:total\s*available\s*bank\s*balance|total\s*available\s*bank|available\s*bank\s*balance|available\s*bank|bank\s*balance|bank\s*bal|total\s*bank|feeds\s*bank|corporate\s*bank)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if b_match:
                    try:
                        res['bank_balance'] = float(b_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract SBI Term Loan
            if res['sbi_term_loan'] is None:
                loan_match = re.search(r'(?:sbi\s*term\s*loan(?:\s*account)?|term\s*loan(?:\s*account)?|sbi\s*loan|loan\s*account|5637)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
                if loan_match:
                    try:
                        val = float(loan_match.group(1).replace(',', ''))
                        res['sbi_term_loan'] = -abs(val)
                    except ValueError:
                        pass

            # Extract SUNFRA FARM OD
            if res['sunfra_farm_od'] is None:
                od_match = re.search(r'(?:sunfra\s*farm\s*od|farm\s*od|od\s*balance|od\s*bal|od-0718|0718)\s*[:=\-]?\s*(?:₹|rs\.?|inr)?\s*(-?[\d,]+(?:\.\d+)?)\s*(?:/\-)?', text, re.I)
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


def format_indian_currency(val, show_symbol=True) -> str:
    try:
        v = float(val or 0.0)
    except (ValueError, TypeError):
        v = 0.0
    
    is_negative = v < 0
    v = abs(v)
    
    s = f"{v:.2f}"
    integer_part, decimal_part = s.split('.')
    
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        other_digits = integer_part[:-3]
        groups = []
        while len(other_digits) > 2:
            groups.insert(0, other_digits[-2:])
            other_digits = other_digits[:-2]
        if other_digits:
            groups.insert(0, other_digits)
        formatted_int = ",".join(groups) + "," + last_three
    else:
        formatted_int = integer_part
        
    formatted_val = f"{formatted_int}.{decimal_part}"
    prefix = "-" if is_negative else ""
    symbol = "Rs. " if show_symbol else ""
    return f"{prefix}{symbol}{formatted_val}"


def format_reconciliation_block(name: str, physical_val: float, zoho_val: float):
    if physical_val is None:
        return f"• *{name}*:\n  Physical: *Not Updated Today*  Zoho: *{format_indian_currency(zoho_val)}* ⚠️"
    else:
        diff = physical_val - zoho_val
        if abs(diff) < 0.01:
            return f"• *{name}*:\n  Physical: *{format_indian_currency(physical_val)}*  Zoho: *{format_indian_currency(zoho_val)}* ✅"
        else:
            diff_sign = "+" if diff > 0 else "-"
            return f"• *{name}*:\n  Physical: *{format_indian_currency(physical_val)}*  Zoho: *{format_indian_currency(zoho_val)}* ⚠️ (Diff: {diff_sign}{format_indian_currency(abs(diff))})"


def format_receivables_breakdown(receivables_dict: dict):
    cnt = receivables_dict.get("count", 0) if isinstance(receivables_dict, dict) else 0
    tot = receivables_dict.get("total_amount", 0.0) if isinstance(receivables_dict, dict) else float(receivables_dict or 0.0)
    details = list(receivables_dict.get("details", [])) if isinstance(receivables_dict, dict) else []

    # Sort in descending order of OD (aging_days), then balance
    details.sort(key=lambda x: (x.get("aging_days", 0), x.get("balance", 0.0)), reverse=True)

    lines = [f"📈 *Customer Receivables Breakdown*:"]
    lines.append(f"• Total Pending: *{cnt} Invoices* | Balance: *{format_indian_currency(tot)}*")

    if details:
        total_items = len(details)
        for idx, item in enumerate(details, 1):
            c_name = item.get("customer_name", "Customer")
            amt = item.get("balance", 0.0)
            days = item.get("aging_days", 0)
            connector = "└" if idx == total_items else "├"
            lines.append(f"  {connector} {idx}. *{c_name}*: *{format_indian_currency(amt)}* (OD {days})")
    return "\n".join(lines)


def format_payables_breakdown(payables_dict: dict):
    cnt = payables_dict.get("count", 0) if isinstance(payables_dict, dict) else 0
    tot = payables_dict.get("total_amount", 0.0) if isinstance(payables_dict, dict) else float(payables_dict or 0.0)
    details = list(payables_dict.get("details", [])) if isinstance(payables_dict, dict) else []

    # Sort in descending order of OD (aging_days), then balance
    details.sort(key=lambda x: (x.get("aging_days", 0), x.get("balance", 0.0)), reverse=True)

    lines = [f"📋 *Vendor Payables Summary*: *{cnt} Pending Bills* | Balance: *{format_indian_currency(tot)}*"]

    if details:
        total_items = len(details)
        for idx, item in enumerate(details, 1):
            v_name = item.get("vendor_name", "Vendor")
            amt = item.get("balance", 0.0)
            days = item.get("aging_days", 0)
            connector = "└" if idx == total_items else "├"
            lines.append(f"  {connector} {idx}. *{v_name}*: *{format_indian_currency(amt)}* (OD {days})")
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

    farms_org_id = "905812487"
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%d %b %Y")
    
    # 1. Fetch Zoho Balances & Receivables/Payables for Sunfra Farms
    accounts = get_chart_of_accounts(access_token, farms_org_id)
    receivables = get_receivables_summary(access_token, farms_org_id)
    payables = get_payables_summary(access_token, farms_org_id)
    
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
        format_reconciliation_block("Undeposited Funds", physical.get('undeposited_funds'), accounts.get('undeposited_funds', 0.0)),
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
    
    # Also dispatch Feeds and Corporate Reconciliation Reports to target recipient
    try:
        generate_and_send_sunfra_feeds_reconciliation_report(target_phone)
        generate_and_send_sunfra_corporate_reconciliation_report(target_phone)
    except Exception as e_sub:
        logger.error(f"Error sending Feeds/Corporate reconciliation reports: {e_sub}")
        
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
    today_str = now_ist.strftime("%d %b %Y")
    
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
    today_str = now_ist.strftime("%d %b %Y")
    
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
