import requests
from zoho_service import get_access_token

token = get_access_token()
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

print("=== CHECKING ZOHO.IN ORGANIZATIONS ===")
url_in = "https://www.zohoapis.in/books/v3/organizations"
res_in = requests.get(url_in, headers=headers).json()
print("zoho.in Orgs:", res_in)

print("=== CHECKING ZOHO.COM ORGANIZATIONS ===")
url_com = "https://www.zohoapis.com/books/v3/organizations"
res_com = requests.get(url_com, headers=headers).json()
print("zoho.com Orgs:", res_com)
