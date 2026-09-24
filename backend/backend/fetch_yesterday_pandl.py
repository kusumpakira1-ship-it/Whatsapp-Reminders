import os
import requests
import re
import json
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from waha_service import send_waha_message, send_waha_file

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

# 3. Fetch P&L Data for Yesterday (Aug 04, 2026)
res_pandl = session.get(url_pandl).json()
raw_data = res_pandl.get('data', [])

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
    
    # Delete empty rows (where total cost == 0, production == 0, revenue == 0, profit == 0)
    if total_cost == 0 and production == 0 and revenue == 0 and profit == 0 and feed_cost == 0 and labour_cost == 0:
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

print(f"Extracted {len(table_rows)} active rows for Yesterday ({display_date}).")

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
print("PDF Generated:", pdf_path)

# 5. Generate PNG Table Image
img_path = f"/app/media/reports/Sunfra_PL_Table_{yesterday_str}.png"
cols = [
    {"name": "Shead Name", "width": 140, "align": "left"},
    {"name": "Batch Age", "width": 110, "align": "center"},
    {"name": "Feed Cost", "width": 110, "align": "right"},
    {"name": "Labour Cost", "width": 110, "align": "right"},
    {"name": "Production", "width": 120, "align": "right"},
    {"name": "Egg Revenue", "width": 120, "align": "right"},
    {"name": "Profit", "width": 110, "align": "right"}
]
table_w = sum(c["width"] for c in cols)
row_h, title_h, head_h = 36, 44, 40
table_h = title_h + head_h + ((len(table_rows) + 1) * row_h)

img = Image.new("RGB", (table_w, table_h), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

try:
    f_title = ImageFont.truetype("arial.ttf", 20)
    f_head = ImageFont.truetype("arialbd.ttf", 16)
    f_body = ImageFont.truetype("arial.ttf", 15)
    f_bold = ImageFont.truetype("arialbd.ttf", 15)
except Exception:
    f_title = f_head = f_body = f_bold = ImageFont.load_default()

draw.rectangle([0, 0, table_w, title_h], fill=(15, 95, 40))
draw.text(((table_w - 220) / 2, 10), f"Sunfra Farms on {display_date}", fill=(255, 255, 255), font=f_title)

y = title_h
draw.rectangle([0, y, table_w, y + head_h], fill=(19, 115, 51))
x = 0
for col in cols:
    draw.text((x + 10, y + 10), col["name"], fill=(255, 255, 255), font=f_head)
    x += col["width"]

y += head_h
for idx, r in enumerate(table_rows):
    bg = (245, 248, 245) if idx % 2 == 1 else (255, 255, 255)
    draw.rectangle([0, y, table_w, y + row_h], fill=bg)
    vals = [
        r['shead'], r['batch_age'],
        f"{r['feed_cost']:,.0f}" if r['feed_cost']>0 else "0",
        f"{r['labour_cost']:,.0f}" if r['labour_cost']>0 else "0",
        f"{r['production']:,.2f}" if r['production']>0 else "0",
        f"{r['revenue']:,.0f}" if r['revenue']>0 else "0",
        f"{r['profit']:,.0f}"
    ]
    x = 0
    for v_str, col in zip(vals, cols):
        draw.text((x + 10, y + 9), v_str, fill=(0, 0, 0), font=f_body)
        x += col["width"]
    y += row_h

draw.rectangle([0, y, table_w, y + row_h], fill=(240, 240, 240))
draw.text((table_w - 220, y + 9), "Total", fill=(0, 0, 0), font=f_bold)
draw.text((table_w - 100, y + 9), f"{tot_profit:,.0f}", fill=(0, 0, 0), font=f_bold)

# Grid lines
for hy in range(title_h, table_h + 1, row_h):
    draw.line([(0, hy), (table_w, hy)], fill=(180, 180, 180), width=1)
vx = 0
for col in cols:
    draw.line([(vx, title_h), (vx, table_h)], fill=(180, 180, 180), width=1)
    vx += col["width"]

img.save(img_path)
print("Image Generated:", img_path)

# 6. Build Monospace Text Table
text_lines = [
    f"📊 *Sunfra Farms P&L Summary on {display_date} (Yesterday)*",
    "--------------------------------------------------",
    "```",
    f"{'Shead Name':<12} | {'Age':<7} | {'Feed Cost':<9} | {'Labour':<7} | {'Prod':<6} | {'Revenue':<9} | {'Profit':<9}",
    "-" * 72
]

for r in table_rows:
    p_str = f"{r['profit']:,.0f}"
    text_lines.append(
        f"{r['shead']:<12} | {r['batch_age']:<7} | {r['feed_cost']:<9,.0f} | {r['labour_cost']:<7,.0f} | {r['production']:<6,.0f} | {r['revenue']:<9,.0f} | {p_str:<9}"
    )

text_lines.extend([
    "-" * 72,
    f"{'TOTAL':<12} | {'':<7} | {tot_feed_cost:<9,.0f} | {tot_labour_cost:<7,.0f} | {tot_production:<6,.0f} | {tot_revenue:<9,.0f} | {tot_profit:<9,.0f}",
    "```",
    "--------------------------------------------------",
    f"• *OVERALL NET PROFIT / LOSS*: *Rs. {tot_profit:,.2f}* " + ("🟢" if tot_profit >= 0 else "🔴"),
    "✅ *Extracted live from sunfra.com (Read-Only)*"
])

full_text = "\n".join(text_lines)

# 7. Dispatch to WhatsApp
target_phone = "917259510983@c.us"
send_waha_message(target_phone, full_text)
send_waha_file(target_phone, pdf_path, caption=f"📄 Sunfra Farms P&L Report — {display_date}.pdf")
send_waha_file(target_phone, img_path, caption=f"📊 Sunfra Farms P&L Table — {display_date}.png")

print("YESTERDAY'S REPORT DISPATCHED SUCCESSFULLY!")
