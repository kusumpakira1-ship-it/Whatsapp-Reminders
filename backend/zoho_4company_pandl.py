import logging
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
        'key': 'indus',
        'display_name': 'Indus Poultry Equipments Pvt Ltd',
        'emoji': '🏭',
        'org_id': '893416886'
    },
    {
        'key': 'farms',
        'display_name': 'Sunfra Farms',
        'emoji': '🌾',
        'org_id': '905812487'
    },
    {
        'key': 'feeds',
        'display_name': 'Sunfra Feeds',
        'emoji': '🏭',
        'org_id': '932776276'
    },
    {
        'key': 'corporate',
        'display_name': 'Sunfra Corporate',
        'emoji': '🏢',
        'org_id': '929124131'
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


def format_currency(val):
    v = float(val or 0.0)
    if v < 0:
        return f"-Rs. {abs(v):,.2f}"
    return f"Rs. {v:,.2f}"


def generate_4company_pandl_report():
    """
    Generates the consolidated 4-Company P&L and Inventory Stock Asset Report
    based on the formula: Net Position = (Stock + Receivables + Bank) - Payables
    """
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%d %b %Y, %I:%M %p")
    
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to generate 4-Company P&L Report: No valid Zoho access token.")
        return None

    msg_lines = [
        "📊 *4-COMPANY DAILY P&L & INVENTORY ASSET REPORT*",
        f"📅 *Date:* {today_str}",
        "=================================================="
    ]
    
    for comp in COMPANIES_CONFIG:
        name = comp['display_name']
        emoji = comp['emoji']
        org_id = comp['org_id']
        
        # 1. Fetch Zoho Balances & Data
        accounts = get_chart_of_accounts(access_token, org_id)
        receivables_data = get_receivables_summary(access_token, org_id)
        payables_data = get_payables_summary(access_token, org_id)
        stock_val, neg_items = fetch_inventory_stock_data(access_token, org_id)
        
        # Extract totals
        bank_total = float(accounts.get('total_bank_balance', 0.0) or 0.0) + float(accounts.get('petty_cash', 0.0) or 0.0)
        rec_total = float(receivables_data.get('total_balance', 0.0) or 0.0)
        pay_total = float(payables_data.get('total_balance', 0.0) or 0.0)
        
        # Calculate Net Position: (Stock + Receivables + Bank) - Payables
        net_position = (stock_val + rec_total + bank_total) - pay_total
        
        msg_lines.append(f"{emoji} *{name}*")
        msg_lines.append(f"💰 *Bank & Cash:* *{format_currency(bank_total)}*")
        msg_lines.append(f"📈 *Receivables:* *{format_currency(rec_total)}*")
        msg_lines.append(f"📦 *Stock Valuation:* *{format_currency(stock_val)}*")
        msg_lines.append(f"📋 *Payables:* *{format_currency(pay_total)}*")
        
        # Negative Stock Items warning
        if neg_items:
            neg_strs = [f"• {item_name}: *{qty:,.2f} units*" for item_name, qty in neg_items[:5]]
            msg_lines.append(f"⚠️ *Negative Stock Warning ({len(neg_items)} items):*\n  " + "\n  ".join(neg_strs))
            if len(neg_items) > 5:
                msg_lines.append(f"  *(+ {len(neg_items) - 5} other negative stock items)*")
        else:
            msg_lines.append("⚠️ *Negative Stock:* *None* ✅")
            
        msg_lines.append("--------------------------------------------------")
        net_status = "✅ Profit" if net_position >= 0 else "⚠️ Loss / Deficit"
        msg_lines.append(f"🧮 *Net Position (P&L):* *{format_currency(net_position)}* ({net_status})")
        msg_lines.append("==================================================")
        
    return "\n".join(msg_lines)


def generate_and_send_4company_pandl_report(recipient_phone: str = "917259510983@c.us") -> bool:
    """
    Generates and dispatches the 4-Company Daily P&L & Stock Report to target recipient.
    """
    target = recipient_phone.strip()
    if not target.endswith("@c.us") and not target.endswith("@g.us"):
        target = f"{target}@c.us"
        
    logger.info(f"Generating 4-Company Daily P&L & Stock Report for {target}...")
    report_text = generate_4company_pandl_report()
    if not report_text:
        return False
        
    logger.info(f"Sending 4-Company P&L report to {target}...")
    success = send_waha_message(target, report_text)
    return success

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(generate_4company_pandl_report())
