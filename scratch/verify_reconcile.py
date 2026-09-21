import sys

sys.path.append('backend')
from zoho_4company_pandl import fetch_4company_pandl

sys.stdout.reconfigure(encoding='utf-8')

print("================ ZOHO RECONCILIATION CHECK FOR SUNFRA FARMS (16 SEP 2026) ================")
res = fetch_4company_pandl(as_of_date="2026-09-16")

farms_data = res.get("companies", {}).get("Sunfra Farms", {})

print("Sunfra Farms Zoho Data:")
print("  • Petty Cash (Zoho):", farms_data.get("petty_cash", 0))
print("  • Total Bank & Cash (Zoho):", farms_data.get("bank_balance", 0))

physical_petty = 156501.00
physical_bank = 1128661.04

print("\nMahalakshmi Physical Data (sent at 7:38 PM in Accounts Poultry):")
print("  • Petty Cash (Physical):", physical_petty)
print("  • Bank (Physical):", physical_bank)
print("  • Total Bank & Cash (Physical):", physical_petty + physical_bank)

diff = abs((physical_petty + physical_bank) - farms_data.get("bank_balance", 0))
print(f"\nVariance / Difference: Rs. {diff:,.2f}")
if diff < 1.0:
    print("✅ PERFECT MATCH 100%! Physical balance and Zoho Books match exactly!")
else:
    print(f"❌ Discrepancy: {diff}")
