from PIL import Image, ImageDraw, ImageFont
import os

def create_pandl_table_image(title_date: str, rows_data: list, output_path: str = "pandl_table.png") -> str:
    """Generates a high-quality table image matching the user's green P&L reference image."""
    
    # Image dimensions & colors
    header_bg = (19, 115, 51)       # Dark green #137333
    header_text_color = (255, 255, 255) # White
    title_bg = (15, 95, 40)         # Header title green
    row_even_bg = (255, 255, 255)   # White
    row_odd_bg = (245, 248, 245)    # Very light green tint
    grid_color = (180, 180, 180)    # Gray grid lines
    text_color = (0, 0, 0)          # Black text
    total_row_bg = (240, 240, 240)  # Light gray for total
    
    # Column definitions & widths
    cols = [
        {"name": "Shead Name", "width": 140, "align": "left"},
        {"name": "Batch Age", "width": 110, "align": "center"},
        {"name": "Feed Cost", "width": 110, "align": "right"},
        {"name": "Labour Cost", "width": 110, "align": "right"},
        {"name": "Production", "width": 120, "align": "right"},
        {"name": "Egg Revenue", "width": 120, "align": "right"},
        {"name": "Profit", "width": 110, "align": "right"}
    ]
    
    table_width = sum(c["width"] for c in cols)
    row_height = 36
    title_height = 44
    header_height = 40
    
    num_rows = len(rows_data) + 1 # rows + total row
    table_height = title_height + header_height + (num_rows * row_height)
    
    img = Image.new("RGB", (table_width, table_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load fonts (fallback to default if custom font not found)
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_header = ImageFont.truetype("arialbd.ttf", 16)
        font_body = ImageFont.truetype("arial.ttf", 15)
        font_bold = ImageFont.truetype("arialbd.ttf", 15)
    except Exception:
        font_title = font_header = font_body = font_bold = ImageFont.load_default()

    # 1. Draw Title
    draw.rectangle([0, 0, table_width, title_height], fill=title_bg)
    title_text = f"Sunfra Farms on {title_date}"
    # Center title
    try:
        w = draw.textlength(title_text, font=font_title)
    except Exception:
        w = 200
    draw.text(((table_width - w) / 2, 10), title_text, fill=(255, 255, 255), font=font_title)

    # 2. Draw Column Headers
    y = title_height
    draw.rectangle([0, y, table_width, y + header_height], fill=header_bg)
    
    x = 0
    for col in cols:
        col_w = col["width"]
        text = col["name"]
        # Center header text
        try:
            tw = draw.textlength(text, font=font_header)
        except Exception:
            tw = 50
        tx = x + (col_w - tw) / 2
        draw.text((tx, y + 10), text, fill=header_text_color, font=font_header)
        x += col_w

    y += header_height

    # 3. Draw Data Rows
    tot_feed = 0.0
    tot_labour = 0.0
    tot_prod = 0.0
    tot_rev = 0.0
    tot_profit = 0.0

    for idx, r in enumerate(rows_data):
        bg = row_odd_bg if idx % 2 == 1 else row_even_bg
        draw.rectangle([0, y, table_width, y + row_height], fill=bg)
        
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

        values = [
            (str(r.get("shead", "")), cols[0]),
            (str(r.get("batch_age", "")), cols[1]),
            (f"{feed_c:,.0f}" if feed_c > 0 else "0", cols[2]),
            (f"{labour_c:,.0f}" if labour_c > 0 else "0", cols[3]),
            (f"{prod:,.2f}" if prod > 0 else "0", cols[4]),
            (f"{rev:,.0f}" if rev > 0 else "0", cols[5]),
            (f"{profit:,.0f}", cols[6])
        ]
        
        x = 0
        for val_str, col in values:
            col_w = col["width"]
            align = col["align"]
            
            try:
                tw = draw.textlength(val_str, font=font_body)
            except Exception:
                tw = 40
                
            if align == "center":
                tx = x + (col_w - tw) / 2
            elif align == "right":
                tx = x + col_w - tw - 12
            else:
                tx = x + 12
                
            draw.text((tx, y + 9), val_str, fill=text_color, font=font_body)
            x += col_w
            
        y += row_height

    # 4. Draw Total Row
    draw.rectangle([0, y, table_width, y + row_height], fill=total_row_bg)
    
    tot_values = [
        ("", cols[0]),
        ("", cols[1]),
        ("", cols[2]),
        ("", cols[3]),
        ("", cols[4]),
        ("Total", cols[5]),
        (f"{tot_profit:,.0f}", cols[6])
    ]
    
    x = 0
    for val_str, col in tot_values:
        col_w = col["width"]
        if val_str:
            try:
                tw = draw.textlength(val_str, font=font_bold)
            except Exception:
                tw = 40
            tx = x + col_w - tw - 12 if col["align"] == "right" else x + 12
            draw.text((tx, y + 9), val_str, fill=text_color, font=font_bold)
        x += col_w

    # 5. Draw Grid Lines
    # Horizontal lines
    for hy in range(title_height, table_height + 1, row_height):
        draw.line([(0, hy), (table_width, hy)], fill=grid_color, width=1)
    draw.line([(0, title_height), (table_width, title_height)], fill=grid_color, width=1)

    # Vertical lines
    vx = 0
    for col in cols:
        draw.line([(vx, title_height), (vx, table_height)], fill=grid_color, width=1)
        vx += col["width"]
    draw.line([(table_width - 1, title_height), (table_width - 1, table_height)], fill=grid_color, width=1)

    img.save(output_path)
    print(f"Table Image Generated Successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    test_rows = [
        {"shead": "Chick 1", "batch_age": "4 Week", "feed_cost": 77527, "labour_cost": 333, "production": 0, "revenue": 0, "profit": -77861},
        {"shead": "Egg Godown", "batch_age": "", "feed_cost": 0, "labour_cost": 2596, "production": 0, "revenue": 0, "profit": -2596},
        {"shead": "Feed Plant", "batch_age": "", "feed_cost": 0, "labour_cost": 3481, "production": 0, "revenue": 0, "profit": -3481},
        {"shead": "Gate Manager", "batch_age": "", "feed_cost": 0, "labour_cost": 1366, "production": 0, "revenue": 0, "profit": -1366},
        {"shead": "Grower 1", "batch_age": "", "feed_cost": 0, "labour_cost": 0, "production": 0, "revenue": 0, "profit": 43000},
        {"shead": "Others", "batch_age": "", "feed_cost": 0, "labour_cost": 6625, "production": 0, "revenue": 0, "profit": -6625},
        {"shead": "Shead 1", "batch_age": "53 Weeks", "feed_cost": 184328, "labour_cost": 1166, "production": 598.23, "revenue": 110472, "profit": -75022},
        {"shead": "Shead 2", "batch_age": "53 Weeks", "feed_cost": 160132, "labour_cost": 666, "production": 629.21, "revenue": 116179, "profit": -44618},
        {"shead": "Shead 3", "batch_age": "23 Weeks", "feed_cost": 195441, "labour_cost": 1332, "production": 648.13, "revenue": 83647, "profit": -113125},
        {"shead": "Shead 4", "batch_age": "65 Weeks", "feed_cost": 183523, "labour_cost": 933, "production": 633.02, "revenue": 116800, "profit": -67656},
        {"shead": "Shead 5", "batch_age": "16 Weeks", "feed_cost": 202581, "labour_cost": 333, "production": 0, "revenue": 0, "profit": -202914},
        {"shead": "Shead 6", "batch_age": "71 Weeks", "feed_cost": 175740, "labour_cost": 1532, "production": 602.09, "revenue": 111124, "profit": -66148},
        {"shead": "Shead 7", "batch_age": "79 Weeks", "feed_cost": 175459, "labour_cost": 2816, "production": 571.10, "revenue": 105411, "profit": -72865},
        {"shead": "Shead 8", "batch_age": "35 Weeks", "feed_cost": 206768, "labour_cost": 666, "production": 694.17, "revenue": 116687, "profit": -90748}
    ]
    create_pandl_table_image("Jul 27, 2026", test_rows, "test_table.png")
