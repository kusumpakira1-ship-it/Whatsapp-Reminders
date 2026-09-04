import logging
import requests
from datetime import datetime, timezone, timedelta

try:
    from backend.config import settings
    from backend.waha_service import send_waha_message
except ImportError:
    from config import settings
    from waha_service import send_waha_message

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

LOGIN_URL = "https://sunfra.com/farm/sunfra/login/login.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest"
}

def get_authenticated_session():
    """Authenticates a requests session with sunfra.com."""
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get(LOGIN_URL, timeout=10)
        login_payload = {
            "username": "sunfra",
            "password": "Sunfra#321",
            "login": "Login"
        }
        session.post(LOGIN_URL, data=login_payload, timeout=10)
        return session
    except Exception as e:
        logger.error(f"Error authenticating with sunfra.com: {e}")
        return None

def parse_tray_loose_to_eggs(val_str):
    """Converts '572.15' -> 572 trays * 30 + 15 loose = 17175 eggs"""
    if not val_str:
        return 0
    parts = str(val_str).split('.')
    trays = int(parts[0]) if parts[0] else 0
    loose = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    return (trays * 30) + loose

def format_eggs_to_tray_loose(total_eggs):
    trays = total_eggs // 30
    loose = total_eggs % 30
    return f"{trays}.{loose:02d} Trays ({total_eggs:,} eggs)"

def generate_egg_production_crosscheck_report(target_date: str = None):
    """
    Cross-checks Supervisor Shed Production against Egg Godown Stock on sunfra.com.
    Returns the formatted text message for WhatsApp.
    """
    if not target_date:
        now_ist = datetime.now(IST)
        target_date_str = now_ist.strftime("%Y-%m-%d")
        display_date_str = now_ist.strftime("%d %b %Y")
    else:
        target_date_str = target_date
        display_date_str = datetime.strptime(target_date, "%Y-%m-%d").strftime("%d %b %Y")

    session = get_authenticated_session()
    if not session:
        return (
            "⚠️ *Egg Production Cross-Check Alert*\n\n"
            "Unable to connect to sunfra.com to fetch shed production and godown stock data."
        )

    url_sup = f"https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json.php?date={target_date_str}&client_id=1"
    url_godown = f"https://sunfra.com/farm/sunfra/egg_godown/egg_godown_stock_json.php?date={target_date_str}&client_id=1"

    try:
        r_sup = session.get(url_sup, timeout=15)
        sup_json = r_sup.json() if r_sup.status_code == 200 else {}
    except Exception as e:
        logger.error(f"Error fetching supervisor production from {url_sup}: {e}")
        sup_json = {}

    try:
        r_godown = session.get(url_godown, timeout=15)
        godown_json = r_godown.json() if r_godown.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error fetching egg godown stock from {url_godown}: {e}")
        godown_json = []

    # 1. Parse Supervisor Shed Production
    sup_records = {}
    sup_list = sup_json.get('1', []) if isinstance(sup_json, dict) else (sup_json if isinstance(sup_json, list) else [])
    for it in sup_list:
        ts = it.get('timestamp', '')
        if ts.startswith(target_date_str):
            s_raw = it.get('sheadNo', '').replace('_', ' ').strip().title()
            trays = int(it.get('no_of_trays', 0) or 0)
            loose = int(it.get('no_of_loose_eggs', 0) or 0)
            prod_eggs = int(it.get('production', 0) or ((trays * 30) + loose))
            sup_records[s_raw] = {
                'trays': trays,
                'loose': loose,
                'total_eggs': prod_eggs
            }

    # 2. Parse Egg Godown Receipts
    godown_records = {}
    if isinstance(godown_json, list):
        for it in godown_json:
            s_raw = it.get('shead_name', '').strip().title()
            good_eggs = parse_tray_loose_to_eggs(it.get('Good'))
            small_eggs = parse_tray_loose_to_eggs(it.get('Small'))
            big_eggs = parse_tray_loose_to_eggs(it.get('Big'))
            dmg_eggs = parse_tray_loose_to_eggs(it.get('Damaged'))
            total_godown_eggs = good_eggs + small_eggs + big_eggs + dmg_eggs
            godown_records[s_raw] = {
                'good_eggs': good_eggs,
                'small_eggs': small_eggs,
                'big_eggs': big_eggs,
                'dmg_eggs': dmg_eggs,
                'total_eggs': total_godown_eggs
            }

    all_sheds = sorted(set(list(sup_records.keys()) + list(godown_records.keys())))
    if not all_sheds:
        return (
            "🥚 *Egg Production vs Godown Stock Cross-Check*\n"
            f"📅 *Date:* {display_date_str}\n"
            "==================================================\n\n"
            "ℹ️ *No shed production or godown entries found for today yet.*"
        )

    matched_lines = []
    mismatched_lines = []

    for shed in all_sheds:
        s_data = sup_records.get(shed)
        g_data = godown_records.get(shed)

        s_eggs = s_data['total_eggs'] if s_data else 0
        g_eggs = g_data['total_eggs'] if g_data else 0
        diff = g_eggs - s_eggs

        if diff == 0 and s_eggs > 0:
            matched_lines.append(f"• 🏠 *{shed}*: *{format_eggs_to_tray_loose(s_eggs)}* — ✅ *Match*")
        elif s_data and not g_data:
            mismatched_lines.append(
                f"• 🏠 *{shed}*: ❌ *Missing in Godown*\n"
                f"  - Supervisor: *{format_eggs_to_tray_loose(s_eggs)}*\n"
                f"  - Godown: *0.00 Trays (Not recorded)*"
            )
        elif not s_data and g_data:
            mismatched_lines.append(
                f"• 🏠 *{shed}*: ❌ *Not reported by Supervisor*\n"
                f"  - Supervisor: *0.00 Trays (Not reported)*\n"
                f"  - Godown: *{format_eggs_to_tray_loose(g_eggs)}*"
            )
        else:
            diff_trays = diff / 30.0
            mismatched_lines.append(
                f"• 🏠 *{shed}*: ❌ *Mismatch*\n"
                f"  - Supervisor: *{format_eggs_to_tray_loose(s_eggs)}*\n"
                f"  - Godown: *{format_eggs_to_tray_loose(g_eggs)}*\n"
                f"  - Variance: *{diff:+d} eggs ({diff_trays:+.2f} trays)*"
            )

    msg_parts = [
        "🥚 *Egg Production vs Godown Stock Cross-Check*",
        f"📅 *Date:* {display_date_str}",
        "=================================================="
    ]

    if mismatched_lines:
        msg_parts.append(f"🚨 *Alert: {len(mismatched_lines)} Sheds Mismatch / Pending in Godown!*\n")
        msg_parts.append("🔴 *Mismatched Sheds:*")
        msg_parts.append("\n\n".join(mismatched_lines))
    else:
        msg_parts.append("🎉 *All Sheds Matched Successfully!* ✅\n")

    if matched_lines:
        msg_parts.append("--------------------------------------------------")
        msg_parts.append(f"🟢 *Matched Sheds ({len(matched_lines)} Sheds):*")
        msg_parts.append("\n".join(matched_lines))

    return "\n".join(msg_parts)

def generate_and_send_egg_production_crosscheck_report(recipient_phone: str = "917259510983@c.us", target_date: str = None) -> bool:
    """Generates the cross-check report and dispatches via WAHA."""
    target = recipient_phone.strip()
    if not target.endswith("@c.us") and not target.endswith("@g.us"):
        target = f"{target}@c.us"

    logger.info(f"Generating Egg Production vs Godown Stock Cross-Check Report for {target}...")
    report_text = generate_egg_production_crosscheck_report(target_date=target_date)
    success = send_waha_message(target, report_text)
    logger.info(f"Egg Production Cross-Check Report sent to {target}: {'Success' if success else 'Failed'}")
    return success
