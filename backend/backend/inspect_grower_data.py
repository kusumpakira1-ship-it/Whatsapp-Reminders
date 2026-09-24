import requests

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_pandl = "https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date=2026-08-01&to_date=2026-08-04&client_id=1"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
res = session.get(url_pandl).json()

print("=== ALL SHEDS IN P&L DATA ===")
for r in res.get('data', []):
    print(f"• {r.get('shead_name')}: feed={r.get('feed_cost')} labour={r.get('labour_cost')} prod={r.get('production')} rev={r.get('total_egg_revenue')} profit={r.get('profit')}")
