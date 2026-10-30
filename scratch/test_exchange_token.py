import requests
import json

client_id = '1000.B9KFRFFVSCJ0SN1DJ0PCZEFK4P5ANE'
client_secret = '67726abb28b0e5b870d2996106d02c8047f7610f4e'
codes = [
    '1000.593ae12c4c0dc4e8cc3b8828ca2ce104.625ae5f5a2feb36d3b6f764faae8e6a1',
    '000.593ae12c4c0dc4e8cc3b8828ca2ce104.625ae5f5a2feb36d3b6f764faae8e6a1'
]

print("Starting exchange test...", flush=True)
url = 'https://accounts.zoho.com/oauth/v2/token'
for c in codes:
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': c
    }
    try:
        res = requests.post(url, data=data, timeout=10)
        print(f"Code prefix {c[:8]}: status={res.status_code}, response={res.text}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
