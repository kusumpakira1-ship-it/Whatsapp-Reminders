import requests
import re
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST)
today_str = now_ist.strftime("%Y-%m-%d")
display_date = now_ist.strftime("%b %d, %Y")

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_batch = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

# 1. Login
session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})

# 2. Fetch Running Weeks from Batch Section
resp_batch = session.get(url_batch)
batch_html = resp_batch.text

batch_map = {}
labels_m = re.search(r'const\s+shedLabels\s*=\s*(\[.*?\]);', batch_html)
weeks_m = re.search(r'const\s+runningWeeksData\s*=\s*(\[.*?\]);', batch_html)

if labels_m and weeks_m:
    import json
    try:
        labels = json.loads(labels_m.group(1))
        weeks = json.loads(weeks_m.group(1))
        for l, w in zip(labels, weeks):
            clean_lbl = l.strip()
            batch_map[clean_lbl] = f"{w} Weeks" if w and w > 0 else ""
    except Exception as e:
        print("Error parsing batch arrays:", e)

print("=== EXTRACTED BATCH RUNNING WEEKS MAP ===")
for k, v in batch_map.items():
    print(f"  • {k}: {v if v else '(None)'}")

# 3. Fetch P&L Data from Profit & Loss Summary
url_pandl = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date=2026-08-01&to_date={today_str}&client_id=1"
res_pandl = session.get(url_pandl).json()
raw_data = res_pandl.get('data', [])

# 4. Build Table matching Reference Image:
# Columns: [Shead Name, Batch Age, Feed Cost, Labour Cost, Production, Egg Revenue, Profit]
# EXCLUDED: Medicine, Other Cost
# EXCLUDED: Empty Rows (where cost, revenue, and production are 0)

table_rows = []
tot_feed_cost = 0.0
tot_labour_cost = 0.0
tot_production = 0.0
tot_revenue = 0.0
tot_profit = 0.0

for r in raw_data:
    shead = r.get('shead_name', '').strip()
    feed_cost = float(r.get('feed_cost', 0) or 0)
    labour_cost = float(r.get('labour_cost', 0) or 0)
    production = float(r.get('production', 0) or 0)
    revenue = float(r.get('total_egg_revenue', 0) or 0)
    total_cost = float(r.get('total', 0) or 0)
    profit = float(r.get('profit', 0) or 0)
    
    # Delete empty rows (where total cost == 0, production == 0, revenue == 0, profit == 0)
    if total_cost == 0 and production == 0 and revenue == 0 and profit == 0 and feed_cost == 0 and labour_cost == 0:
        continue
        
    batch_age = batch_map.get(shead, '')
    
    table_rows.append({
        'shead': shead,
        'batch_age': batch_age,
        'feed_cost': feed_cost,
        'labour_cost': labour_cost,
        'production': production,
        'revenue': revenue,
        'profit': profit
    })
    
    tot_feed_cost += feed_cost
    tot_labour_cost += labour_cost
    tot_production += production
    tot_revenue += revenue
    tot_profit += profit

# 5. Format WhatsApp Markdown Table Report
msg = [
    f"📊 *Sunfra Farms P&L Summary on {display_date}*",
    "--------------------------------------------------",
    "| *Shead Name* | *Batch Age* | *Feed Cost* | *Labour Cost* | *Production* | *Egg Revenue* | *Profit/Loss* |",
    "--------------------------------------------------"
]

for r in table_rows:
    p_str = f"Rs. {r['profit']:,.2f}" if r['profit'] >= 0 else f"-Rs. {abs(r['profit']):,.2f}"
    age_str = r['batch_age'] if r['batch_age'] else "-"
    msg.append(
        f"• *{r['shead']}* ({age_str})\n"
        f"  └ Feed: *Rs. {r['feed_cost']:,.0f}* | Labour: *Rs. {r['labour_cost']:,.0f}*\n"
        f"  └ Prod: *{r['production']:,.0f} Eggs* | Rev: *Rs. {r['revenue']:,.0f}*\n"
        f"  └ Net Profit: *{p_str}* ({'🟢' if r['profit']>=0 else '🔴'})"
    )

msg.extend([
    "--------------------------------------------------",
    "📈 *TOTAL SUMMARY*:",
    f"• Total Feed Cost: *Rs. {tot_feed_cost:,.2f}*",
    f"• Total Labour Cost: *Rs. {tot_labour_cost:,.2f}*",
    f"• Total Egg Production: *{tot_production:,.0f} Eggs*",
    f"• Total Egg Revenue: *Rs. {tot_revenue:,.2f}*",
    f"• *OVERALL NET PROFIT / LOSS*: *Rs. {tot_profit:,.2f}* " + ("🟢" if tot_profit >= 0 else "🔴"),
    "--------------------------------------------------",
    "✅ *Extracted live from sunfra.com (Read-Only)*"
])

print("\n=== GENERATED WHATSAPP REPORT ===")
print("\n".join(msg))
