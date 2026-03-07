import os
import subprocess
import shutil

SCRIPT_DIR = r"PATH\TO\FILE"

LIST_FILE = os.path.join(SCRIPT_DIR, "list.txt")
YTDLP = os.path.join(SCRIPT_DIR, "yt-dlp.exe")

HOLDING_DIR = r"PATH\TO\FILE"
DEST_DIR = r"PATH\TO\FILE

os.makedirs(HOLDING_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)

with open(LIST_FILE, "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

for url in links:
    before = set(os.listdir(HOLDING_DIR))

    subprocess.run([
        YTDLP,
        "-o", os.path.join(HOLDING_DIR, "%(title)s.%(ext)s"),
        url
    ])

    after = set(os.listdir(HOLDING_DIR))
    new_files = after - before

    for file in new_files:
        src = os.path.join(HOLDING_DIR, file)
        dst = os.path.join(DEST_DIR, file)
        shutil.move(src, dst)
