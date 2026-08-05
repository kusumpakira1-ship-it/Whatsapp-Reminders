import os
import re
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from waha_service import send_waha_message, send_waha_file
from config import settings

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_pandl_pdf(title_date: str, rows_data: list, pdf_path: str) -> str:
    """Generates a professional PDF report with the green P&L Summary table and ₹ symbol."""
    
    font_reg = 'Helvetica'
    font_bold = 'Helvetica-Bold'

    for p, pb in [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf")
    ]:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont('RupeeFont', p))
                pdfmetrics.registerFont(TTFont('RupeeFontBold', pb if os.path.exists(pb) else p))
                font_reg = 'RupeeFont'
                font_bold = 'RupeeFontBold'
                break
            except Exception as e:
                logger.error(f"Error registering TTF font: {e}")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#004D40'),
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName=font_reg,
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#555555'),
        alignment=1
    )
    
    story.append(Paragraph("<b>SUNFRA FARMS — PROFIT & LOSS REPORT</b>", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Period Date: {title_date}", subtitle_style))
    story.append(Spacer(1, 15))

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
        
        p_str = f"₹ {profit:,.2f}" if profit >= 0 else f"-₹ {abs(profit):,.2f}"
        
        row = [
            r.get("shead", ""),
            r.get("batch_age", "-"),
            f"₹ {feed_c:,.0f}" if feed_c > 0 else "0",
            f"₹ {labour_c:,.0f}" if labour_c > 0 else "0",
            f"{prod:,.2f}" if prod > 0 else "0",
            f"₹ {rev:,.0f}" if rev > 0 else "0",
            p_str
        ]
        table_data.append(row)
        
    tot_p_str = f"₹ {tot_profit:,.2f}" if tot_profit >= 0 else f"-₹ {abs(tot_profit):,.2f}"
    table_data.append(["TOTAL", "", f"₹ {tot_feed:,.0f}", f"₹ {tot_labour:,.0f}", f"{tot_prod:,.2f}", f"₹ {tot_rev:,.0f}", tot_p_str])
    
    col_widths = [105, 70, 75, 75, 75, 80, 80]
    t = Table(table_data, colWidths=col_widths)
    
    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#137333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_bold),
        ('FONTNAME', (0, 1), (-1, -1), font_reg),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFEFEF')),
        ('FONTNAME', (0, -1), (-1, -1), font_bold),
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
    return pdf_path

def generate_and_send_sunfra_pandl_report(recipient_phone: str = "917259510983@c.us", target_date_str: str = None) -> bool:
    """Fetches P&L for a particular single day and Batch age from sunfra.com (Read-Only), generates PDF with ₹ symbol, and dispatches ONLY PDF to WhatsApp."""
    try:
        now_ist = datetime.now(IST)
        if not target_date_str:
            target_date_str = now_ist.strftime("%Y-%m-%d")
            
        dt_obj = datetime.strptime(target_date_str, "%Y-%m-%d")
        display_date = dt_obj.strftime("%b %d, %Y")

        url_login = "https://sunfra.com/farm/sunfra/login/login.php"
        url_batch = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
        url_pandl = f"https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json.php?from_date={target_date_str}&to_date={target_date_str}&client_id=1"

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        })

        session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'}, timeout=20)

        # Batch Age Mapping
        resp_batch = session.get(url_batch, timeout=20)
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
                logger.error(f"Error parsing batch json: {e}")

        # P&L Data
        res_pandl = session.get(url_pandl, timeout=20).json()
        raw_data = res_pandl.get('data', [])

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

        if not table_rows:
            logger.info("No P&L data rows found for today yet.")
            return False

        # 1. Generate PDF
        os.makedirs("/app/media/reports", exist_ok=True)
        pdf_file = f"/app/media/reports/Sunfra_PL_Report_{target_date_str}.pdf"
        generate_pandl_pdf(display_date, table_rows, pdf_file)

        # 2. Dispatch ONLY PDF file (No text message, no image)
        status = send_waha_file(recipient_phone, pdf_file, caption=f"📄 Sunfra Farms P&L Report ({display_date}).pdf")
        logger.info(f"Sunfra P&L PDF dispatched successfully to {recipient_phone}")
        return status
    except Exception as e:
        logger.error(f"Error generating Sunfra P&L report: {e}")
        return False
