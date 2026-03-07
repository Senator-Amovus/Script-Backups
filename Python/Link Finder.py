import subprocess
import sys
import csv

# Auto-install pytube if missing
try:
    from pytube import Playlist
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
    from pytube import Playlist

PLAYLIST_URL = "Link goes here"

OUTPUT_FILE = r"PATH\TO\FILE\Links.csv"

playlist = Playlist(PLAYLIST_URL)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Link"])
    for url in playlist.video_urls:
        writer.writerow([url])

print("Saved to:", OUTPUT_FILE)
