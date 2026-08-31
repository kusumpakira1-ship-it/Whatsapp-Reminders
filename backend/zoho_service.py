import os
import requests
import logging
from datetime import datetime, timezone, timedelta
from config import settings
from database import SessionLocal
from models import SystemSetting

logger = logging.getLogger(__name__)

domain_suffix = settings.ZOHO_DOMAIN.replace("zoho.", "")
ZOHO_ACCOUNTS_URL = f"https://accounts.zoho.{domain_suffix}"
ZOHO_BOOKS_API_URL = f"https://www.zohoapis.{domain_suffix}/books/v3"

def get_setting(key: str, default: str = "") -> str:
    db = SessionLocal()
    try:
        s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        return s.value if s and s.value else default
    except Exception as e:
        logger.error(f"Error fetching system setting '{key}': {e}")
        return default
    finally:
        db.close()

def save_setting(key: str, value: str):
    db = SessionLocal()
    try:
        s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if not s:
            s = SystemSetting(key=key, value=value)
            db.add(s)
        else:
            s.value = value
        db.commit()
    except Exception as e:
        logger.error(f"Error saving system setting '{key}': {e}")
    finally:
        db.close()

def get_zoho_auth_url(redirect_uri: str = None) -> str:
    """Returns the authorization URL for initial Zoho Books OAuth setup."""
    scope = "ZohoBooks.fullaccess.READ,ZohoBooks.settings.READ,ZohoBooks.banking.READ,ZohoBooks.reports.READ"
    r_uri = redirect_uri or settings.ZOHO_REDIRECT_URI or "http://localhost"
    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth?scope={scope}&client_id={settings.ZOHO_CLIENT_ID}&response_type=code&access_type=offline&redirect_uri={r_uri}&prompt=consent"
    return url

def exchange_grant_code(grant_code: str, redirect_uri: str = None) -> dict:
    """Exchanges 1-time grant code for permanent refresh_token and access_token."""
    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    r_uri = redirect_uri or settings.ZOHO_REDIRECT_URI or "http://localhost"
    params = {
        "grant_type": "authorization_code",
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "redirect_uri": r_uri,
        "code": grant_code.strip()
    }
    try:
        res = requests.post(url, data=params, timeout=30)
        data = res.json()
        if "refresh_token" in data:
            save_setting("zoho_refresh_token", data["refresh_token"])
            logger.info("Successfully saved permanent Zoho refresh_token!")
        if "access_token" in data:
            save_setting("zoho_access_token", data["access_token"])
        return data
    except Exception as e:
        logger.error(f"Error exchanging Zoho grant code: {e}")
        return {"error": str(e)}

def get_access_token() -> str:
    """Retrieves valid access_token, refreshing it if expired."""
    cached_access = get_setting("zoho_access_token")
    refresh_token = get_setting("zoho_refresh_token", os.getenv("ZOHO_REFRESH_TOKEN", ""))
    
    if not refresh_token:
        logger.warning("No Zoho refresh_token found. Please authorize Zoho Books OAuth.")
        return ""

    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": settings.ZOHO_CLIENT_ID,
        "client_secret": settings.ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    try:
        res = requests.post(url, data=params, timeout=30)
        data = res.json()
        if "access_token" in data:
            new_access = data["access_token"]
            save_setting("zoho_access_token", new_access)
            return new_access
        else:
            logger.error(f"Failed to refresh Zoho token: {data}")
            return cached_access
    except Exception as e:
        logger.error(f"Error calling Zoho token refresh API: {e}")
        return cached_access

def get_organization_id(access_token: str = None) -> str:
    """Auto-detects the primary Zoho Books Organization ID."""
    cached_org = get_setting("zoho_org_id")
    if cached_org:
        return cached_org
        
    if not access_token:
        access_token = get_access_token()
    if not access_token:
        return ""

    url = f"{ZOHO_BOOKS_API_URL}/organizations"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "organizations" in data and len(data["organizations"]) > 0:
            org_id = str(data["organizations"][0]["organization_id"])
            save_setting("zoho_org_id", org_id)
            logger.info(f"Detected Zoho Organization ID: {org_id}")
            return org_id
        else:
            logger.error(f"Failed to fetch Zoho organizations: {data}")
            return ""
    except Exception as e:
        logger.error(f"Error fetching Zoho organizations: {e}")
        return ""

def get_chart_of_accounts(access_token: str = None, org_id: str = None) -> dict:
    """Retrieves exact balances for Petty Cash, SBI Term Loan, Sunfra Farm OD, Sunfra Farms Bank, and Sunfra Indian Bank."""
    if not access_token:
        access_token = get_access_token()
    if not org_id:
        org_id = get_organization_id(access_token)
        
    accounts = {
        "petty_cash": 0.0,
        "farm_petty_cash": 0.0,
        "undeposited_funds": 0.0,
        "sbi_term_loan": 0.0,
        "sunfra_farm_od": 0.0,
        "sunfra_farms_bank": 0.0,
        "sunfra_indian_bank": 0.0,
        "sunfra_feeds_bank": 0.0,
        "total_bank_balance": 0.0,
        "details": []
    }
    if not access_token or not org_id:
        return accounts

    url = f"{ZOHO_BOOKS_API_URL}/bankaccounts?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "bankaccounts" in data:
            for acc in data["bankaccounts"]:
                acc_name = acc.get("account_name", "")
                balance = float(acc.get("bcy_balance", 0) or acc.get("balance", 0) or 0.0)
                name_lower = acc_name.lower()
                
                if "farm petty cash" in name_lower or "farm_petty_cash" in name_lower:
                    accounts["farm_petty_cash"] = balance
                elif "petty cash" in name_lower:
                    accounts["petty_cash"] = balance
                elif "undeposited" in name_lower:
                    accounts["undeposited_funds"] = balance
                elif "term loan" in name_lower:
                    accounts["sbi_term_loan"] = balance
                elif "od" in name_lower or "overdraft" in name_lower:
                    accounts["sunfra_farm_od"] = balance
                elif "indian bank" in name_lower:
                    accounts["sunfra_indian_bank"] = balance
                    accounts["total_bank_balance"] += balance
                elif "sunfra feeds" in name_lower or "feeds" in name_lower or "feed" in name_lower:
                    accounts["sunfra_feeds_bank"] = balance
                    accounts["total_bank_balance"] += balance
                elif "sunfra farms" in name_lower or "sunfra farm" in name_lower:
                    accounts["sunfra_farms_bank"] = balance
                    accounts["total_bank_balance"] += balance
                else:
                    accounts["total_bank_balance"] += balance
                    
                accounts["details"].append({"name": acc_name, "balance": balance})
    except Exception as e:
        logger.error(f"Error fetching Zoho bank accounts: {e}")
        
    return accounts

def get_egg_godown_stock(access_token: str = None, org_id: str = None) -> dict:
    """Queries item inventory stock for Egg Godown."""
    if not access_token:
        access_token = get_access_token()
    if not org_id:
        org_id = get_organization_id(access_token)
        
    if not access_token or not org_id:
        return {"total_eggs": 0, "total_trays": 0.0}

    url = f"{ZOHO_BOOKS_API_URL}/items?organization_id={org_id}&search_text=egg"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    stock_info = {"total_eggs": 0, "total_trays": 0.0, "items": []}
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "items" in data:
            for item in data["items"]:
                item_name = item.get("name", "")
                stock_on_hand = float(item.get("stock_on_hand", 0) or 0)
                unit = str(item.get("unit", "")).lower()
                
                trays = stock_on_hand if "tray" in unit else stock_on_hand / 30.0
                stock_info["total_trays"] += trays
                stock_info["items"].append({"name": item_name, "stock": stock_on_hand, "unit": unit})
            stock_info["total_eggs"] = int(stock_info["total_trays"] * 30)
    except Exception as e:
        logger.error(f"Error fetching Zoho egg stock inventory: {e}")

    return stock_info

def get_receivables_summary(access_token: str = None, org_id: str = None) -> dict:
    """Calculates total unpaid customer receivables count and balance."""
    if not access_token:
        access_token = get_access_token()
    if not org_id:
        org_id = get_organization_id(access_token)
        
    summary = {"count": 0, "total_amount": 0.0, "details": []}
    if not access_token or not org_id:
        return summary

    url = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org_id}&status=unpaid"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "invoices" in data:
            summary["count"] = len(data["invoices"])
            today_dt = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
            for inv in data["invoices"]:
                balance = float(inv.get("balance", 0) or 0.0)
                summary["total_amount"] += balance
                cust_name = str(inv.get("customer_name") or inv.get("company_name") or "Unknown Customer").strip()
                inv_date_str = str(inv.get("date") or inv.get("due_date") or "").strip()
                aging_days = 0
                if inv_date_str:
                    try:
                        inv_dt = datetime.strptime(inv_date_str[:10], "%Y-%m-%d").date()
                        aging_days = max(0, (today_dt - inv_dt).days)
                    except Exception:
                        pass
                summary["details"].append({
                    "customer_name": cust_name,
                    "balance": balance,
                    "date": inv_date_str,
                    "aging_days": aging_days
                })
            summary["details"].sort(key=lambda x: (x.get("aging_days", 0), x.get("balance", 0.0)), reverse=True)
    except Exception as e:
        logger.error(f"Error fetching Zoho receivables: {e}")
        
    return summary

def get_payables_summary(access_token: str = None, org_id: str = None) -> dict:
    """Calculates total unpaid vendor payables count and balance."""
    if not access_token:
        access_token = get_access_token()
    if not org_id:
        org_id = get_organization_id(access_token)
        
    summary = {"count": 0, "total_amount": 0.0, "details": []}
    if not access_token or not org_id:
        return summary

    url = f"{ZOHO_BOOKS_API_URL}/bills?organization_id={org_id}&status=unpaid"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "bills" in data:
            summary["count"] = len(data["bills"])
            today_dt = datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
            for bill in data["bills"]:
                balance = float(bill.get("balance", 0) or 0.0)
                summary["total_amount"] += balance
                v_name = str(bill.get("vendor_name") or bill.get("company_name") or "Unknown Vendor").strip()
                bill_date_str = str(bill.get("date") or bill.get("due_date") or "").strip()
                aging_days = 0
                if bill_date_str:
                    try:
                        bill_dt = datetime.strptime(bill_date_str[:10], "%Y-%m-%d").date()
                        aging_days = max(0, (today_dt - bill_dt).days)
                    except Exception:
                        pass
                summary["details"].append({
                    "vendor_name": v_name,
                    "balance": balance,
                    "date": bill_date_str,
                    "aging_days": aging_days
                })
            summary["details"].sort(key=lambda x: (x.get("aging_days", 0), x.get("balance", 0.0)), reverse=True)
    except Exception as e:
        logger.error(f"Error fetching Zoho payables: {e}")
        
    return summary

def get_today_zoho_sales_out(access_token: str = None, org_id: str = None) -> dict:
    """Calculates total sales quantity out and amount billed in Zoho Books today."""
    if not access_token:
        access_token = get_access_token()
    if not org_id:
        org_id = get_organization_id(access_token)
        
    result = {"total_trays_out": 0.0, "total_eggs_out": 0, "total_sales_amount": 0.0, "invoice_count": 0}
    if not access_token or not org_id:
        return result

    IST = timezone(timedelta(hours=5, minutes=30))
    today_str = datetime.now(IST).strftime("%Y-%m-%d")

    url = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org_id}&date={today_str}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=30)
        data = res.json()
        if res.status_code == 200 and "invoices" in data:
            invoices = data["invoices"]
            result["invoice_count"] = len(invoices)
            for inv in invoices:
                result["total_sales_amount"] += float(inv.get("total", 0) or 0.0)
                inv_id = inv.get("invoice_id")
                
                # Fetch line items for detailed quantities
                detail_url = f"{ZOHO_BOOKS_API_URL}/invoices/{inv_id}?organization_id={org_id}"
                detail_res = requests.get(detail_url, headers=headers, timeout=15).json()
                line_items = detail_res.get("invoice", {}).get("line_items", [])
                
                for item in line_items:
                    qty = float(item.get("quantity", 0) or 0.0)
                    unit = str(item.get("unit", "")).lower()
                    if "try" in unit or "tray" in unit:
                        result["total_trays_out"] += qty
                        result["total_eggs_out"] += int(qty * 30)
                    elif "egg" in unit or "pcs" in unit or "piece" in unit or qty > 100:
                        result["total_eggs_out"] += int(qty)
                        result["total_trays_out"] += (qty / 30.0)
    except Exception as e:
        logger.error(f"Error fetching today Zoho sales out: {e}")
        
    result["total_trays_out"] = round(result["total_trays_out"], 1)
    return result
