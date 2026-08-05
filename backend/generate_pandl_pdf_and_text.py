import os
import requests
import re
import json
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from waha_service import send_waha_message, send_waha_file

def generate_pandl_pdf(title_date: str, rows_data: list, pdf_path: str = "Sunfra_PL_Report.pdf") -> str:
    """Generates a professional PDF report with the green P&L Summary table."""
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Title Style
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#004D40'),
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#555555'),
        alignment=1
    )
    
    story.append(Paragraph("<b>SUNFRA FARMS — PROFIT & LOSS REPORT</b>", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Period Date: {title_date}", subtitle_style))
    story.append(Spacer(1, 15))

    # Table Header & Data
    headers = ['Shead Name', 'Batch Age', 'Feed Cost', 'Labour Cost', 'Production', 'Egg Revenue', 'Profit']
    table_data = [[headers[0], headers[1], headers[2], headers[3], headers[4], headers[5], headers[6]]]
    
    tot_feed = 0.0
    tot_labour = 0.0
    tot_prod = 0.0
    tot_rev = 0.0
    tot_profit = 0.0
    
    for r in rows_data:
        feed_c = float(r.get("feed_cost", 0) or 0)
        labour_c = float(r.get("labour_cost", 0) or 0)
        prod = float(r.get("production", 0) or 0)
        rev = float(r.get("revenue", 0) or 0)
        profit = float(r.get("profit", 0) or 0)
        
        tot_feed += feed_c
        tot_labour += labour_c
        tot_prod += prod
        tot_rev += rev
        tot_profit += profit
        
        p_str = f"Rs. {profit:,.2f}" if profit >= 0 else f"-Rs. {abs(profit):,.2f}"
        
        row = [
            r.get("shead", ""),
            r.get("batch_age", "-"),
            f"Rs. {feed_c:,.0f}" if feed_c > 0 else "0",
            f"Rs. {labour_c:,.0f}" if labour_c > 0 else "0",
            f"{prod:,.2f}" if prod > 0 else "0",
            f"Rs. {rev:,.0f}" if rev > 0 else "0",
            p_str
        ]
        table_data.append(row)
        
    # Total Row
    tot_p_str = f"Rs. {tot_profit:,.2f}" if tot_profit >= 0 else f"-Rs. {abs(tot_profit):,.2f}"
    table_data.append(["TOTAL", "", f"Rs. {tot_feed:,.0f}", f"Rs. {tot_labour:,.0f}", f"{tot_prod:,.2f}", f"Rs. {tot_rev:,.0f}", tot_p_str])
    
    # Table Styling
    col_widths = [100, 70, 75, 75, 75, 80, 80]
    t = Table(table_data, colWidths=col_widths)
    
    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#137333')), # Dark green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        # Total Row Styling
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFEFEF')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ]
    
    # Alternating row colors
    for i in range(1, len(table_data) - 1):
        if i % 2 == 0:
            ts.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F9FBF9')))
            
    t.setStyle(TableStyle(ts))
    story.append(t)
    
    doc.build(story)
    print(f"PDF Generated Successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    today_str = now_ist.strftime("%Y-%m-%d")
    display_date = now_ist.strftime("%b %d, %Y")

    url_login = "https://sunfra.com/farm/sunfra/login/login.php"
    url_batch = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    })

    session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})

    # Fetch Batch Running Weeks
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
            pass

    # Fetch P&L Data
    url_pandl = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date=2026-08-01&to_date={today_str}&client_id=1"
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

    # 1. Build PDF Document
    pdf_file = f"Sunfra_PL_Report_{today_str}.pdf"
    generate_pandl_pdf(display_date, table_rows, pdf_file)

    # 2. Build Monospace / Clean Text Table
    text_table_lines = [
        f"📊 *Sunfra Farms P&L Summary on {display_date}*",
        "--------------------------------------------------",
        "```",
        f"{'Shead Name':<12} | {'Age':<7} | {'Feed Cost':<9} | {'Labour':<7} | {'Prod':<6} | {'Revenue':<9} | {'Profit':<9}",
        "-" * 72
    ]

    for r in table_rows:
        p_str = f"{r['profit']:,.0f}"
        text_table_lines.append(
            f"{r['shead']:<12} | {r['batch_age']:<7} | {r['feed_cost']:<9,.0f} | {r['labour_cost']:<7,.0f} | {r['production']:<6,.0f} | {r['revenue']:<9,.0f} | {p_str:<9}"
        )

    text_table_lines.extend([
        "-" * 72,
        f"{'TOTAL':<12} | {'':<7} | {tot_feed_cost:<9,.0f} | {tot_labour_cost:<7,.0f} | {tot_production:<6,.0f} | {tot_revenue:<9,.0f} | {tot_profit:<9,.0f}",
        "```",
        "--------------------------------------------------",
        f"• *OVERALL NET PROFIT / LOSS*: *Rs. {tot_profit:,.2f}* " + ("🟢" if tot_profit >= 0 else "🔴"),
        "✅ *Extracted live from sunfra.com (Read-Only)*"
    ])

    full_text_table = "\n".join(text_table_lines)
    print("\n=== GENERATED TEXT TABLE ===")
    print(full_text_table)

    # 3. Dispatch both PDF & Text Table to WhatsApp
    target_phone = "917259510983@c.us"
    
    # Send Text Table
    s_msg = send_waha_message(target_phone, full_text_table)
    print(f"Text Table Dispatch Status: {s_msg}")

    # Send PDF Document
    s_file = send_waha_file(target_phone, pdf_file, caption=f"📄 Sunfra Farms P&L Report ({display_date}).pdf")
    print(f"PDF File Dispatch Status: {s_file}")
