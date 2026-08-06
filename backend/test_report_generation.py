from sunfra_pandl_report import generate_and_send_sunfra_pandl_report

print("Testing Sunfra P&L PDF report generation...")
res = generate_and_send_sunfra_pandl_report(recipient_phone="917259510983@c.us")
print("Report Generation Result:", res)
