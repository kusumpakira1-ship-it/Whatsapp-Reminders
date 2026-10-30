import requests
import json

refresh_token = '1000.7c59fea5714f993ac878b37d256e3783.aa78348ecdeb3f906d825cbc130f0d6b'
client_id = '1000.B9KFRFFVSCJ0SN1DJ0PCZEFK4P5ANE'
client_secret = '67726abb28b0e5b870d2996106d02c8047f7610f4e'

url = 'https://accounts.zoho.com/oauth/v2/token'
params = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'client_id': client_id,
    'client_secret': client_secret
}

res = requests.post(url, data=params, timeout=10)
data = res.json()
print("Refresh test result:", data)
assert 'access_token' in data, "Failed to refresh token!"
print("Token refresh works perfectly!")
