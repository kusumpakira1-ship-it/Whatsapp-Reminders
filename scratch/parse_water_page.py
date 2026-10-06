import requests, re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

resp = requests.get("https://sunfra.com/farm/sunfra/sensor/water_flow_for_farm.php", headers=headers, timeout=20)
html = resp.text

table_match = re.search(r'<table.*?>.*?</table>', html, re.DOTALL | re.IGNORECASE)
if table_match:
    t = table_match.group(0)
    rows = re.findall(r'<tr.*?>(.*?)</tr>', t, re.DOTALL | re.IGNORECASE)
    for r in rows:
        cols = re.findall(r'<td.*?>(.*?)</td>', r, re.DOTALL | re.IGNORECASE)
        clean_cols = [re.sub(r'<.*?>', '', c).strip() for c in cols]
        if clean_cols:
            print(clean_cols)
