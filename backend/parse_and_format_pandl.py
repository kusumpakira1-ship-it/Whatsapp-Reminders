import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST)
today_str = now_ist.strftime("%Y-%m-%d")
display_date = now_ist.strftime("%d %b %Y")

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_api = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date=2026-08-01&to_date={today_str}&client_id=1"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

# Login
session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
res = session.get(url_api).json()

all_rows = res.get('data', [])
print(f"Total Rows Extracted from Website: {len(all_rows)}")

# Filter out empty rows
clean_rows = []
total_feed_cost = 0.0
total_labour_cost = 0.0
total_expense = 0.0
total_production = 0.0
total_revenue = 0.0
total_profit = 0.0

for r in all_rows:
    shead = r.get('shead_name', '').strip()
    feed_used = float(r.get('feed_used', 0) or 0)
    feed_cost = float(r.get('feed_cost', 0) or 0)
    medicine = float(r.get('medicine', 0) or 0)
    other = float(r.get('other_cost', 0) or 0)
    labour = float(r.get('labour_cost', 0) or 0)
    tot_cost = float(r.get('total', 0) or 0)
    prod = float(r.get('production', 0) or 0)
    rev = float(r.get('total_egg_revenue', 0) or 0)
    profit = float(r.get('profit', 0) or 0)
    
    # Check if row is empty (no cost and no production and no revenue)
    if tot_cost == 0 and prod == 0 and rev == 0 and profit == 0 and feed_cost == 0 and labour == 0:
        continue  # DELETE / SKIP EMPTY ROW
        
    clean_rows.append({
        'shead': shead,
        'feed_cost': feed_cost,
        'medicine': medicine,
        'labour': labour,
        'tot_cost': tot_cost,
        'prod': prod,
        'rev': rev,
        'profit': profit
    })
    
    total_feed_cost += feed_cost
    total_labour_cost += labour
    total_expense += tot_cost
    total_production += prod
    total_revenue += rev
    total_profit += profit

print(f"Active Non-Empty Rows Count: {len(clean_rows)}")

# Format WhatsApp Message
msg_lines = [
    "📊 *SUNFRA FARMS — PROFIT & LOSS REPORT*",
    f"📅 *Period:* 01 Aug 2026 to {display_date}",
    "--------------------------------------------------",
    "🏢 *SHED-WISE P&L SUMMARY (Empty Rows Removed)*:\n"
]

for item in clean_rows:
    p_status = "🟢 Profit" if item['profit'] >= 0 else "🔴 Loss"
    msg_lines.append(
        f"• *{item['shead']}*:\n"
        f"  └ Total Cost: *Rs. {item['tot_cost']:,.2f}* | Production: *{item['prod']:,.0f} Eggs*\n"
        f"  └ Revenue: *Rs. {item['rev']:,.2f}* | Net: *Rs. {item['profit']:,.2f}* ({p_status})\n"
    )

msg_lines.extend([
    "--------------------------------------------------",
    "📈 *TOTAL OVERALL P&L SUMMARY*:",
    f"• Total Feed Cost: *Rs. {total_feed_cost:,.2f}*",
    f"• Total Labour Cost: *Rs. {total_labour_cost:,.2f}*",
    f"• Total Operating Expenses: *Rs. {total_expense:,.2f}*",
    f"• Total Egg Production: *{total_production:,.0f} Eggs*",
    f"• Total Egg Revenue: *Rs. {total_revenue:,.2f}*",
    f"• *NET OVERALL PROFIT / LOSS*: *Rs. {total_profit:,.2f}* " + ("🟢" if total_profit >= 0 else "🔴"),
    "--------------------------------------------------",
    "✅ *Extracted live from sunfra.com (Read-Only)*"
])

report_text = "\n".join(msg_lines)
print("\n=== FORMATTED WHATSAPP REPORT ===")
print(report_text)
