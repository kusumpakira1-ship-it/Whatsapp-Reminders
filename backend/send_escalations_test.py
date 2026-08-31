import asyncio
import sys

# Ensure the repository root is in sys.path for imports
repo_root = r"c:\\Users\\sunfra\\Desktop\\Whatsapp Reminders"
if repo_root not in sys.path:
    sys.path.append(repo_root)

# Import the WAHA helper that actually sends a text message
from backend.waha_service import send_waha_message

# Test recipient – the number you asked for
TEST_RECIPIENTS = ["183300681367688@lid"]

# Four escalation messages (pre‑formatted exactly as you provided)
ESCALATION_MESSAGES = {
    "Ai iOT Team": "🚨 *Company‑Wise Escalation Report (EOD Summary)*\n📅 *Date:* 26 Aug 2026\n\n1️⃣ *Ai iOT Team Reports:* (❌ 1 Failed)\n• Balaji (Approval Task): *Report Review & Approval* - ❌\n• Ai iOT Team: *Daily Work Update* - ✅\n\n🚨 *Total Failed: 2*",
    "Corporate Company": "🚨 *Company‑Wise Escalation Report (EOD Summary)*\n📅 *Date:* 26 Aug 2026\n\n2️⃣ *Corporate Company (P&L) Reports:* (✅ All 6 Passed)\n• Sunfra Corporate P&L: *Daily Purchases* - ✅\n• Sunfra Corporate P&L: *Daily Sales* - ✅\n• Sunfra Corporate P&L: *Day Book* - ✅\n• Sunfra Corporate P&L: *Each Sales P&L* - ✅\n• Sunfra Corporate P&L: *Total Payables* - ✅\n• Sunfra Corporate P&L: *Total Receivables* - ✅\n\n🚨 *Total Failed: 1*",
    "Sunfra Feeds": "🚨 *Company‑Wise Escalation Report (EOD Summary)*\n📅 *Date:* 26 Aug 2026\n\n3️⃣ *Sunfra Feed Tasks & Reports:* (❌ 3 Failed)\n• Summary - Sunfra Feeds: *Day Book* - ❌\n• Raw Material Prices & Orders: *Stock/Website Updates* - ✅\n• Summary - Sunfra Feeds: *Daily Purchases* - ✅\n• Summary - Sunfra Feeds: *Daily Sales* - ✅\n• Summary - Sunfra Feeds: *Each Sales P&L* - ❌\n• Summary - Sunfra Feeds: *Total Payables* - ✅\n• Summary - Sunfra Feeds: *Total Receivables* - ✅\n• Sunfra Feed Plant: *Silo Empty and Cleaning* - ❌\n\n🚨 *Total Failed: 7*",
    "Sunfra Farms": "🚨 *Company‑Wise Escalation Report (EOD Summary)*\n📅 *Date:* 26 Aug 2026\n\n4️⃣ *Sunfra Farms Tasks & Reports:* (❌ 3 Failed)\n• Sunfra P&L: *Profit & Loss Summary* - ❌\n• Accounts Poultry: *CA Statement* - ✅\n• Accounts Poultry: *Daily Purchases* - ✅\n• Accounts Poultry: *Daily Sales* - ✅\n• Accounts Poultry: *Day Book* - ✅\n• Accounts Poultry: *Each Sales P&L* - ❌\n• Accounts Poultry: *Total Payables* - ✅\n• Accounts Poultry: *Total Receivables* - ✅\n• Rule Book: *Rule Book Updates* - ❌\n\n🚨 *Total Failed: 9*"
}

async def send_all():
    """Send each escalation message to the test recipient via WAHA."""
    for _, msg in ESCALATION_MESSAGES.items():
        for recipient in TEST_RECIPIENTS:
            # Send the full message with emojis
            send_waha_message(recipient, msg)

if __name__ == "__main__":
    asyncio.run(send_all())
