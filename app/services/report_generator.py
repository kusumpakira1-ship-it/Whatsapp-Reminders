import os
import pandas as pd
from datetime import datetime, date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from db.database import SessionLocal
from db.models import ProcessedData

def generate_daily_reports():
    """Generates PDF and Excel reports for today's processed data."""
    db = SessionLocal()
    today = date.today()
    
    # Fetch today's data
    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{today} 00:00:00"
    ).all()
    
    db.close()
    
    if not data:
        return None, None, "No data collected today."
    
    # Convert to Pandas DataFrame for easy grouping
    df = pd.DataFrame([{
        "Farm Name": d.farm_name,
        "Category": d.category,
        "Quantity": float(d.quantity) if d.quantity else 0,
        "Unit": d.unit,
        "Notes": d.notes,
        "Sender": d.sender,
        "Time": d.processed_time.strftime("%H:%M:%S")
    } for d in data])
    
    os.makedirs("/app/media/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    
    excel_path = f"/app/media/reports/Daily_Report_{timestamp}.xlsx"
    pdf_path = f"/app/media/reports/Daily_Report_{timestamp}.pdf"
    
    # 1. Generate Excel
    df.to_excel(excel_path, index=False)
    
    # 2. Generate Summary Text
    summary_text = f"📊 *Daily Farm Report ({today})*\n\n"
    
    summary = df.groupby(['Farm Name', 'Category'])['Quantity'].sum().reset_index()
    for _, row in summary.iterrows():
        summary_text += f"- {row['Farm Name'] or 'Unknown Farm'}: {row['Quantity']} {row['Category']}\n"
    
    # 3. Generate PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Daily Farm Report - {today}")
    
    c.setFont("Helvetica", 12)
    y_position = 710
    
    for line in summary_text.split('\n'):
        c.drawString(50, y_position, line)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = 750
            
    c.save()
    
    return pdf_path, excel_path, summary_text
