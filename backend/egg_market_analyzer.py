import os
import re
import json
import logging
from datetime import datetime, timezone, timedelta
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from database import SessionLocal
from models import RawMessage
from waha_service import send_waha_file, send_waha_message
from ai_processor import _call_ai

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))

def parse_market_rates_from_messages(today_msgs, yesterday_msgs):
    """Parses real WhatsApp messages strictly enforcing today's date for today's egg prices."""
    egg_prices_map = {}
    loading_map = {}
    paper_map = {}

    # 1. Parse TODAY's egg prices ONLY from today_msgs!
    for m in today_msgs:
        text = m.raw_text or ''
        msg_hour = m.timestamp.hour
        is_egg_msg = ('egg' in text.lower() or 'closing' in text.lower() or 'ppr rate' in text.lower() or 'veh kol' in text.lower()) and 'godown' not in text.lower()
        if is_egg_msg:
            slot = 'morning' if msg_hour < 12 else 'afternoon' if msg_hour < 17 else 'evening'
            for line in text.split('\n'):
                match = re.search(r'^([A-Za-z\s\(\)]+):?\s*(\d{3})$', line.strip())
                if match:
                    mkt = match.group(1).strip().upper()
                    val = int(match.group(2))
                    if mkt not in egg_prices_map:
                        egg_prices_map[mkt] = {'morning': None, 'afternoon': None, 'evening': None}
                    if egg_prices_map[mkt][slot] is None:
                        egg_prices_map[mkt][slot] = val

    # 2. Extract Loading & Paper Rates from today_msgs + yesterday_msgs
    all_rate_msgs = today_msgs + yesterday_msgs
    for m in all_rate_msgs:
        text = m.raw_text or ''
        if 'loading rates' in text.lower() or 'paper rates' in text.lower():
            lines = text.split('\n')
            current_sec = None
            for line in lines:
                l_lower = line.strip().lower()
                if 'loading rates' in l_lower:
                    current_sec = 'loading'
                    continue
                elif 'paper rates' in l_lower:
                    current_sec = 'paper'
                    continue

                match = re.search(r'([A-Za-z\s\(\)]+):\s*(\d+)(?:\s*\(([-\d]+)\))?', line)
                if match and current_sec:
                    mkt = match.group(1).strip().upper()
                    today_val = int(match.group(2))
                    diff_val = int(match.group(3)) if match.group(3) else 0
                    yesterday_val = today_val - diff_val

                    target = loading_map if current_sec == 'loading' else paper_map
                    if mkt not in target:
                        target[mkt] = {'today': today_val, 'yesterday': yesterday_val, 'change': diff_val}

    # Format into list output
    egg_prices_list = []
    for mkt, slots in egg_prices_map.items():
        egg_prices_list.append({
            "market": mkt,
            "morning": slots['morning'],
            "afternoon": slots['afternoon'],
            "evening": slots['evening']
        })

    loading_rates_list = []
    for mkt, vals in loading_map.items():
        loading_rates_list.append({
            "market": mkt,
            "yesterday": vals['yesterday'],
            "today": vals['today']
        })

    paper_rates_list = []
    for mkt, vals in paper_map.items():
        paper_rates_list.append({
            "market": mkt,
            "yesterday": vals['yesterday'],
            "today": vals['today']
        })

    return {
        "egg_prices": egg_prices_list,
        "loading_rates": loading_rates_list,
        "paper_rates": paper_rates_list
    }

def calculate_market_analysis(data):
    # 1. Egg Price Movement
    egg_rows = []
    for item in data.get("egg_prices", []):
        mkt = item.get("market")
        m = item.get("morning")
        a = item.get("afternoon")
        e = item.get("evening")
        
        status = ""
        symbol = "🔵"
        
        if m is not None and a is not None and e is not None:
            if a < m and e > a:
                diff = e - a
                status = f'<font color="#d97706"><b>Recovered (+{diff})</b></font>'
                symbol = "🟡"
            elif e > m:
                diff = e - m
                status = f'<font color="#16a34a"><b>Increased (+{diff})</b></font>'
                symbol = "🟢"
            elif e < m:
                diff = m - e
                status = f'<font color="#dc2626"><b>Decreased (-{diff})</b></font>'
                symbol = "🔴"
            else:
                status = '<font color="#2563eb"><b>Stable</b></font>'
                symbol = "🔵"
        elif m is None and a is not None and e is not None:
            diff = e - a
            if diff > 0:
                status = f'<font color="#16a34a"><b>Increased (+{diff})</b></font>'
                symbol = "🟢"
            elif diff < 0:
                status = f'<font color="#dc2626"><b>Decreased ({diff})</b></font>'
                symbol = "🔴"
            else:
                status = '<font color="#2563eb"><b>Stable</b></font>'
                symbol = "🔵"
        elif a is None and m is not None and e is not None:
            diff = e - m
            if diff > 0:
                status = f'<font color="#16a34a"><b>Increased (+{diff})</b></font>'
                symbol = "🟢"
            elif diff < 0:
                status = f'<font color="#dc2626"><b>Decreased ({diff})</b></font>'
                symbol = "🔴"
            else:
                status = '<font color="#2563eb"><b>Stable</b></font>'
                symbol = "🔵"
        elif e is None and m is not None and a is not None:
            diff = a - m
            if diff > 0:
                status = f'<font color="#16a34a"><b>Increased (+{diff})</b></font>'
                symbol = "🟢"
            elif diff < 0:
                status = f'<font color="#dc2626"><b>Decreased ({diff})</b></font>'
                symbol = "🔴"
            else:
                status = '<font color="#2563eb"><b>Stable</b></font>'
                symbol = "🔵"
        else:
            status = '<font color="#2563eb"><b>Stable</b></font>'
            symbol = "🔵"

        egg_rows.append({
            "market": mkt,
            "morning": str(m) if m is not None else "—",
            "afternoon": str(a) if a is not None else "—",
            "evening": str(e) if e is not None else "—",
            "status": status,
            "symbol": symbol,
            "latest_price": e if e is not None else a if a is not None else m
        })

    # 2. Loading Rates
    loading_rows = []
    for item in data.get("loading_rates", []):
        mkt = item.get("market")
        y = item.get("yesterday")
        t = item.get("today")
        change = (t - y) if (t is not None and y is not None) else 0
        if change > 0:
            status = f'<font color="#16a34a"><b>Increased (+{change})</b></font>'
        elif change < 0:
            status = f'<font color="#dc2626"><b>Decreased ({change})</b></font>'
        else:
            status = '<font color="#2563eb"><b>Stable</b></font>'

        loading_rows.append({
            "market": mkt,
            "yesterday": str(y) if y is not None else "—",
            "today": str(t) if t is not None else "—",
            "change": str(change),
            "status": status,
            "diff_num": change
        })

    # 3. Paper Rates
    paper_rows = []
    for item in data.get("paper_rates", []):
        mkt = item.get("market")
        y = item.get("yesterday")
        t = item.get("today")
        change = (t - y) if (t is not None and y is not None) else 0
        if change > 0:
            status = f'<font color="#16a34a"><b>Increased (+{change})</b></font>'
        elif change < 0:
            status = f'<font color="#dc2626"><b>Decreased ({change})</b></font>'
        else:
            status = '<font color="#2563eb"><b>Stable</b></font>'

        paper_rows.append({
            "market": mkt,
            "yesterday": str(y) if y is not None else "—",
            "today": str(t) if t is not None else "—",
            "change": str(change),
            "status": status,
            "diff_num": change
        })

    # 4. Combined Market View
    all_mkts = []
    for row in egg_rows:
        if row["market"] not in all_mkts: all_mkts.append(row["market"])
    for row in loading_rows:
        if row["market"] not in all_mkts: all_mkts.append(row["market"])
    for row in paper_rows:
        if row["market"] not in all_mkts: all_mkts.append(row["market"])

    combined_rows = []
    for mkt in all_mkts:
        e_info = next((r for r in egg_rows if r["market"] == mkt), None)
        l_info = next((r for r in loading_rows if r["market"] == mkt), None)
        p_info = next((r for r in paper_rows if r["market"] == mkt), None)

        egg_str = e_info["latest_price"] if e_info and e_info["latest_price"] is not None else "—"
        
        load_str = "—"
        if l_info and l_info["today"] != "—":
            load_str = f"{l_info['today']} ({l_info['diff_num']})"
            
        paper_str = "—"
        if p_info and p_info["today"] != "—":
            paper_str = f"{p_info['today']} ({p_info['diff_num']})"

        parts = []
        status_color = "🔵"
        if e_info:
            e_stat_clean = re.sub(r'<[^>]*>', '', e_info["status"]).split(" (")[0]
            parts.append(f"Egg {e_stat_clean}")
            if "Decreased" in e_info["status"]: status_color = "🔴"
            elif "Recovered" in e_info["status"] and status_color != "🔴": status_color = "🟡"
            elif "Increased" in e_info["status"] and status_color not in ["🔴", "🟡"]: status_color = "🟢"

        if l_info:
            if l_info["diff_num"] < 0:
                parts.append("Loading &darr;")
                if status_color not in ["🔴"]: status_color = "🟡"
            elif l_info["diff_num"] > 0:
                parts.append("Loading &uarr;")
            else:
                parts.append("Loading Stable")

        if p_info:
            if p_info["diff_num"] < 0:
                parts.append("Paper &darr;")
            elif p_info["diff_num"] > 0:
                parts.append("Paper &uarr;")
            else:
                parts.append("Paper Stable")

        overall_status_text = " &bull; ".join(parts)
        if status_color == "🔴":
            overall_status_text = f'<font color="#dc2626"><b>{overall_status_text}</b></font>'
        elif status_color == "🟡":
            overall_status_text = f'<font color="#d97706"><b>{overall_status_text}</b></font>'
        elif status_color == "🟢":
            overall_status_text = f'<font color="#16a34a"><b>{overall_status_text}</b></font>'
        else:
            overall_status_text = f'<font color="#2563eb"><b>{overall_status_text}</b></font>'

        combined_rows.append({
            "market": mkt,
            "egg_price": str(egg_str),
            "loading": load_str,
            "paper": paper_str,
            "overall_status": overall_status_text
        })

    return {
        "egg_rows": egg_rows,
        "loading_rows": loading_rows,
        "paper_rows": paper_rows,
        "combined_rows": combined_rows
    }

def generate_egg_market_pdf(analysis, pdf_path, report_date_str):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1b4332'),
        alignment=0,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#40916c'),
        spaceAfter=12
    )
    section_title_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1b4332'),
        spaceBefore=10,
        spaceAfter=6
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2b2b2b')
    )
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    story = []
    story.append(Paragraph("Egg Price & Market Analysis Report", title_style))
    story.append(Paragraph(f"Date: {report_date_str} | Generated automatically from Team Group messages", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2d6a4f'), spaceBefore=0, spaceAfter=12))
    
    # ── Section 1: Egg Price Movement Analysis ──
    story.append(Paragraph("1. Egg Price Movement Analysis", section_title_style))
    story.append(Paragraph("Compares Morning &rarr; Afternoon &rarr; Evening prices across regional markets.", subtitle_style))
    
    table1_data = [[
        Paragraph("<b>Market</b>", header_cell_style),
        Paragraph("<b>Morning</b>", header_cell_style),
        Paragraph("<b>Afternoon</b>", header_cell_style),
        Paragraph("<b>Evening</b>", header_cell_style),
        Paragraph("<b>Status</b>", header_cell_style)
    ]]
    
    for row in analysis["egg_rows"]:
        table1_data.append([
            Paragraph(row["market"], table_cell_style),
            Paragraph(row["morning"], table_cell_style),
            Paragraph(row["afternoon"], table_cell_style),
            Paragraph(row["evening"], table_cell_style),
            Paragraph(row["status"], table_cell_style)
        ])
        
    t1 = Table(table1_data, colWidths=[100, 90, 90, 90, 160])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b4332')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2d6a4f')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))
    
    # ── Section 2: Loading & Paper Rate Analysis ──
    story.append(Paragraph("2. Loading & Paper Rate Analysis", section_title_style))
    story.append(Paragraph("Compares today's Loading and Paper rates with previous day's rates.", subtitle_style))
    
    # Loading Table
    story.append(Paragraph("Loading Rates", ParagraphStyle('SubSub', parent=section_title_style, fontSize=10, textColor=colors.HexColor('#2d6a4f'))))
    table2a_data = [[
        Paragraph("<b>Market</b>", header_cell_style),
        Paragraph("<b>Yesterday</b>", header_cell_style),
        Paragraph("<b>Today</b>", header_cell_style),
        Paragraph("<b>Change</b>", header_cell_style),
        Paragraph("<b>Status</b>", header_cell_style)
    ]]
    for row in analysis["loading_rows"]:
        table2a_data.append([
            Paragraph(row["market"], table_cell_style),
            Paragraph(row["yesterday"], table_cell_style),
            Paragraph(row["today"], table_cell_style),
            Paragraph(row["change"], table_cell_style),
            Paragraph(row["status"], table_cell_style)
        ])
    t2a = Table(table2a_data, colWidths=[100, 90, 90, 90, 160])
    t2a.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2d6a4f')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2a)
    story.append(Spacer(1, 10))
    
    # Paper Table
    story.append(Paragraph("Paper Rates", ParagraphStyle('SubSub2', parent=section_title_style, fontSize=10, textColor=colors.HexColor('#2d6a4f'))))
    table2b_data = [[
        Paragraph("<b>Market</b>", header_cell_style),
        Paragraph("<b>Yesterday</b>", header_cell_style),
        Paragraph("<b>Today</b>", header_cell_style),
        Paragraph("<b>Change</b>", header_cell_style),
        Paragraph("<b>Status</b>", header_cell_style)
    ]]
    for row in analysis["paper_rows"]:
        table2b_data.append([
            Paragraph(row["market"], table_cell_style),
            Paragraph(row["yesterday"], table_cell_style),
            Paragraph(row["today"], table_cell_style),
            Paragraph(row["change"], table_cell_style),
            Paragraph(row["status"], table_cell_style)
        ])
    t2b = Table(table2b_data, colWidths=[100, 90, 90, 90, 160])
    t2b.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2d6a4f')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t2b)
    story.append(Spacer(1, 14))
    
    # ── Section 3: Overall Market Comparison ──
    story.append(Paragraph("3. Overall Market Comparison", section_title_style))
    story.append(Paragraph("Combined unified overview of all market prices & trends.", subtitle_style))
    
    table3_data = [[
        Paragraph("<b>Market</b>", header_cell_style),
        Paragraph("<b>Egg Price</b>", header_cell_style),
        Paragraph("<b>Loading</b>", header_cell_style),
        Paragraph("<b>Paper</b>", header_cell_style),
        Paragraph("<b>Overall Status</b>", header_cell_style)
    ]]
    for row in analysis["combined_rows"]:
        table3_data.append([
            Paragraph(row["market"], table_cell_style),
            Paragraph(row["egg_price"], table_cell_style),
            Paragraph(row["loading"], table_cell_style),
            Paragraph(row["paper"], table_cell_style),
            Paragraph(row["overall_status"], table_cell_style)
        ])
    t3 = Table(table3_data, colWidths=[80, 80, 90, 90, 190])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b4332')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1b4332')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t3)
    
    doc.build(story)

def send_daily_egg_market_pdf_job():
    logger.info("Running daily Egg Price & Market Analysis report job...")
    db = SessionLocal()
    try:
        now_ist = datetime.now(IST)
        today_start = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        
        # Strictly filter TODAY's messages for today's egg prices
        today_messages = db.query(RawMessage).filter(
            (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
            RawMessage.timestamp >= today_start
        ).order_by(RawMessage.timestamp.asc()).all()

        # Yesterday's messages for rate comparison
        yesterday_messages = db.query(RawMessage).filter(
            (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
            RawMessage.timestamp >= yesterday_start,
            RawMessage.timestamp < today_start
        ).order_by(RawMessage.timestamp.asc()).all()
        
        extracted = parse_market_rates_from_messages(today_messages, yesterday_messages)
        analysis = calculate_market_analysis(extracted)
        
        os.makedirs("/app/media/reports", exist_ok=True)
        date_str = now_ist.strftime("%d %b %Y")
        pdf_path = f"/app/media/reports/Egg_Market_Analysis_{now_ist.strftime('%Y%m%d_%H%M')}.pdf"
        
        generate_egg_market_pdf(analysis, pdf_path, date_str)
        
        target_phone = "917975209680@c.us"
        caption = f"📊 *Egg Price & Market Analysis Report*\nDate: {date_str}"
        
        logger.info(f"Sending Egg Market Analysis PDF to {target_phone}")
        send_waha_file(target_phone, pdf_path, caption=caption)
        
    except Exception as e:
        logger.error(f"Error in send_daily_egg_market_pdf_job: {e}")
    finally:
        db.close()
