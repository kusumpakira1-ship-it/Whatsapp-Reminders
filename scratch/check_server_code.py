import ftplib, io
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
buf = io.BytesIO()
ftp.retrbinary('RETR index.php', buf.write)
content = buf.getvalue().decode('utf-8', errors='ignore')
ftp.quit()

# Find the waha/groups section
marker = "waha/groups"
start = content.find(marker)
# Find the guaranteed_groups section
gg_start = content.find('guaranteed_groups')
gg_end = content.find('usort($unique_groups', gg_start)
print("=== guaranteed_groups block on server ===")
print(content[gg_start:gg_end + 100])
print()
print("=== Around 'Sales' keyword in waha/groups route ===")
sales_idx = content.find('Sales - Sunfra Feeds', gg_start)
if sales_idx >= 0:
    print(content[sales_idx-50:sales_idx+100])
else:
    print("NOT FOUND in guaranteed_groups block")
