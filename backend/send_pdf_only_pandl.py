import os
import requests
import re
import json
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from waha_service import send_waha_file

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST)
yesterday_dt = now_ist - timedelta(days=1)
yesterday_str = yesterday_dt.strftime("%Y-%m-%d")
display_date = yesterday_dt.strftime("%b %d, %Y")

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_batch = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
url_pandl = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date={yesterday_str}&to_date={yesterday_str}&client_id=1"

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
    try:
        labels = json.loads(labels_m.group(1))
        weeks = json.loads(weeks_m.group(1))
        for l, w in zip(labels, weeks):
            clean_lbl = l.strip()
            if w and w > 0:
                batch_map[clean_lbl] = f"{w} W"
    except Exception as e:
        print("Error parsing batch arrays:", e)

# 3. Fetch P&L Data for Yesterday
res_pandl = session.get(url_pandl).json()
raw_data = res_pandl.get('data', [])

# Standard sections to ALWAYS include (including Grower 1)
ALWAYS_INCLUDE = {"Chick 1", "Egg Godown", "Feed Plant", "Gate Manager", "Grower 1", "Others", "Shead 1", "Shead 2", "Shead 3", "Shead 4", "Shead 5", "Shead 6", "Shead 7", "Shead 8", "Shead 9"}

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
    
    # Keep row if it's in ALWAYS_INCLUDE (like Grower 1) OR has non-zero total cost / prod / rev / profit
    if shead not in ALWAYS_INCLUDE and total_cost == 0 and production == 0 and revenue == 0 and profit == 0 and feed_cost == 0 and labour_cost == 0:
        continue
        
    batch_age = batch_map.get(shead, '-')
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

# 4. Generate PDF Document
os.makedirs("/app/media/reports", exist_ok=True)
pdf_path = f"/app/media/reports/Sunfra_PL_Report_{yesterday_str}.pdf"

doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#004D40'), alignment=1)
subtitle_style = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=11, leading=14, textColor=colors.HexColor('#555555'), alignment=1)

story.append(Paragraph("<b>SUNFRA FARMS — PROFIT & LOSS REPORT</b>", title_style))
story.append(Spacer(1, 6))
story.append(Paragraph(f"Period Date: {display_date}", subtitle_style))
story.append(Spacer(1, 15))

headers = ['Shead Name', 'Batch Age', 'Feed Cost', 'Labour Cost', 'Production', 'Egg Revenue', 'Profit']
table_data = [[headers[0], headers[1], headers[2], headers[3], headers[4], headers[5], headers[6]]]

for r in table_rows:
    p_str = f"Rs. {r['profit']:,.2f}" if r['profit'] >= 0 else f"-Rs. {abs(r['profit']):,.2f}"
    table_data.append([
        r['shead'],
        r['batch_age'],
        f"Rs. {r['feed_cost']:,.0f}" if r['feed_cost'] > 0 else "0",
        f"Rs. {r['labour_cost']:,.0f}" if r['labour_cost'] > 0 else "0",
        f"{r['production']:,.2f}" if r['production'] > 0 else "0",
        f"Rs. {r['revenue']:,.0f}" if r['revenue'] > 0 else "0",
        p_str
    ])

tot_p_str = f"Rs. {tot_profit:,.2f}" if tot_profit >= 0 else f"-Rs. {abs(tot_profit):,.2f}"
table_data.append(["TOTAL", "", f"Rs. {tot_feed_cost:,.0f}", f"Rs. {tot_labour_cost:,.0f}", f"{tot_production:,.2f}", f"Rs. {tot_revenue:,.0f}", tot_p_str])

t = Table(table_data, colWidths=[105, 70, 75, 75, 75, 80, 80])
ts = [
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#137333')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFEFEF')),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ('FONTSIZE', (0, -1), (-1, -1), 10),
    ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
    ('TOPPADDING', (0, -1), (-1, -1), 8),
]
for i in range(1, len(table_data) - 1):
    if i % 2 == 0:
        ts.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FBF9')))
t.setStyle(TableStyle(ts))
story.append(t)
doc.build(story)

# 5. Dispatch ONLY PDF to WhatsApp (No message text, no image)
target_phone = "917259510983@c.us"
res = send_waha_file(target_phone, pdf_path, caption=f"📄 Sunfra Farms P&L Report ({display_date}).pdf")
print("PDF ONLY DISPATCH RESULT:", res)
