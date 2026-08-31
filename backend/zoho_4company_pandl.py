import logging
import sys
# Ensure console can display Unicode emojis on Windows
sys.stdout.reconfigure(encoding='utf-8')
import requests
from datetime import datetime, timezone, timedelta
from config import settings
from waha_service import send_waha_message
from zoho_service import (
    get_access_token,
    ZOHO_BOOKS_API_URL,
    get_chart_of_accounts,
    get_receivables_summary,
    get_payables_summary
)

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

COMPANIES_CONFIG = [
    {
        'key': 'farms',
        'display_name': 'Sunfra Farms',
        'emoji': '🌾',
        'org_id': '905812487'
    },
    {
        'key': 'feeds',
        'display_name': 'Sunfra Feeds',
        'emoji': '🐔',
        'org_id': '932776276'
    },
    {
        'key': 'corporate',
        'display_name': 'Corporate',
        'emoji': '🏢',
        'org_id': '929124131'
    },
    {
        'key': 'indus',
        'display_name': 'Indus',
        'emoji': '⚡',
        'org_id': '893416886'
    }
]

def fetch_inventory_stock_data(access_token: str, org_id: str):
    """
    Fetches items from Zoho Books API to calculate total stock valuation
    and detect any items with negative stock quantity.
    """
    url = f"{ZOHO_BOOKS_API_URL}/items?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    total_stock_value = 0.0
    negative_items = []
    
    try:
        page = 1
        has_more = True
        while has_more:
            res = requests.get(f"{url}&page={page}", headers=headers, timeout=20)
            if res.status_code != 200:
                logger.error(f"Error fetching items for org {org_id}: {res.status_code}")
                break
                
            data = res.json()
            items = data.get("items", [])
            for it in items:
                # Check item stock quantity
                q = float(it.get("actual_available_stock", 0.0) or it.get("stock_on_hand", 0.0) or 0.0)
                rate = float(it.get("purchase_rate", 0.0) or it.get("rate", 0.0) or 0.0)
                
                # Calculate valuation for positive stock items
                if q > 0:
                    total_stock_value += (q * rate)
                elif q < 0:
                    negative_items.append((it.get("name", "Unknown Item"), q))
                    
            page_context = data.get("page_context", {})
            has_more = page_context.get("has_more_page", False)
            page += 1
    except Exception as e:
        logger.error(f"Exception fetching inventory stock for org {org_id}: {e}")
        
    return total_stock_value, negative_items


def fetch_today_sales_and_purchases(access_token: str, org_id: str, today_date_str: str):
    """
    Fetches Today's Total Sales (Invoices generated today) and
    Today's Total Costs (Bills & Expenses recorded today) for a specific org ID.
    """
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    today_sales = 0.0
    today_purchases = 0.0
    sales_count = 0
    purch_count = 0
    
    try:
        # 1. Today's Invoices (Sales)
        url_inv = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org_id}&date={today_date_str}"
        res_inv = requests.get(url_inv, headers=headers, timeout=20)
        if res_inv.status_code == 200:
            invs = res_inv.json().get("invoices", [])
            sales_count = len(invs)
            today_sales = sum(float(i.get("total", 0) or 0.0) for i in invs)

        # 2. Today's Bills (Purchases)
        url_bill = f"{ZOHO_BOOKS_API_URL}/bills?organization_id={org_id}&date={today_date_str}"
        res_bill = requests.get(url_bill, headers=headers, timeout=20)
        if res_bill.status_code == 200:
            bills = res_bill.json().get("bills", [])
            purch_count += len(bills)
            today_purchases += sum(float(b.get("total", 0) or 0.0) for b in bills)

        # 3. Today's Expenses
        url_exp = f"{ZOHO_BOOKS_API_URL}/expenses?organization_id={org_id}&date={today_date_str}"
        res_exp = requests.get(url_exp, headers=headers, timeout=20)
        if res_exp.status_code == 200:
            exps = res_exp.json().get("expenses", [])
            purch_count += len(exps)
            today_purchases += sum(float(e.get("total", 0) or e.get("amount", 0) or e.get("biller_amount", 0) or 0.0) for e in exps)
    except Exception as e:
        logger.error(f"Error fetching today sales/purchases for org {org_id}: {e}")
        
    return today_sales, today_purchases, sales_count, purch_count


def format_currency(val, show_symbol=True) -> str:
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


def generate_4company_pandl_report():
    """
    Generates a list of 4-Company Daily P&L Reports for Today (one report string per company),
    along with Stock Valuation, Receivables, Payables, Net Financial Position, and Negative Stock Items.
    """
    now_ist = datetime.now(IST)
    today_date_str = now_ist.strftime("%Y-%m-%d")
    display_date_str = now_ist.strftime("%d %b %Y")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to generate 4-Company Daily P&L Report: No valid Zoho access token.")
        return []

    company_reports = []
    
    for comp in COMPANIES_CONFIG:
        name = comp['display_name']
        emoji = comp['emoji']
        org_id = comp['org_id']
        
        msg_lines = [
            f"{emoji} *{name}* — 📊 *DAILY P&L & STOCK REPORT*",
            f"📅 *Date:* {display_date_str}",
            "=================================================="
        ]
        
        # 1. Fetch Today's Daily Sales & Costs
        today_sales, today_costs, sales_cnt, cost_cnt = fetch_today_sales_and_purchases(access_token, org_id, today_date_str)
        today_daily_pl = today_sales - today_costs
        
        # 2. Fetch Overall Balances & Inventory Stock Data
        accounts = get_chart_of_accounts(access_token, org_id)
        receivables_data = get_receivables_summary(access_token, org_id)
        payables_data = get_payables_summary(access_token, org_id)
        stock_val, neg_items = fetch_inventory_stock_data(access_token, org_id)
        
        bank_total = float(accounts.get('total_bank_balance', 0.0) or 0.0) + float(accounts.get('petty_cash', 0.0) or 0.0)
        rec_total = float(receivables_data.get('total_amount', 0.0) or receivables_data.get('total_balance', 0.0) or 0.0)
        pay_total = float(payables_data.get('total_amount', 0.0) or payables_data.get('total_balance', 0.0) or 0.0)
        
        # Overall Net Position = (Stock + Receivables + Bank) - Payables
        net_financial_position = (stock_val + rec_total + bank_total) - pay_total
        
        msg_lines.append(f"📈 *Today's Sales:* *{format_currency(today_sales)}* ({sales_cnt} invoices)")
        msg_lines.append(f"📋 *Today's Costs/Purchases:* *{format_currency(today_costs)}* ({cost_cnt} items)")
        
        pl_status = "✅ Daily Profit" if today_daily_pl >= 0 else "⚠️ Daily Loss"
        msg_lines.append(f"🧮 *TODAY'S DAILY NET P&L:* *{format_currency(today_daily_pl)}* ({pl_status})")
        msg_lines.append("--------------------------------------------------")
        msg_lines.append(f"📦 *Stock Valuation:* *{format_currency(stock_val)}*")
        msg_lines.append(f"💰 *Bank & Cash Balance:* *{format_currency(bank_total)}*")
        msg_lines.append(f"📈 *Total Receivables:* *{format_currency(rec_total)}*")
        msg_lines.append(f"📋 *Total Payables:* *{format_currency(pay_total)}*")
        
        net_pos_status = "✅ Profit" if net_financial_position >= 0 else "⚠️ Deficit"
        msg_lines.append(f"⚖️ *Overall Net Financial Position:* *{format_currency(net_financial_position)}* ({net_pos_status})")
        
        # Negative Stock Items warning (List ALL items as requested)
        if neg_items:
            neg_strs = [f"• {item_name}: *{qty:,.2f} units*" for item_name, qty in neg_items]
            msg_lines.append(f"⚠️ *Negative Stock Warning ({len(neg_items)} items):*\n  " + "\n  ".join(neg_strs))
        else:
            msg_lines.append("⚠️ *Negative Stock:* *None* ✅")
            
        msg_lines.append("==================================================")
        company_reports.append("\n".join(msg_lines))
        
    return company_reports


def fetch_range_sales_and_purchases(access_token: str, org_id: str, start_date_str: str, end_date_str: str):
    """
    Fetches Sales (Invoices) and Costs (Bills & Expenses) for a date range (start_date_str to end_date_str)
    for a specific Zoho org ID.
    """
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    total_sales = 0.0
    total_purchases = 0.0
    sales_count = 0
    purch_count = 0
    
    try:
        url_inv = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org_id}&date_start={start_date_str}&date_end={end_date_str}"
        res_inv = requests.get(url_inv, headers=headers, timeout=25)
        if res_inv.status_code == 200:
            invs = res_inv.json().get("invoices", [])
            sales_count = len(invs)
            total_sales = sum(float(i.get("total", 0) or 0.0) for i in invs)

        url_bill = f"{ZOHO_BOOKS_API_URL}/bills?organization_id={org_id}&date_start={start_date_str}&date_end={end_date_str}"
        res_bill = requests.get(url_bill, headers=headers, timeout=25)
        if res_bill.status_code == 200:
            bills = res_bill.json().get("bills", [])
            purch_count += len(bills)
            total_purchases += sum(float(b.get("total", 0) or 0.0) for b in bills)

        url_exp = f"{ZOHO_BOOKS_API_URL}/expenses?organization_id={org_id}&date_start={start_date_str}&date_end={end_date_str}"
        res_exp = requests.get(url_exp, headers=headers, timeout=25)
        if res_exp.status_code == 200:
            exps = res_exp.json().get("expenses", [])
            purch_count += len(exps)
            total_purchases += sum(float(e.get("total", 0) or e.get("amount", 0) or e.get("biller_amount", 0) or 0.0) for e in exps)
    except Exception as e:
        logger.error(f"Error fetching range sales/purchases for org {org_id}: {e}")
        
    return total_sales, total_purchases, sales_count, purch_count


def generate_4company_weekly_pandl_report():
    """
    Generates 4-Company Weekly P&L & Stock Reports for Sunday through Saturday.
    """
    now_ist = datetime.now(IST)
    # Calculate Sunday through Saturday range
    # weekday(): Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
    today_weekday = now_ist.weekday()
    # Days back to previous Sunday
    days_to_sun = (today_weekday + 1) % 7
    sun_date = now_ist.date() - timedelta(days=days_to_sun)
    sat_date = sun_date + timedelta(days=6)
    
    start_str = sun_date.strftime("%Y-%m-%d")
    end_str = sat_date.strftime("%Y-%m-%d")
    period_str = f"{sun_date.strftime('%d %b %Y')} to {sat_date.strftime('%d %b %Y')}"
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to generate 4-Company Weekly P&L Report: No valid Zoho access token.")
        return []

    company_reports = []
    
    for comp in COMPANIES_CONFIG:
        name = comp['display_name']
        emoji = comp['emoji']
        org_id = comp['org_id']
        
        msg_lines = [
            f"{emoji} *{name}* — 📊 *WEEKLY P&L & STOCK REPORT*",
            f"📅 *Period:* {period_str}",
            "=================================================="
        ]
        
        weekly_sales, weekly_costs, sales_cnt, cost_cnt = fetch_range_sales_and_purchases(access_token, org_id, start_str, end_str)
        weekly_net_pl = weekly_sales - weekly_costs
        
        accounts = get_chart_of_accounts(access_token, org_id)
        receivables_data = get_receivables_summary(access_token, org_id)
        payables_data = get_payables_summary(access_token, org_id)
        stock_val, neg_items = fetch_inventory_stock_data(access_token, org_id)
        
        bank_total = float(accounts.get('total_bank_balance', 0.0) or 0.0) + float(accounts.get('petty_cash', 0.0) or 0.0)
        rec_total = float(receivables_data.get('total_amount', 0.0) or receivables_data.get('total_balance', 0.0) or 0.0)
        pay_total = float(payables_data.get('total_amount', 0.0) or payables_data.get('total_balance', 0.0) or 0.0)
        
        net_financial_position = (stock_val + rec_total + bank_total) - pay_total
        
        msg_lines.append(f"📈 *Weekly Sales:* *{format_currency(weekly_sales)}* ({sales_cnt} invoices)")
        msg_lines.append(f"📋 *Weekly Costs/Purchases:* *{format_currency(weekly_costs)}* ({cost_cnt} items)")
        
        pl_status = "✅ Weekly Profit" if weekly_net_pl >= 0 else "⚠️ Weekly Loss"
        msg_lines.append(f"🧮 *WEEKLY NET P&L:* *{format_currency(weekly_net_pl)}* ({pl_status})")
        msg_lines.append("--------------------------------------------------")
        msg_lines.append(f"📦 *Stock Valuation:* *{format_currency(stock_val)}*")
        msg_lines.append(f"💰 *Bank & Cash Balance:* *{format_currency(bank_total)}*")
        msg_lines.append(f"📈 *Total Receivables:* *{format_currency(rec_total)}*")
        msg_lines.append(f"📋 *Total Payables:* *{format_currency(pay_total)}*")
        
        net_pos_status = "✅ Profit" if net_financial_position >= 0 else "⚠️ Deficit"
        msg_lines.append(f"⚖️ *Overall Net Financial Position:* *{format_currency(net_financial_position)}* ({net_pos_status})")
        
        if neg_items:
            neg_strs = [f"• {item_name}: *{qty:,.2f} units*" for item_name, qty in neg_items]
            msg_lines.append(f"⚠️ *Negative Stock Warning ({len(neg_items)} items):*\n  " + "\n  ".join(neg_strs))
        else:
            msg_lines.append("⚠️ *Negative Stock:* *None* ✅")
            
        msg_lines.append("==================================================")
        company_reports.append("\n".join(msg_lines))
        
    return company_reports


def generate_4company_monthly_pandl_report():
    """
    Generates 4-Company Monthly P&L & Stock Reports for 1st of month through last day of month.
    """
    now_ist = datetime.now(IST)
    first_date = now_ist.date().replace(day=1)
    last_date = now_ist.date()
    
    start_str = first_date.strftime("%Y-%m-%d")
    end_str = last_date.strftime("%Y-%m-%d")
    period_str = f"{first_date.strftime('%d %b %Y')} to {last_date.strftime('%d %b %Y')}"
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to generate 4-Company Monthly P&L Report: No valid Zoho access token.")
        return []

    company_reports = []
    
    for comp in COMPANIES_CONFIG:
        name = comp['display_name']
        emoji = comp['emoji']
        org_id = comp['org_id']
        
        msg_lines = [
            f"{emoji} *{name}* — 📊 *MONTHLY P&L & STOCK REPORT*",
            f"📅 *Period:* {period_str}",
            "=================================================="
        ]
        
        monthly_sales, monthly_costs, sales_cnt, cost_cnt = fetch_range_sales_and_purchases(access_token, org_id, start_str, end_str)
        monthly_net_pl = monthly_sales - monthly_costs
        
        accounts = get_chart_of_accounts(access_token, org_id)
        receivables_data = get_receivables_summary(access_token, org_id)
        payables_data = get_payables_summary(access_token, org_id)
        stock_val, neg_items = fetch_inventory_stock_data(access_token, org_id)
        
        bank_total = float(accounts.get('total_bank_balance', 0.0) or 0.0) + float(accounts.get('petty_cash', 0.0) or 0.0)
        rec_total = float(receivables_data.get('total_amount', 0.0) or receivables_data.get('total_balance', 0.0) or 0.0)
        pay_total = float(payables_data.get('total_amount', 0.0) or payables_data.get('total_balance', 0.0) or 0.0)
        
        net_financial_position = (stock_val + rec_total + bank_total) - pay_total
        
        msg_lines.append(f"📈 *Monthly Sales:* *{format_currency(monthly_sales)}* ({sales_cnt} invoices)")
        msg_lines.append(f"📋 *Monthly Costs/Purchases:* *{format_currency(monthly_costs)}* ({cost_cnt} items)")
        
        pl_status = "✅ Monthly Profit" if monthly_net_pl >= 0 else "⚠️ Monthly Loss"
        msg_lines.append(f"🧮 *MONTHLY NET P&L:* *{format_currency(monthly_net_pl)}* ({pl_status})")
        msg_lines.append("--------------------------------------------------")
        msg_lines.append(f"📦 *Stock Valuation:* *{format_currency(stock_val)}*")
        msg_lines.append(f"💰 *Bank & Cash Balance:* *{format_currency(bank_total)}*")
        msg_lines.append(f"📈 *Total Receivables:* *{format_currency(rec_total)}*")
        msg_lines.append(f"📋 *Total Payables:* *{format_currency(pay_total)}*")
        
        net_pos_status = "✅ Profit" if net_financial_position >= 0 else "⚠️ Deficit"
        msg_lines.append(f"⚖️ *Overall Net Financial Position:* *{format_currency(net_financial_position)}* ({net_pos_status})")
        
        if neg_items:
            neg_strs = [f"• {item_name}: *{qty:,.2f} units*" for item_name, qty in neg_items]
            msg_lines.append(f"⚠️ *Negative Stock Warning ({len(neg_items)} items):*\n  " + "\n  ".join(neg_strs))
        else:
            msg_lines.append("⚠️ *Negative Stock:* *None* ✅")
            
        msg_lines.append("==================================================")
        company_reports.append("\n".join(msg_lines))
        
    return company_reports


def generate_and_send_4company_weekly_pandl_report(recipient_phone: str = "917259510983@c.us") -> bool:
    """Dispatches the 4-Company Weekly P&L & Stock Reports every Saturday at 11:59 PM."""
    target = recipient_phone.strip()
    if not target.endswith("@c.us") and not target.endswith("@g.us"):
        target = f"{target}@c.us"
        
    logger.info(f"Generating 4-Company Weekly P&L & Stock Reports for {target}...")
    reports = generate_4company_weekly_pandl_report()
    if not reports:
        return False
        
    all_success = True
    for idx, report_text in enumerate(reports, 1):
        success = send_waha_message(target, report_text)
        if not success:
            all_success = False
        logger.info(f"Sent 4-Company Weekly P&L msg {idx}/{len(reports)} to {target}: {'Success' if success else 'Failed'}")
    return all_success


def generate_and_send_4company_monthly_pandl_report(recipient_phone: str = "917259510983@c.us") -> bool:
    """Dispatches the 4-Company Monthly P&L & Stock Reports on the last day of every month at 11:59 PM."""
    target = recipient_phone.strip()
    if not target.endswith("@c.us") and not target.endswith("@g.us"):
        target = f"{target}@c.us"
        
    logger.info(f"Generating 4-Company Monthly P&L & Stock Reports for {target}...")
    reports = generate_4company_monthly_pandl_report()
    if not reports:
        return False
        
    all_success = True
    for idx, report_text in enumerate(reports, 1):
        success = send_waha_message(target, report_text)
        if not success:
            all_success = False
        logger.info(f"Sent 4-Company Monthly P&L msg {idx}/{len(reports)} to {target}: {'Success' if success else 'Failed'}")
    return all_success


def generate_and_send_4company_pandl_report(recipient_phone: str = "917259510983@c.us") -> bool:
    """
    Generates and dispatches the 4-Company Daily P&L & Stock Reports (as separate WhatsApp messages per company) to target recipient.
    """
    target = recipient_phone.strip()
    if not target.endswith("@c.us") and not target.endswith("@g.us"):
        target = f"{target}@c.us"
        
    logger.info(f"Generating 4-Company Daily P&L & Stock Reports for {target}...")
    reports = generate_4company_pandl_report()
    if not reports:
        return False
        
    logger.info(f"Sending {len(reports)} company P&L reports separately to {target}...")
    all_success = True
    for idx, report_text in enumerate(reports, 1):
        success = send_waha_message(target, report_text)
        if not success:
            all_success = False
        logger.info(f"Sent 4-Company P&L msg {idx}/{len(reports)} to {target}: {'Success' if success else 'Failed'}")
    return all_success

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(generate_4company_pandl_report())
