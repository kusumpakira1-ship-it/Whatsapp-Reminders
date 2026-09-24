import requests
from zoho_service import get_access_token, ZOHO_BOOKS_API_URL

token = get_access_token()
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

url = f"{ZOHO_BOOKS_API_URL}/organizations"
res = requests.get(url, headers=headers).json()

print("=== ALL ZOHO ORGANIZATIONS FOR YOUR ACCOUNT ===")
orgs = res.get('organizations', [])
print(f"Total Organizations Found: {len(orgs)}")
for o in orgs:
    print(f"• Org ID: {o.get('organization_id')} | Name: '{o.get('name')}' | Currency: {o.get('currency_code')} | Role: {o.get('user_role')}")
