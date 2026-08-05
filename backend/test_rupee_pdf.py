import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Check available TTF fonts on system
font_path = None
for p in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf"
]:
    if os.path.exists(p):
        font_path = p
        break

print("Found Font Path:", font_path)

if font_path:
    pdfmetrics.registerFont(TTFont('RupeeFont', font_path))
    pdfmetrics.registerFont(TTFont('RupeeFontBold', font_path))
    font_name = 'RupeeFont'
    font_name_bold = 'RupeeFontBold'
else:
    font_name = 'Helvetica'
    font_name_bold = 'Helvetica-Bold'

doc = SimpleDocTemplate("/tmp/rupee_test.pdf", pagesize=A4)
story = []
styles = getSampleStyleSheet()

t_data = [
    ["Shead Name", "Feed Cost", "Profit"],
    ["Chick 1", "₹ 77,527", "-₹ 81,180"],
    ["Shead 1", "₹ 3,45,190", "₹ 35,534"]
]

t = Table(t_data, colWidths=[150, 150, 150])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#137333')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, -1), font_name_bold),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray)
]))
story.append(t)
doc.build(story)
print("PDF with Rupee Symbol Generated Successfully!")
