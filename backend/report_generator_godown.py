import os
import glob
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from database import SessionLocal
from models import ProcessedData, EggGodownInventory
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable

IST = timezone(timedelta(hours=5, minutes=30))

def generate_godown_report():
    db = SessionLocal()
    now_ist = datetime.now(IST)
    today_dt = now_ist.date()
    yesterday_dt = today_dt - timedelta(days=1)

    # 1. Fetch egg collections for today
    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{today_dt} 00:00:00",
        ProcessedData.processed_time <= f"{today_dt} 23:59:59",
        ProcessedData.category.in_(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg'])
    ).all()

    # 2. Get today's and yesterday's inventory
    today_inv = db.query(EggGodownInventory).filter(EggGodownInventory.date == today_dt).first()
    yesterday_inv = db.query(EggGodownInventory).filter(EggGodownInventory.date == yesterday_dt).first()

    opening = 0
    closing = 0

    if today_inv:
        opening = today_inv.opening_balance
        closing = today_inv.closing_balance
    elif yesterday_inv:
        # Fallback opening to yesterday's closing
        opening = yesterday_inv.closing_balance

    # 3. Process production by shed (Shed 1 to Shed 9)
    # Parse data into dataframe
    df = pd.DataFrame([{
        'shed': str(d.shead_name or '').strip(),
        'qty': float(d.quantity) if d.quantity else 0.0,
        'unit': str(d.unit or '').lower(),
        'cat': str(d.category or '').lower()
    } for d in data]) if data else pd.DataFrame()

    shed_data = {}
    for i in range(1, 10):
        shed_data[f"Shed {i}"] = {"c1": 0, "c2": 0, "total": 0}

    grand_total_produced = 0

    if not df.empty:
        import re
        for _, row in df.iterrows():
            name = row['shed']
            numbers = re.findall(r'\d+', name)
            if not numbers:
                continue
            shed_num = int(numbers[0])
            if shed_num < 1 or shed_num > 9:
                continue
            
            shed_key = f"Shed {shed_num}"
            qty = row['qty']
            eggs = qty * 30 if 'tray' in row['unit'] else qty
            cat = row['cat']

            if cat == 'egg_collection_1':
                shed_data[shed_key]["c1"] += int(eggs)
            elif cat == 'egg_collection_2':
                shed_data[shed_key]["c2"] += int(eggs)
            else:
                # General collection - split or add to c1
                shed_data[shed_key]["c1"] += int(eggs)

            shed_data[shed_key]["total"] += int(eggs)
            grand_total_produced += int(eggs)

    # If closing balance is not explicitly entered, closing balance = opening + production
    if not today_inv or today_inv.closing_balance == 0:
        closing = opening + grand_total_produced

    # 4. Save total produced back to today's inventory row
    try:
        if today_inv:
            today_inv.total_produced = grand_total_produced
            db.commit()
        else:
            new_inv = EggGodownInventory(
                date=today_dt,
                opening_balance=opening,
                closing_balance=closing,
                total_produced=grand_total_produced
            )
            db.add(new_inv)
            db.commit()
    except Exception as commit_err:
        db.rollback()
        print("Error saving total produced:", commit_err)

    # 5. Format WhatsApp text message
    date_str = today_dt.strftime("%A, %d %B %Y")
    msg_lines = [
        "🥚 *Daily Egg Godown Summary* 🥚",
        f"Date: *{date_str}*",
        "",
        "*Production by Shed (1st & 2nd Collection):*"
    ]
    for i in range(1, 10):
        sk = f"Shed {i}"
        c1 = shed_data[sk]["c1"]
        c2 = shed_data[sk]["c2"]
        tot = shed_data[sk]["total"]
        msg_lines.append(f"- *Shed {i}*: 1st: {c1:,} | 2nd: {c2:,} | Total: *{tot:,}*")

    msg_lines.append("")
    msg_lines.append(f"📈 *Grand Total Production:* {grand_total_produced:,} eggs")
    msg_lines.append("")
    msg_lines.append("*Godown Stock Balance:*")
    msg_lines.append(f"- Opening Balance: {opening:,} eggs")
    msg_lines.append(f"- Received (Production): +{grand_total_produced:,} eggs")
    msg_lines.append(f"- Closing Balance: *{closing:,}* eggs")

    summary_text = "\n".join(msg_lines)

    # 6. Generate PDF report
    os.makedirs("/app/media/reports", exist_ok=True)
    # Cleanup old godown reports
    for old_file in glob.glob("/app/media/reports/Godown_Report_*"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    timestamp = now_ist.strftime("%Y%m%d_%H%M")
    pdf_path = f"/app/media/reports/Godown_Report_{timestamp}.pdf"

    # Build PDF Story
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, fontSize=18, textColor=colors.HexColor('#1b4332'), spaceAfter=15)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2d6a4f'), spaceBefore=10, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
    table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'], alignment=1, fontSize=10, textColor=colors.white, fontName='Helvetica-Bold')
    table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], alignment=1, fontSize=10)

    story = [
        Paragraph(f"<b>Egg Godown Summary Report</b>", title_style),
        Paragraph(f"<b>Date:</b> {date_str}", body_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2d6a4f'), spaceAfter=15),
        Paragraph("<b>1. Production by Shed (Sheds 1-9)</b>", section_style),
    ]

    # Create Shed table
    table_data = [[
        Paragraph("<b>Shed</b>", table_header_style),
        Paragraph("<b>1st Collection</b>", table_header_style),
        Paragraph("<b>2nd Collection</b>", table_header_style),
        Paragraph("<b>Total Eggs</b>", table_header_style)
    ]]

    for i in range(1, 10):
        sk = f"Shed {i}"
        table_data.append([
            Paragraph(sk, table_cell_style),
            Paragraph(f"{shed_data[sk]['c1']:,}", table_cell_style),
            Paragraph(f"{shed_data[sk]['c2']:,}", table_cell_style),
            Paragraph(f"<b>{shed_data[sk]['total']:,}</b>", table_cell_style)
        ])
        
    table_data.append([
        Paragraph("<b>Grand Total</b>", table_cell_style),
        Paragraph("", table_cell_style),
        Paragraph("", table_cell_style),
        Paragraph(f"<b>{grand_total_produced:,}</b>", table_cell_style)
    ])

    col_widths = [110, 130, 130, 130]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d6a4f')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d8f3dc')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>2. Godown Inventory Balance Summary</b>", section_style))

    inv_data = [
        [Paragraph("<b>Metric</b>", table_header_style), Paragraph("<b>Quantity (Eggs)</b>", table_header_style)],
        [Paragraph("Opening Balance", table_cell_style), Paragraph(f"{opening:,}", table_cell_style)],
        [Paragraph("Received (Production)", table_cell_style), Paragraph(f"+{grand_total_produced:,}", table_cell_style)],
        [Paragraph("<b>Closing Balance</b>", table_cell_style), Paragraph(f"<b>{closing:,}</b>", table_cell_style)]
    ]

    t_inv = Table(inv_data, colWidths=[250, 250])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1b4332')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#d8f3dc')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_inv)

    doc.build(story)
    db.close()
    return pdf_path, summary_text
