import sys
import requests
import json

client_id = '1000.B9KFRFFVSCJ0SN1DJ0PCZEFK4P5ANE'
client_secret = '67726abb28b0e5b870d2996106d02c8047f7610f4e'
org_id = '904503869'

def exchange(code):
    code = code.strip()
    if not code.startswith('1000.') and code.startswith('000.'):
        code = '1' + code
    print(f"Attempting exchange with code: {code[:12]}...")
    url = 'https://accounts.zoho.com/oauth/v2/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code
    }
    res = requests.post(url, data=data, timeout=10)
    print("Response:", res.json())
    return res.json()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        exchange(sys.argv[1])
