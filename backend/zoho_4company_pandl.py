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
    get_payables_summary,
    zoho_get
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

def fetch_inventory_asset_from_balancesheet(access_token: str, org_id: str) -> float:
    url = f"{ZOHO_BOOKS_API_URL}/reports/balancesheet?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    try:
        res = zoho_get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            return 0.0
        data = res.json()
        
        def find_inventory(node):
            if isinstance(node, dict):
                name = str(node.get('name') or node.get('account_name') or '').strip().lower()
                if 'inventory asset' in name or name == 'inventory' or name == 'stock':
                    val = node.get('total') or node.get('balance') or node.get('amount') or 0.0
                    return float(val)
                for k, v in node.items():
                    res_val = find_inventory(v)
                    if res_val is not None:
                        return res_val
            elif isinstance(node, list):
                for item in node:
                    res_val = find_inventory(item)
                    if res_val is not None:
                        return res_val
            return None

        val = find_inventory(data)
        return val if val is not None else 0.0
    except Exception as e:
        logger.error(f"Error fetching balance sheet inventory asset for org {org_id}: {e}")
        return 0.0


def fetch_balance_sheet_cash_and_equivalents(access_token: str, org_id: str):
    """
    Fetches the exact 'Total for Cash and Cash Equivalents' directly from the Zoho Books Balance Sheet report (Cash total + Bank total).
    """
    url = f"{ZOHO_BOOKS_API_URL}/reports/balancesheet?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    totals = {"cash": 0.0, "bank": 0.0}
    try:
        res = zoho_get(url, headers=headers, timeout=20)
        if res.status_code == 200:
            bs = res.json()
            def extract(node):
                if isinstance(node, dict):
                    n = (node.get("name") or node.get("account_name") or "").lower().strip()
                    t = float(node.get("total", 0) or node.get("balance", 0) or node.get("amount", 0) or 0.0)
                    if n == "cash":
                        totals["cash"] = t
                    elif n == "bank":
                        totals["bank"] = t
                    for k, v in node.items():
                        if isinstance(v, (dict, list)):
                            extract(v)
                elif isinstance(node, list):
                    for item in node:
                        extract(item)
            extract(bs)
    except Exception as e:
        logger.error(f"Error fetching balance sheet cash & bank for org {org_id}: {e}")
        
    tot = totals["cash"] + totals["bank"]
    return tot, totals["cash"], totals["bank"]


def fetch_inventory_stock_data(access_token: str, org_id: str):
    """
    Fetches Inventory Asset balance from Zoho Books Balance Sheet API as stock valuation,
    and detects items with physical negative Stock on Hand.
    """
    inv_asset_value = fetch_inventory_asset_from_balancesheet(access_token, org_id)
    url = f"{ZOHO_BOOKS_API_URL}/items?organization_id={org_id}&per_page=200"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    total_stock_value = 0.0
    negative_items = []
    
    try:
        page = 1
        has_more = True
        while has_more and page <= 5:
            res = zoho_get(f"{url}&page={page}", headers=headers, timeout=15)
            if res.status_code != 200:
                break
                
            data = res.json()
            items = data.get("items", [])
            for it in items:
                stock_on_hand = float(it.get("stock_on_hand", 0.0) or 0.0)
                rate = float(it.get("purchase_rate", 0.0) or it.get("rate", 0.0) or 0.0)
                
                if stock_on_hand > 0:
                    total_stock_value += (stock_on_hand * rate)
                elif stock_on_hand < 0:
                    negative_items.append((it.get("name", "Unknown Item"), stock_on_hand))
                    
            page_context = data.get("page_context", {})
            has_more = page_context.get("has_more_page", False)
            page += 1
    except Exception as e:
        logger.error(f"Exception fetching inventory stock for org {org_id}: {e}")
        
    final_stock_valuation = inv_asset_value if inv_asset_value > 0 else total_stock_value
    return final_stock_valuation, negative_items


def fetch_egg_stock_count(access_token: str, org_id: str):
    """
    Calculates Egg Stock quantity directly from the main 'EGGS' item on hand.
    """
    url = f"{ZOHO_BOOKS_API_URL}/items?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    total_eggs = 0.0
    main_found = False
    try:
        page = 1
        has_more = True
        while has_more and page <= 5:
            res = zoho_get(f"{url}&page={page}", headers=headers, timeout=12)
            if res.status_code != 200:
                break
            data = res.json()
            items = data.get("items", [])
            for it in items:
                name_u = (it.get("name", "") or "").upper().strip()
                unit = (it.get("unit", "") or "").upper().strip()
                stock = float(it.get("actual_available_stock", 0.0) or it.get("stock_on_hand", 0.0) or 0.0)
                
                # Priority 1: Main 'EGGS' item
                if name_u == 'EGGS':
                    count = stock * 30 if ('TRY' in unit or 'TRAY' in unit) else stock
                    total_eggs = count
                    main_found = True
                    break
                elif not main_found:
                    is_egg = ('EGG' in name_u or (name_u.startswith('SHEAD') and 'FEED' not in name_u)) and ('CONSUMPTION' not in name_u and 'TRANSPORT' not in name_u and 'TRAY' not in name_u)
                    if is_egg and stock != 0:
                        count = stock * 30 if ('TRY' in unit or 'TRAY' in unit) else stock
                        total_eggs += count
            if main_found:
                break
            has_more = data.get("page_context", {}).get("has_more_page", False)
            page += 1
    except Exception as e:
        logger.error(f"Error fetching egg stock count for org {org_id}: {e}")
    return total_eggs


def fetch_historical_net_positions(access_token: str, org_id: str, today_net_pos: float, today_date_str: str):
    """
    Calculates historical Net Positions for: today, -1 day, -2 days, -1 week, -2 weeks, -1 month, -2 months, -1 year.
    """
    try:
        today_dt = datetime.strptime(today_date_str, "%Y-%m-%d").date()
    except Exception:
        today_dt = datetime.now(IST).date()
        
    intervals = [
        ("-1 Day", 1),
        ("-2 Days", 2),
        ("-1 Week", 7),
        ("-2 Weeks", 14),
        ("-1 Month", 30),
        ("-2 Months", 60),
        ("-1 Year", 365)
    ]
    
    today_formatted = today_dt.strftime("%d %b")
    historical = [(f"Today ({today_formatted})", today_net_pos)]
    for label, days_back in intervals:
        target_dt = today_dt - timedelta(days=days_back)
        date_formatted = target_dt.strftime("%d %b %Y") if days_back >= 365 else target_dt.strftime("%d %b")
        display_label = f"{label} ({date_formatted})"
        
        start_str = target_dt.strftime("%Y-%m-%d")
        end_str = today_dt.strftime("%Y-%m-%d")
        sales, purch, _, _ = fetch_range_sales_and_purchases(access_token, org_id, start_str, end_str)
        net_change = sales - purch
        past_net = today_net_pos - net_change
        historical.append((display_label, past_net))
        
    return historical


def fetch_today_sales_and_purchases(access_token: str, org_id: str, today_date_str: str):
    """
    Fetches Today's Total Sales (Invoices generated today) and
    Today's Total Costs (Bills & Expenses recorded today) for a specific org ID,
    along with itemized breakdowns.
    """
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    today_sales = 0.0
    today_purchases = 0.0
    sales_list = []
    purch_list = []
    
    try:
        # 1. Today's Invoices (Sales)
        url_inv = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org_id}&date_start={today_date_str}&date_end={today_date_str}"
        res_inv = zoho_get(url_inv, headers=headers, timeout=20)
        if res_inv.status_code == 200:
            invs = res_inv.json().get("invoices", [])
            for i in invs:
                cust = i.get("customer_name") or "Customer"
                no = i.get("invoice_number") or ""
                amt = float(i.get("total", 0) or 0.0)
                sales_list.append((cust, no, amt))
                today_sales += amt

        # 2. Today's Bills (Purchases)
        url_bill = f"{ZOHO_BOOKS_API_URL}/bills?organization_id={org_id}&date_start={today_date_str}&date_end={today_date_str}"
        res_bill = zoho_get(url_bill, headers=headers, timeout=20)
        if res_bill.status_code == 200:
            bills = res_bill.json().get("bills", [])
            for b in bills:
                vend = b.get("vendor_name") or "Vendor"
                no = b.get("bill_number") or ""
                amt = float(b.get("total", 0) or 0.0)
                purch_list.append((vend, no, amt))
                today_purchases += amt

        # 3. Today's Expenses
        url_exp = f"{ZOHO_BOOKS_API_URL}/expenses?organization_id={org_id}&date_start={today_date_str}&date_end={today_date_str}"
        res_exp = zoho_get(url_exp, headers=headers, timeout=20)
        if res_exp.status_code == 200:
            exps = res_exp.json().get("expenses", [])
            for e in exps:
                vend = e.get("vendor_name") or e.get("biller_name") or e.get("account_name") or "Expense"
                no = e.get("reference_number") or e.get("expense_id") or ""
                amt = float(e.get("total", 0) or e.get("amount", 0) or e.get("biller_amount", 0) or 0.0)
                purch_list.append((vend, no, amt))
                today_purchases += amt
    except Exception as e:
        logger.error(f"Error fetching today sales/purchases for org {org_id}: {e}")
        
    return today_sales, today_purchases, len(sales_list), len(purch_list), sales_list, purch_list


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
        company_key = comp.get('key', '')
        name = comp['display_name']
        emoji = comp['emoji']
        org_id = comp['org_id']
        
        msg_lines = [
            f"{emoji} *{name}* — 📊 *DAILY P&L & STOCK REPORT*",
            f"📅 *Date:* {display_date_str}",
            "=================================================="
        ]
        
        # 1. Fetch Today's Daily Sales & Costs
        today_sales, today_costs, sales_cnt, cost_cnt, sales_list, purch_list = fetch_today_sales_and_purchases(access_token, org_id, today_date_str)
        today_daily_pl = today_sales - today_costs
        
        # 2. Fetch Overall Balances & Inventory Stock Data
        accounts = get_chart_of_accounts(access_token, org_id)
        receivables_data = get_receivables_summary(access_token, org_id)
        payables_data = get_payables_summary(access_token, org_id)
        stock_val, neg_items = fetch_inventory_stock_data(access_token, org_id)
        
        bank_total, bs_cash, bs_bank = fetch_balance_sheet_cash_and_equivalents(access_token, org_id)
        rec_total = float(receivables_data.get('total_amount', 0.0) or receivables_data.get('total_balance', 0.0) or 0.0)
        pay_total = float(payables_data.get('total_amount', 0.0) or payables_data.get('total_balance', 0.0) or 0.0)
        
        # Overall Net Position = (Stock + Receivables + Bank) - Payables
        net_financial_position = (stock_val + rec_total + bank_total) - pay_total
        
        msg_lines.append(f"📦 *Stock Valuation:* *{format_currency(stock_val)}*")
        
        # Add Egg Stock right below Stock Valuation (highlight with red emoji if > 2.5 Lakhs)
        egg_stock_count = fetch_egg_stock_count(access_token, org_id)
        if egg_stock_count > 0 or company_key == 'farms':
            lakhs = egg_stock_count / 100000.0
            highlight = " 🔴" if egg_stock_count > 250000 else ""
            msg_lines.append(f"  • *Egg Stock:* *{lakhs:.2f} Lakhs eggs* ({int(egg_stock_count):,} eggs){highlight}")
            
        msg_lines.append(f"💰 *Bank & Cash Balance:* *{format_currency(bank_total)}*")
        msg_lines.append(f"📈 *Total Receivables:* *{format_currency(rec_total)}*")
        msg_lines.append(f"📋 *Total Payables:* *{format_currency(pay_total)}*")
        
        net_pos_status = "✅ Profit" if net_financial_position >= 0 else "⚠️ Deficit"
        msg_lines.append(f"⚖️ *Overall Net Financial Position:* *{format_currency(net_financial_position)}* ({net_pos_status})")
        
        # Net Position Historical Breakdown: today, -1 day, -2 days, -1 week, -2 weeks, -1 month, -2 months, -1 year
        hist_positions = fetch_historical_net_positions(access_token, org_id, net_financial_position, today_date_str)
        hist_lines = [f"  • {lbl}: *{format_currency(pos)}*" for lbl, pos in hist_positions]
        msg_lines.append("📊 *Net Position Breakdown (History):*\n" + "\n".join(hist_lines))
        
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
        res_inv = zoho_get(url_inv, headers=headers, timeout=25)
        if res_inv.status_code == 200:
            invs = res_inv.json().get("invoices", [])
            sales_count = len(invs)
            total_sales = sum(float(i.get("total", 0) or 0.0) for i in invs)

        url_bill = f"{ZOHO_BOOKS_API_URL}/bills?organization_id={org_id}&date_start={start_date_str}&date_end={end_date_str}"
        res_bill = zoho_get(url_bill, headers=headers, timeout=25)
        if res_bill.status_code == 200:
            bills = res_bill.json().get("bills", [])
            purch_count += len(bills)
            total_purchases += sum(float(b.get("total", 0) or 0.0) for b in bills)

        url_exp = f"{ZOHO_BOOKS_API_URL}/expenses?organization_id={org_id}&date_start={start_date_str}&date_end={end_date_str}"
        res_exp = zoho_get(url_exp, headers=headers, timeout=25)
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
        
        bank_total, bs_cash, bs_bank = fetch_balance_sheet_cash_and_equivalents(access_token, org_id)
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
        
        bank_total, bs_cash, bs_bank = fetch_balance_sheet_cash_and_equivalents(access_token, org_id)
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
