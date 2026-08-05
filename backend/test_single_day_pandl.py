import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(IST).strftime("%Y-%m-%d")

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_api = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date={today}&to_date={today}&client_id=1"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
resp_api = session.get(url_api)
print(f"Single Day Today ({today}) API Status:", resp_api.status_code)
print("API Response Text:\n", resp_api.text)
