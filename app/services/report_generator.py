import os
import pandas as pd
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from db.database import SessionLocal
from db.models import ProcessedData

def get_date_range(range_type: str):
    today = date.today()
    if range_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif range_type == 'monthly':
        start_date = today - timedelta(days=30)
    elif range_type == 'yearly':
        start_date = today - timedelta(days=365)
    else: # default daily
        start_date = today
    return start_date, today

def generate_custom_report(range_type: str = 'daily'):
    """Generates PDF and Excel reports with P&L for a specific time range."""
    db = SessionLocal()
    start_date, end_date = get_date_range(range_type)
    
    # Fetch data
    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{start_date} 00:00:00"
    ).all()
    db.close()
    
    if not data:
        return None, None, f"No data collected for the {range_type} period."
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        "Farm Name": d.farm_name,
        "Category": d.category.capitalize(),
        "Quantity": float(d.quantity) if d.quantity else 0,
        "Unit": d.unit,
        "Amount": float(d.amount) if d.amount else 0.0,
        "Notes": d.notes,
        "Time": d.processed_time.strftime("%Y-%m-%d %H:%M")
    } for d in data])
    
    # P&L Calculation
    revenue_categories = ['Sales']
    expense_categories = ['Feed', 'Medicine', 'Purchase', 'Expense']
    
    total_revenue = df[df['Category'].isin(revenue_categories)]['Amount'].sum()
    total_expense = df[df['Category'].isin(expense_categories)]['Amount'].sum()
    net_profit = total_revenue - total_expense
    
    os.makedirs("/app/media/reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    excel_path = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.xlsx"
    pdf_path = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.pdf"
    
    # 1. Generate Excel
    df.to_excel(excel_path, index=False)
    
    # 2. Generate Summary Text
    summary_text = f"📊 *{range_type.capitalize()} Financial Report*\n"
    summary_text += f"📅 {start_date} to {end_date}\n\n"
    summary_text += f"📈 *Revenue:* ₹{total_revenue:,.2f}\n"
    summary_text += f"📉 *Expenses:* ₹{total_expense:,.2f}\n"
    summary_text += f"💰 *Net Profit:* ₹{net_profit:,.2f}\n\n"
    summary_text += "*Breakdown by Category:*\n"
    
    summary = df.groupby(['Farm Name', 'Category'])['Quantity'].sum().reset_index()
    for _, row in summary.iterrows():
        farm = row['Farm Name'] or 'Unknown Farm'
        summary_text += f"- {farm}: {row['Quantity']} {row['Category']}\n"
    
    # 3. Generate PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, f"Farm Financial Report - {range_type.capitalize()}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Period: {start_date} to {end_date}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 690, "Profit & Loss Summary")
    c.setFont("Helvetica", 12)
    c.drawString(50, 670, f"Total Revenue: Rs. {total_revenue:,.2f}")
    c.drawString(50, 650, f"Total Expenses: Rs. {total_expense:,.2f}")
    c.drawString(50, 630, f"Net Profit: Rs. {net_profit:,.2f}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 590, "Activity Breakdown")
    c.setFont("Helvetica", 12)
    
    y_position = 570
    for _, row in summary.iterrows():
        farm = row['Farm Name'] or 'Unknown Farm'
        c.drawString(50, y_position, f"{farm}: {row['Quantity']} {row['Category']}")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = 750
            
    c.save()
    
    return pdf_path, excel_path, summary_text

# Keep the old one just in case scheduler needs exactly this signature for now, but route it
def generate_daily_reports():
    return generate_custom_report('daily')
