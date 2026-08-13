"""
Copy Venkat's 5 feed report images sent at 10:06 PM yesterday to artifacts directory and inspect
"""

import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')

media_dir = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\media"
artifacts_dir = r"C:\Users\sunfra\.gemini\antigravity-ide\brain\a01d7f12-f2e1-4d67-8055-f48c5359db15"

venkat_files = [
    "false_120363428748481277@g.us_3EB066CBEFA11836C61FAB_45586833240126@lid.jpg",
    "false_120363428748481277@g.us_3EB070737234F701391E28_45586833240126@lid.jpg",
    "false_120363428748481277@g.us_3EB07A0BFA12F386384E04_45586833240126@lid.jpg",
    "false_120363428748481277@g.us_3EB0989220A512125F8353_45586833240126@lid.jpg",
    "false_120363428748481277@g.us_3EB0FB4BF7B4CD7E1E451E_45586833240126@lid.jpg"
]

print("=== VENKAT FEED REPORT IMAGES (Summary - Sunfra Feeds Group) ===")
copied = []
for idx, fn in enumerate(venkat_files, 1):
    src = os.path.join(media_dir, fn)
    dst_name = f"venkat_feed_report_12aug_{idx}.jpg"
    dst = os.path.join(artifacts_dir, dst_name)
    if os.path.exists(src):
        shutil.copy(src, dst)
        sz = os.path.getsize(dst)
        print(f"Image {idx}: {dst_name} (Size: {sz:,} bytes) -> Copied to Artifacts ✅")
        copied.append(dst)
    else:
        print(f"Image {idx}: {fn} not found in media dir ❌")

