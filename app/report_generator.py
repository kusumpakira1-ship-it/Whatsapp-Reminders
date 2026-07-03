import os
import re
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from database import SessionLocal
from models import ProcessedData

IST = timezone(timedelta(hours=5, minutes=30))

REVENUE_CATS = {'sales'}
EXPENSE_CATS = {'feed', 'raw_material', 'medicine', 'expense', 'purchase'}


def get_date_range(range_type: str):
    today = date.today()
    if range_type == 'weekly':
        start_date = today - timedelta(days=7)
    elif range_type == 'monthly':
        start_date = today - timedelta(days=30)
    elif range_type == 'yearly':
        start_date = today - timedelta(days=365)
    else:
        start_date = today
    return start_date, today


def _natural_sort_key(name: str):
    parts = re.split(r'(\d+)', str(name))
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _get_item_label(row) -> str:
    """Extract a meaningful item label from notes or processed_text."""
    notes = str(row.get('notes', '') or '')
    processed = str(row.get('processed_text', '') or '')

    # Try extracting "Item: X" or "Activity: X" from notes
    for prefix in ('Item:', 'Activity:', 'Medicine:', 'Material:'):
        if prefix in notes:
            val = notes.split(prefix, 1)[1].split('\n')[0].strip()
            if val:
                return val

    # Fall back to processed_text (remove shead prefix like "Shead 1 - ")
    if processed:
        cleaned = re.sub(r'^Shead\s*\d+\s*[-–]\s*', '', processed, flags=re.IGNORECASE).strip()
        if cleaned:
            return cleaned

    return ''


def _sorted_sheads(df: pd.DataFrame):
    return sorted(
        [s for s in df['shead_name'].dropna().unique() if str(s).strip()],
        key=_natural_sort_key
    )


# ─────────────────────────────────────────────────────────────────────────────
#  WHATSAPP SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def _build_whatsapp_summary(df: pd.DataFrame, range_type: str, start_date, end_date) -> str:
    today_str = datetime.now(IST).strftime("%d %b %Y")
    period_label = (
        f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"
        if start_date != end_date else today_str
    )

    lines = []
    lines.append(f"🐔 *{range_type.capitalize()} Farm Report*")
    lines.append(f"📅 {period_label}")

    # ── 🥚 EGG COLLECTIONS ──────────────────────────────────────
    egg_cats = ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']
    egg_df = df[df['category'].isin(egg_cats)]

    if not egg_df.empty:
        lines.append("")
        lines.append("🥚 *Egg Collections*")

        for round_cat, round_label, round_emoji in [
            ('egg_collection_1', '1st Collection', '🌅'),
            ('egg_collection_2', '2nd Collection', '🌆'),
            ('egg_collection',   'Collection',     '🥚'),
            ('egg',              'Eggs',            '🥚'),
        ]:
            r_df = df[df['category'] == round_cat]
            if r_df.empty:
                continue
            lines.append(f"  {round_emoji} *{round_label}*")
            sheads = _sorted_sheads(r_df)
            for shead in sheads:
                s_df = r_df[r_df['shead_name'] == shead]
                qty = s_df['quantity'].sum()
                unit = s_df['unit'].mode()[0] if not s_df['unit'].empty else 'trays'
                lines.append(f"    {shead} — {qty:,.0f} {unit}")
            # blank shead rows
            blank_df = r_df[r_df['shead_name'].isin(['', None]) | (r_df['shead_name'] == '')]
            if not blank_df.empty:
                qty = blank_df['quantity'].sum()
                unit = blank_df['unit'].mode()[0] if not blank_df['unit'].empty else 'trays'
                lines.append(f"    General — {qty:,.0f} {unit}")
            total_r = r_df['quantity'].sum()
            unit_r = r_df['unit'].mode()[0] if not r_df['unit'].empty else 'trays'
            lines.append(f"    *Total — {total_r:,.0f} {unit_r}*")

    # ── 💀 MORTALITY ─────────────────────────────────────────────
    mort_df = df[df['category'] == 'mortality']
    if not mort_df.empty:
        lines.append("")
        lines.append("💀 *Mortality*")
        for shead in _sorted_sheads(mort_df):
            qty = mort_df[mort_df['shead_name'] == shead]['quantity'].sum()
            lines.append(f"    {shead} — {qty:,.0f} birds")
        blank_m = mort_df[mort_df['shead_name'].isin(['', None]) | (mort_df['shead_name'] == '')]
        if not blank_m.empty:
            lines.append(f"    General — {blank_m['quantity'].sum():,.0f} birds")
        lines.append(f"    *Total — {mort_df['quantity'].sum():,.0f} birds*")

    # ── 📦 DISPATCH & LOADING ────────────────────────────────────
    loaded_df = df[df['category'] == 'egg_loaded']
    unloaded_df = df[df['category'] == 'egg_unloaded']
    if not loaded_df.empty or not unloaded_df.empty:
        lines.append("")
        lines.append("📦 *Dispatch & Loading*")
        if not loaded_df.empty:
            unit = loaded_df['unit'].mode()[0] if not loaded_df['unit'].empty else 'trays'
            lines.append(f"    🚛 Loaded Out — {loaded_df['quantity'].sum():,.0f} {unit}")
        if not unloaded_df.empty:
            unit = unloaded_df['unit'].mode()[0] if not unloaded_df['unit'].empty else 'trays'
            lines.append(f"    📥 Received Back — {unloaded_df['quantity'].sum():,.0f} {unit}")

    # ── 🏭 PRODUCTION ─────────────────────────────────────────────
    prod_df = df[df['category'] == 'production']
    if not prod_df.empty:
        lines.append("")
        lines.append("🏭 *Production*")
        for _, row in prod_df.iterrows():
            shead = row['shead_name'] or 'General'
            note = row['notes'] or row['processed_text'] or ''
            lines.append(f"    {shead} — {note}")

    # ── ⚖️ HEN WEIGHT ─────────────────────────────────────────────
    wt_df = df[df['category'] == 'hen_weight']
    if not wt_df.empty:
        lines.append("")
        lines.append("⚖️ *Hen Weights*")
        for shead in _sorted_sheads(wt_df):
            avg_wt = wt_df[wt_df['shead_name'] == shead]['quantity'].mean()
            lines.append(f"    {shead} — {avg_wt:.2f} kg")

    # ── 🌾 FEED & RAW MATERIALS ───────────────────────────────────
    feed_df = df[df['category'].isin(['feed', 'raw_material'])]
    if not feed_df.empty:
        lines.append("")
        lines.append("🌾 *Feed & Raw Materials*")
        for _, row in feed_df.iterrows():
            label = _get_item_label(row) or (row['notes'] or row['processed_text'] or 'Feed')
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else ''
            amt_str = f"  ₹{row['amount']:,.2f}" if row['amount'] > 0 else ''
            parts = [p for p in [label, qty_str + amt_str] if p]
            lines.append(f"    {' — '.join(parts)}" if parts else f"    {label}")
        total_feed_amt = feed_df['amount'].sum()
        if total_feed_amt > 0:
            lines.append(f"    *Total — ₹{total_feed_amt:,.2f}*")

    # ── 💊 MEDICINE ───────────────────────────────────────────────
    med_df = df[df['category'] == 'medicine']
    if not med_df.empty:
        lines.append("")
        lines.append("💊 *Medicine*")
        for _, row in med_df.iterrows():
            label = _get_item_label(row) or row['notes'] or row['processed_text'] or 'Medicine'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else ''
            amt_str = f"  ₹{row['amount']:,.2f}" if row['amount'] > 0 else ''
            parts = [p for p in [label, qty_str + amt_str] if p]
            lines.append(f"    {' — '.join(parts)}" if parts else f"    {label}")
        total_med_amt = med_df['amount'].sum()
        if total_med_amt > 0:
            lines.append(f"    *Total — ₹{total_med_amt:,.2f}*")

    # ── 🛒 PURCHASES ───────────────────────────────────────────────
    purch_df = df[df['category'] == 'purchase']
    if not purch_df.empty:
        lines.append("")
        lines.append("🛒 *Purchases*")
        for _, row in purch_df.iterrows():
            label = _get_item_label(row) or row['notes'] or row['processed_text'] or 'Purchase'
            amt_str = f"  ₹{row['amount']:,.2f}" if row['amount'] > 0 else ''
            lines.append(f"    {label}{amt_str}")
        total_p = purch_df['amount'].sum()
        if total_p > 0:
            lines.append(f"    *Total — ₹{total_p:,.2f}*")

    # ── 💸 OTHER EXPENSES ─────────────────────────────────────────
    exp_df = df[df['category'] == 'expense']
    if not exp_df.empty:
        lines.append("")
        lines.append("💸 *Other Expenses*")
        for _, row in exp_df.iterrows():
            label = _get_item_label(row) or row['notes'] or row['processed_text'] or 'Expense'
            amt_str = f"  ₹{row['amount']:,.2f}" if row['amount'] > 0 else ''
            lines.append(f"    {label}{amt_str}")
        total_e = exp_df['amount'].sum()
        if total_e > 0:
            lines.append(f"    *Total — ₹{total_e:,.2f}*")

    # ── 💵 SALES / REVENUE ────────────────────────────────────────
    sales_df = df[df['category'] == 'sales']
    if not sales_df.empty:
        lines.append("")
        lines.append("💵 *Sales*")
        for _, row in sales_df.iterrows():
            shead = row['shead_name'] or 'General'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else ''
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else ''
            detail = '  →  '.join([p for p in [qty_str, amt_str] if p])
            lines.append(f"    {shead} — {detail}" if detail else f"    {shead}")
        lines.append(f"    *Total Revenue — ₹{sales_df['amount'].sum():,.2f}*")

    # ── 📊 PROFIT & LOSS ─────────────────────────────────────────
    total_revenue = float(df[df['category'].isin(REVENUE_CATS)]['amount'].sum())
    feed_amt  = float(df[df['category'].isin(['feed', 'raw_material'])]['amount'].sum())
    med_amt   = float(df[df['category'] == 'medicine']['amount'].sum())
    purch_amt = float(df[df['category'] == 'purchase']['amount'].sum())
    exp_amt   = float(df[df['category'] == 'expense']['amount'].sum())
    total_expense = feed_amt + med_amt + purch_amt + exp_amt
    net = total_revenue - total_expense

    lines.append("")
    lines.append("📊 *Profit & Loss*")
    lines.append(f"  💵 Revenue           ₹{total_revenue:,.2f}")
    if feed_amt > 0:
        lines.append(f"  🌾 Feed & Materials  ₹{feed_amt:,.2f}")
    if med_amt > 0:
        lines.append(f"  💊 Medicine          ₹{med_amt:,.2f}")
    if purch_amt > 0:
        lines.append(f"  🛒 Purchases         ₹{purch_amt:,.2f}")
    if exp_amt > 0:
        lines.append(f"  💸 Other Expenses    ₹{exp_amt:,.2f}")
    lines.append(f"  📉 Total Expenses    ₹{total_expense:,.2f}")
    lines.append("")
    if net >= 0:
        lines.append(f"✅ *Net Profit   ₹{net:,.2f}*")
    else:
        lines.append(f"❌ *Net Loss   ₹{abs(net):,.2f}*")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  EXCEL EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def _generate_excel(excel_path: str, df: pd.DataFrame, range_type: str, start_date, end_date):
    """Generate a structured Excel with one sheet per category group."""
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:

        # Sheet 1: All Data
        export = df[['time', 'shead_name', 'category', 'quantity', 'unit',
                      'amount', 'notes', 'sender', 'group_name']].copy()
        export.columns = ['Time', 'Shead', 'Category', 'Qty', 'Unit',
                          'Amount (Rs.)', 'Notes', 'Sender', 'Group']
        export['Category'] = export['Category'].str.replace('_', ' ').str.title()
        export.to_excel(writer, sheet_name='All Data', index=False)

        # Sheet 2: Egg Collections
        egg_df = df[df['category'].isin(['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg'])].copy()
        if not egg_df.empty:
            egg_df['Round'] = egg_df['category'].map({
                'egg_collection_1': '1st Collection (Morning)',
                'egg_collection_2': '2nd Collection (Evening)',
                'egg_collection': 'General Collection',
                'egg': 'General Collection',
            })
            egg_exp = egg_df[['time', 'shead_name', 'Round', 'quantity', 'unit']].copy()
            egg_exp.columns = ['Time', 'Shead', 'Round', 'Qty', 'Unit']
            egg_exp.to_excel(writer, sheet_name='Egg Collections', index=False)

        # Sheet 3: Feed & Raw Materials (individual items)
        feed_df = df[df['category'].isin(['feed', 'raw_material'])].copy()
        if not feed_df.empty:
            feed_df['Item'] = feed_df.apply(_get_item_label, axis=1)
            feed_exp = feed_df[['time', 'shead_name', 'Item', 'quantity', 'unit', 'amount']].copy()
            feed_exp.columns = ['Time', 'Shead', 'Item', 'Qty', 'Unit', 'Amount (Rs.)']
            feed_exp.to_excel(writer, sheet_name='Feed & Raw Materials', index=False)

        # Sheet 4: Medicine (individual items)
        med_df = df[df['category'] == 'medicine'].copy()
        if not med_df.empty:
            med_df['Item'] = med_df.apply(_get_item_label, axis=1)
            med_exp = med_df[['time', 'shead_name', 'Item', 'quantity', 'unit', 'amount']].copy()
            med_exp.columns = ['Time', 'Shead', 'Item', 'Qty', 'Unit', 'Amount (Rs.)']
            med_exp.to_excel(writer, sheet_name='Medicine', index=False)

        # Sheet 5: Sales
        sales_df = df[df['category'] == 'sales'].copy()
        if not sales_df.empty:
            sales_exp = sales_df[['time', 'shead_name', 'quantity', 'unit', 'amount', 'notes']].copy()
            sales_exp.columns = ['Time', 'Shead', 'Qty', 'Unit', 'Amount (Rs.)', 'Notes']
            sales_exp.to_excel(writer, sheet_name='Sales', index=False)

        # Sheet 6: Mortality
        mort_df = df[df['category'] == 'mortality'].copy()
        if not mort_df.empty:
            mort_exp = mort_df[['time', 'shead_name', 'quantity', 'notes']].copy()
            mort_exp.columns = ['Time', 'Shead', 'Deaths', 'Notes']
            mort_exp.to_excel(writer, sheet_name='Mortality', index=False)

        # Sheet 7: P&L Summary
        total_revenue = float(df[df['category'].isin(REVENUE_CATS)]['amount'].sum())
        feed_amt  = float(df[df['category'].isin(['feed', 'raw_material'])]['amount'].sum())
        med_amt   = float(df[df['category'] == 'medicine']['amount'].sum())
        purch_amt = float(df[df['category'] == 'purchase']['amount'].sum())
        exp_amt   = float(df[df['category'] == 'expense']['amount'].sum())
        total_expense = feed_amt + med_amt + purch_amt + exp_amt
        net = total_revenue - total_expense

        pl_data = pd.DataFrame([
            {'Category': 'Revenue (Sales)',        'Amount (Rs.)': total_revenue},
            {'Category': 'Feed & Raw Materials',   'Amount (Rs.)': feed_amt},
            {'Category': 'Medicine',               'Amount (Rs.)': med_amt},
            {'Category': 'Purchases',              'Amount (Rs.)': purch_amt},
            {'Category': 'Other Expenses',         'Amount (Rs.)': exp_amt},
            {'Category': 'TOTAL EXPENSES',         'Amount (Rs.)': total_expense},
            {'Category': 'NET PROFIT / LOSS',      'Amount (Rs.)': net},
        ])
        pl_data.to_excel(writer, sheet_name='P&L Summary', index=False)


# ─────────────────────────────────────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def _generate_pdf(pdf_path: str, df: pd.DataFrame, range_type: str, start_date, end_date):
    """Generate a structured, section-based PDF report."""
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []

    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceAfter=4, textColor=colors.HexColor('#1b4332'))
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, textColor=colors.HexColor('#2d6a4f'), spaceBefore=12)
    normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
    bold = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')

    period_label = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    story.append(Paragraph(f"🐔 Farm Report — {range_type.capitalize()}", h1))
    story.append(Paragraph(f"Period: {period_label}", normal))
    story.append(Spacer(1, 0.1*inch))

    def _section_table(headers, rows, col_widths, header_color='#2d6a4f'):
        data = [headers] + rows
        tbl = Table(data, colWidths=col_widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fff4')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        return tbl

    # ── EGG COLLECTIONS ──
    egg_cats = ['egg_collection_1', 'egg_collection_2', 'egg_collection', 'egg']
    egg_df = df[df['category'].isin(egg_cats)]
    if not egg_df.empty:
        story.append(Paragraph("🥚 Egg Collections", h2))
        round_map = {
            'egg_collection_1': '1st (Morning)',
            'egg_collection_2': '2nd (Evening)',
            'egg_collection': 'General',
            'egg': 'General',
        }
        egg_rows = []
        for _, row in egg_df.sort_values(['category', 'shead_name']).iterrows():
            egg_rows.append([
                round_map.get(row['category'], row['category']),
                row['shead_name'] or '—',
                f"{row['quantity']:,.0f} {row['unit']}".strip(),
                row['time'],
            ])
        story.append(_section_table(['Round', 'Shead', 'Quantity', 'Time'], egg_rows,
                                    [1.5*inch, 1.2*inch, 1.5*inch, 1.0*inch]))

    # ── MORTALITY ──
    mort_df = df[df['category'] == 'mortality']
    if not mort_df.empty:
        story.append(Paragraph("💀 Mortality", h2))
        rows = [[row['shead_name'] or '—', f"{row['quantity']:,.0f} birds", row['time']]
                for _, row in mort_df.iterrows()]
        rows.append(['TOTAL', f"{mort_df['quantity'].sum():,.0f} birds", ''])
        story.append(_section_table(['Shead', 'Deaths', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── DISPATCH & LOADING ──
    loaded_df = df[df['category'] == 'egg_loaded']
    unloaded_df = df[df['category'] == 'egg_unloaded']
    if not loaded_df.empty or not unloaded_df.empty:
        story.append(Paragraph("📦 Dispatch & Loading", h2))
        rows = []
        for _, row in loaded_df.iterrows():
            rows.append(['Loaded Out', f"{row['quantity']:,.0f} {row['unit']}".strip(), row['time']])
        for _, row in unloaded_df.iterrows():
            rows.append(['Received Back', f"{row['quantity']:,.0f} {row['unit']}".strip(), row['time']])
        story.append(_section_table(['Type', 'Quantity', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── PRODUCTION ──
    prod_df = df[df['category'] == 'production']
    if not prod_df.empty:
        story.append(Paragraph("🏭 Production", h2))
        rows = [[row['shead_name'] or '—', row['notes'] or row['processed_text'] or '', row['time']]
                for _, row in prod_df.iterrows()]
        story.append(_section_table(['Shead', 'Details', 'Time'], rows, [1.5*inch, 3.5*inch, 1.0*inch]))

    # ── HEN WEIGHT ──
    wt_df = df[df['category'] == 'hen_weight']
    if not wt_df.empty:
        story.append(Paragraph("⚖️ Hen Weights", h2))
        rows = [[row['shead_name'] or '—', f"{row['quantity']:.2f} kg", row['time']]
                for _, row in wt_df.iterrows()]
        story.append(_section_table(['Shead', 'Weight', 'Time'], rows, [2*inch, 2*inch, 1.5*inch]))

    # ── FEED & RAW MATERIALS ──
    feed_df = df[df['category'].isin(['feed', 'raw_material'])]
    if not feed_df.empty:
        story.append(Paragraph("🌾 Feed & Raw Materials", h2))
        rows = []
        for _, row in feed_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, qty_str, amt_str, row['time']])
        total_f = feed_df['amount'].sum()
        rows.append(['', 'TOTAL', '', f"₹{total_f:,.2f}", ''])
        story.append(_section_table(['Shead', 'Item', 'Qty', 'Amount', 'Time'], rows,
                                    [1.0*inch, 2.0*inch, 1.0*inch, 1.2*inch, 0.8*inch]))

    # ── MEDICINE ──
    med_df = df[df['category'] == 'medicine']
    if not med_df.empty:
        story.append(Paragraph("💊 Medicine", h2))
        rows = []
        for _, row in med_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, qty_str, amt_str, row['time']])
        total_m = med_df['amount'].sum()
        rows.append(['', 'TOTAL', '', f"₹{total_m:,.2f}", ''])
        story.append(_section_table(['Shead', 'Medicine', 'Qty', 'Amount', 'Time'], rows,
                                    [1.0*inch, 2.0*inch, 1.0*inch, 1.2*inch, 0.8*inch]))

    # ── PURCHASES ──
    purch_df = df[df['category'] == 'purchase']
    if not purch_df.empty:
        story.append(Paragraph("🛒 Purchases", h2))
        rows = []
        for _, row in purch_df.iterrows():
            item = _get_item_label(row) or row['notes'] or '—'
            amt_str = f"₹{row['amount']:,.2f}" if row['amount'] > 0 else '—'
            rows.append([row['shead_name'] or '—', item, amt_str, row['time']])
        story.append(_section_table(['Shead', 'Item', 'Amount', 'Time'], rows,
                                    [1.2*inch, 2.5*inch, 1.2*inch, 1.1*inch]))

    # ── SALES ──
    sales_df = df[df['category'] == 'sales']
    if not sales_df.empty:
        story.append(Paragraph("💵 Sales", h2))
        rows = []
        for _, row in sales_df.iterrows():
            qty_str = f"{row['quantity']:,.0f} {row['unit']}".strip() if row['quantity'] > 0 else '—'
            rows.append([row['shead_name'] or '—', qty_str, f"₹{row['amount']:,.2f}", row['time']])
        rows.append(['TOTAL', '', f"₹{sales_df['amount'].sum():,.2f}", ''])
        story.append(_section_table(['Shead', 'Qty', 'Revenue', 'Time'], rows,
                                    [1.5*inch, 1.5*inch, 1.5*inch, 1.0*inch]))

    # ── P&L SUMMARY ──
    story.append(Paragraph("📊 Profit & Loss", h2))
    total_revenue = float(df[df['category'].isin(REVENUE_CATS)]['amount'].sum())
    feed_amt  = float(df[df['category'].isin(['feed', 'raw_material'])]['amount'].sum())
    med_amt   = float(df[df['category'] == 'medicine']['amount'].sum())
    purch_amt = float(df[df['category'] == 'purchase']['amount'].sum())
    exp_amt   = float(df[df['category'] == 'expense']['amount'].sum())
    total_expense = feed_amt + med_amt + purch_amt + exp_amt
    net = total_revenue - total_expense

    pl_rows = [
        ['💵 Revenue (Sales)',       f"₹{total_revenue:,.2f}"],
    ]
    if feed_amt > 0:
        pl_rows.append(['🌾 Feed & Raw Materials', f"₹{feed_amt:,.2f}"])
    if med_amt > 0:
        pl_rows.append(['💊 Medicine',             f"₹{med_amt:,.2f}"])
    if purch_amt > 0:
        pl_rows.append(['🛒 Purchases',            f"₹{purch_amt:,.2f}"])
    if exp_amt > 0:
        pl_rows.append(['💸 Other Expenses',       f"₹{exp_amt:,.2f}"])
    pl_rows.append(['📉 Total Expenses',            f"₹{total_expense:,.2f}"])
    pl_rows.append(['✅ NET PROFIT / LOSS',         f"₹{net:,.2f}"])

    pl_table = Table([['Category', 'Amount']] + pl_rows, colWidths=[3*inch, 2*inch])
    pl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1b4332')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0fff4')]),
        ('BACKGROUND', (0, -1), (-1, -1),
         colors.HexColor('#d8f3dc') if net >= 0 else colors.HexColor('#ffe0e0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(pl_table)

    doc.build(story)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def generate_custom_report(range_type: str = 'daily'):
    db = SessionLocal()
    start_date, end_date = get_date_range(range_type)

    data = db.query(ProcessedData).filter(
        ProcessedData.processed_time >= f"{start_date} 00:00:00"
    ).all()
    db.close()

    if not data:
        return None, None, f"📭 No farm data collected for {start_date.strftime('%d %b %Y')}."

    df = pd.DataFrame([{
        'shead_name':    d.shead_name or '',
        'category':      d.category or 'unknown',
        'quantity':      float(d.quantity) if d.quantity else 0,
        'unit':          d.unit or '',
        'amount':        float(d.amount) if d.amount else 0.0,
        'notes':         d.notes or '',
        'processed_text': '',
        'sender':        d.sender or '',
        'group_name':    d.group_name or '',
        'time':          d.processed_time.strftime("%H:%M") if d.processed_time else '',
    } for d in data])

    df = df[df['category'] != 'unknown']
    if df.empty:
        return None, None, f"📭 No classifiable farm data found for {start_date.strftime('%d %b %Y')}."

    os.makedirs("/app/media/reports", exist_ok=True)
    
    # Delete old reports of the same range type to keep directory clean
    import glob
    for old_file in glob.glob(f"/app/media/reports/{range_type.capitalize()}_Report_*"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M")
    excel_path = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.xlsx"
    pdf_path   = f"/app/media/reports/{range_type.capitalize()}_Report_{timestamp}.pdf"

    summary_text = _build_whatsapp_summary(df, range_type, start_date, end_date)
    _generate_excel(excel_path, df, range_type, start_date, end_date)
    _generate_pdf(pdf_path, df, range_type, start_date, end_date)

    return pdf_path, excel_path, summary_text


def generate_daily_reports():
    return generate_custom_report('daily')
