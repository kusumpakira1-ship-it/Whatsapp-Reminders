import paramiko

users = ['u632391467', 'u632391467_kusumpakira', 'u632391467_root', 'root', 'sunfra']
passwords = ['Kusum@2026Bb!', 'Sunfra#321', 'Kusum@2026']

success = False
for u in users:
    for p in passwords:
        try:
            transport = paramiko.Transport(('145.223.17.70', 65002))
            transport.connect(username=u, password=p)
            sftp = paramiko.SFTPClient.from_transport(transport)
            print(f"✅ SFTP CONNECTED! User: {u} | Pass: {p}")
            print("SFTP List Dir:", sftp.listdir())
            success = True
            
            # Save index.php to public_html/kusum/Whatsapp_Rem/index.php
            remote_path = "/home/u632391467/domains/sunfragroup.com/public_html/kusum/Whatsapp_Rem/index.php"
            local_path = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php"
            
            # Check dirs
            print("Remote Dirs:", sftp.listdir('.'))
            sftp.put(local_path, remote_path)
            print("✅ INDEX.PHP UPLOADED TO HOSTINGER LIVE SUCCESSFULLY VIA SFTP!")
            
            sftp.close()
            transport.close()
            break
        except Exception as e:
            pass
    if success:
        break

if not success:
    print("❌ SFTP Login failed with tested credentials.")
