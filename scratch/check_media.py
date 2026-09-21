import os

media_dir = "c:/app/media"
files = os.listdir(media_dir)
print(f"Total files in {media_dir}: {len(files)}")

for f in files:
    if "3EB08DB18F30CE14E1B338" in f or "3EB04BA303BB63ECEA1F37" in f or "184791135711366" in f:
        print("Found matching image:", f)
