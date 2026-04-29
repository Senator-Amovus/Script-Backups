#!/usr/bin/env python3
"""
Playlist Bridge — YouTube ↔ Spotify importer
Dependencies: pip install requests google-api-python-client google-auth-oauthlib spotipy
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import re
import time
import json
import os
import sys

# ── Dependency check ──────────────────────────────────────────────────────────
MISSING = []
try:
    import requests
except ImportError:
    MISSING.append("requests")
try:
    from googleapiclient.discovery import build as yt_build
    from google_auth_oauthlib.flow import InstalledAppFlow
    import google.auth.transport.requests
except ImportError:
    MISSING.append("google-api-python-client google-auth-oauthlib")
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    MISSING.append("spotipy")

if MISSING:
    print("Install missing packages first:")
    print(f"  pip install {' '.join(MISSING)}")
    sys.exit(1)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_yt_playlist_id(text):
    text = text.strip()
    m = re.search(r'list=([A-Za-z0-9_-]+)', text)
    if m:
        return m.group(1)
    if re.match(r'^[A-Za-z0-9_-]{10,}$', text):
        return text
    return None

def extract_sp_playlist_id(text):
    text = text.strip()
    m = re.search(r'playlist/([A-Za-z0-9]+)', text)
    if m:
        return m.group(1)
    if re.match(r'^[A-Za-z0-9]{22}$', text):
        return text
    return None

def clean_title(title):
    """Strip common YouTube noise: (Official Video), [Lyrics], etc."""
    title = re.sub(r'\(.*?(official|video|audio|lyrics|hd|4k|mv).*?\)', '', title, flags=re.I)
    title = re.sub(r'\[.*?(official|video|audio|lyrics|hd|4k|mv).*?\]', '', title, flags=re.I)
    title = re.sub(r'\s{2,}', ' ', title)
    return title.strip()

# ── YouTube API ───────────────────────────────────────────────────────────────

def get_yt_service(api_key=None, oauth_json=None):
    if oauth_json and os.path.exists(oauth_json):
        SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
        flow = InstalledAppFlow.from_client_secrets_file(oauth_json, SCOPES)
        creds = flow.run_local_server(port=0)
        return yt_build('youtube', 'v3', credentials=creds)
    if api_key:
        return yt_build('youtube', 'v3', developerKey=api_key)
    raise ValueError("Provide either a YouTube API Key or OAuth JSON file.")

def fetch_yt_playlist_tracks(service, playlist_id, max_songs=0, log=print):
    tracks = []
    page_token = None
    log(f"[YT] Fetching playlist: {playlist_id}")
    while True:
        req = service.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=page_token
        )
        resp = req.execute()
        for item in resp.get('items', []):
            sn = item['snippet']
            title = sn.get('title', '')
            channel = sn.get('videoOwnerChannelTitle', '')
            if title in ('Deleted video', 'Private video'):
                log(f"[YT] Skipping: {title}")
                continue
            tracks.append({'title': title, 'artist': channel})
            log(f"[YT] ✓ {title} — {channel}")
            if max_songs and len(tracks) >= max_songs:
                return tracks
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    log(f"[YT] Total tracks fetched: {len(tracks)}")
    return tracks

def create_yt_playlist(service, name, log=print):
    log(f"[YT] Creating playlist: {name}")
    resp = service.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {'title': name, 'description': 'Imported by Playlist Bridge'},
            'status': {'privacyStatus': 'private'}
        }
    ).execute()
    pl_id = resp['id']
    log(f"[YT] Playlist created: https://youtube.com/playlist?list={pl_id}")
    return pl_id

def search_and_add_yt_video(service, playlist_id, query, log=print):
    results = service.search().list(
        part='snippet', q=query, type='video', maxResults=1
    ).execute()
    items = results.get('items', [])
    if not items:
        log(f"[YT] ✗ Not found: {query}")
        return False
    video_id = items[0]['id']['videoId']
    video_title = items[0]['snippet']['title']
    service.playlistItems().insert(
        part='snippet',
        body={
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {'kind': 'youtube#video', 'videoId': video_id}
            }
        }
    ).execute()
    log(f"[YT] ✓ Added: {video_title}")
    return True

# ── Spotify API ───────────────────────────────────────────────────────────────

def get_sp_client(client_id, client_secret, redirect_uri):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope='playlist-read-private playlist-modify-private playlist-modify-public'
    ))

def fetch_sp_playlist_tracks(sp, playlist_id, max_songs=0, log=print):
    tracks = []
    offset = 0
    log(f"[SP] Fetching playlist: {playlist_id}")
    while True:
        results = sp.playlist_items(playlist_id, limit=100, offset=offset,
                                     fields='items(track(name,artists)),next')
        for item in results.get('items', []):
            track = item.get('track')
            if not track:
                continue
            name = track['name']
            artist = track['artists'][0]['name'] if track['artists'] else ''
            tracks.append({'title': name, 'artist': artist})
            log(f"[SP] ✓ {name} — {artist}")
            if max_songs and len(tracks) >= max_songs:
                return tracks
        if not results.get('next'):
            break
        offset += 100
    log(f"[SP] Total tracks fetched: {len(tracks)}")
    return tracks

def create_sp_playlist(sp, name, log=print):
    user_id = sp.current_user()['id']
    log(f"[SP] Creating playlist: {name}")
    pl = sp.user_playlist_create(user_id, name, public=False,
                                  description='Imported by Playlist Bridge')
    pl_id = pl['id']
    log(f"[SP] Playlist created: https://open.spotify.com/playlist/{pl_id}")
    return pl_id

def search_and_add_sp_track(sp, playlist_id, title, artist, log=print):
    query = f"track:{clean_title(title)} artist:{artist}" if artist else clean_title(title)
    results = sp.search(q=query, type='track', limit=1)
    items = results['tracks']['items']
    if not items:
        # Fallback: broader search
        results = sp.search(q=clean_title(title), type='track', limit=1)
        items = results['tracks']['items']
    if not items:
        log(f"[SP] ✗ Not found: {title}")
        return False
    uri = items[0]['uri']
    found_name = items[0]['name']
    sp.playlist_add_items(playlist_id, [uri])
    log(f"[SP] ✓ Added: {found_name}")
    return True

# ── Core import logic ─────────────────────────────────────────────────────────

def run_yt_to_sp(config, log, progress):
    yt = get_yt_service(api_key=config['yt_api_key'], oauth_json=config.get('yt_oauth_json'))
    sp = get_sp_client(config['sp_client_id'], config['sp_client_secret'], config['sp_redirect_uri'])

    playlist_id = extract_yt_playlist_id(config['source_id'])
    if not playlist_id:
        raise ValueError("Invalid YouTube playlist URL or ID.")

    tracks = fetch_yt_playlist_tracks(yt, playlist_id, max_songs=config['max_songs'], log=log)
    if not tracks:
        raise ValueError("No tracks found in the YouTube playlist.")

    sp_playlist_id = create_sp_playlist(sp, config['dest_name'], log=log)

    ok = fail = 0
    for i, t in enumerate(tracks, 1):
        success = search_and_add_sp_track(sp, sp_playlist_id, t['title'], t['artist'], log=log)
        if success:
            ok += 1
        else:
            fail += 1
        progress(i, len(tracks))
        time.sleep(0.1)  # be polite to the API

    log(f"\n✅ Done! {ok} added, {fail} not found.")
    log(f"🔗 https://open.spotify.com/playlist/{sp_playlist_id}")

def run_sp_to_yt(config, log, progress):
    sp = get_sp_client(config['sp_client_id'], config['sp_client_secret'], config['sp_redirect_uri'])
    yt = get_yt_service(oauth_json=config.get('yt_oauth_json'))  # OAuth required for write

    playlist_id = extract_sp_playlist_id(config['source_id'])
    if not playlist_id:
        raise ValueError("Invalid Spotify playlist URL or ID.")

    tracks = fetch_sp_playlist_tracks(sp, playlist_id, max_songs=config['max_songs'], log=log)
    if not tracks:
        raise ValueError("No tracks found in the Spotify playlist.")

    yt_playlist_id = create_yt_playlist(yt, config['dest_name'], log=log)

    ok = fail = 0
    for i, t in enumerate(tracks, 1):
        query = f"{t['title']} {t['artist']}"
        success = search_and_add_yt_video(yt, yt_playlist_id, query, log=log)
        if success:
            ok += 1
        else:
            fail += 1
        progress(i, len(tracks))
        time.sleep(0.15)

    log(f"\n✅ Done! {ok} added, {fail} not found.")
    log(f"🔗 https://youtube.com/playlist?list={yt_playlist_id}")

# ── GUI ───────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Playlist Bridge")
        self.geometry("720x780")
        self.resizable(True, True)
        self.configure(bg="#0e0e0e")
        self._build_ui()

    def _lbl(self, parent, text, **kw):
        return tk.Label(parent, text=text, bg="#0e0e0e", fg="#888",
                        font=("Courier", 9), **kw)

    def _entry(self, parent, show=None):
        e = tk.Entry(parent, bg="#1a1a1a", fg="#f0f0f0", insertbackground="#f0f0f0",
                     relief="flat", font=("Courier", 11), bd=0, highlightthickness=1,
                     highlightbackground="#2a2a2a", highlightcolor="#555", show=show or "")
        return e

    def _build_ui(self):
        pad = dict(padx=16, pady=4)
        BG = "#0e0e0e"

        # Title
        tk.Label(self, text="PLAYLIST BRIDGE", bg=BG, fg="#f0f0f0",
                 font=("Courier", 22, "bold")).pack(pady=(20, 2))
        tk.Label(self, text="YouTube  ↔  Spotify  |  API-powered importer", bg=BG, fg="#555",
                 font=("Courier", 10)).pack(pady=(0, 20))

        # ── Direction ──
        frame_dir = tk.LabelFrame(self, text=" Direction ", bg=BG, fg="#666",
                                   font=("Courier", 9), bd=1, relief="flat",
                                   highlightthickness=1, highlightbackground="#2a2a2a")
        frame_dir.pack(fill="x", **pad)

        self.direction = tk.StringVar(value="yt_to_sp")
        rb_frame = tk.Frame(frame_dir, bg=BG)
        rb_frame.pack(fill="x", padx=10, pady=8)
        tk.Radiobutton(rb_frame, text="YouTube  →  Spotify", variable=self.direction,
                       value="yt_to_sp", bg=BG, fg="#f0f0f0", selectcolor="#1a1a1a",
                       activebackground=BG, font=("Courier", 11),
                       command=self._on_direction_change).pack(side="left", padx=(0, 30))
        tk.Radiobutton(rb_frame, text="Spotify  →  YouTube", variable=self.direction,
                       value="sp_to_yt", bg=BG, fg="#f0f0f0", selectcolor="#1a1a1a",
                       activebackground=BG, font=("Courier", 11),
                       command=self._on_direction_change).pack(side="left")

        # ── YouTube creds ──
        frame_yt = tk.LabelFrame(self, text=" YouTube Credentials ", bg=BG, fg="#FF0000",
                                  font=("Courier", 9), bd=1, relief="flat",
                                  highlightthickness=1, highlightbackground="#2a2a2a")
        frame_yt.pack(fill="x", **pad)

        self._lbl(frame_yt, "API Key (read-only tasks):").pack(anchor="w", padx=10, pady=(8,0))
        self.yt_api_key = self._entry(frame_yt, show="•")
        self.yt_api_key.pack(fill="x", padx=10, pady=(2,4), ipady=5)

        self._lbl(frame_yt, "OAuth JSON path (needed to CREATE playlists on YouTube):").pack(anchor="w", padx=10)
        self.yt_oauth_json = self._entry(frame_yt)
        self.yt_oauth_json.pack(fill="x", padx=10, pady=(2,8), ipady=5)
        self.yt_oauth_json.insert(0, "client_secret.json")

        # ── Spotify creds ──
        frame_sp = tk.LabelFrame(self, text=" Spotify Credentials ", bg=BG, fg="#1DB954",
                                  font=("Courier", 9), bd=1, relief="flat",
                                  highlightthickness=1, highlightbackground="#2a2a2a")
        frame_sp.pack(fill="x", **pad)

        row1 = tk.Frame(frame_sp, bg=BG)
        row1.pack(fill="x", padx=10, pady=(8,0))
        col1 = tk.Frame(row1, bg=BG)
        col1.pack(side="left", fill="x", expand=True, padx=(0,8))
        col2 = tk.Frame(row1, bg=BG)
        col2.pack(side="left", fill="x", expand=True)

        self._lbl(col1, "Client ID:").pack(anchor="w")
        self.sp_client_id = self._entry(col1)
        self.sp_client_id.pack(fill="x", ipady=5)

        self._lbl(col2, "Client Secret:").pack(anchor="w")
        self.sp_client_secret = self._entry(col2, show="•")
        self.sp_client_secret.pack(fill="x", ipady=5)

        self._lbl(frame_sp, "Redirect URI (must match your Spotify app settings):").pack(anchor="w", padx=10, pady=(6,0))
        self.sp_redirect_uri = self._entry(frame_sp)
        self.sp_redirect_uri.pack(fill="x", padx=10, pady=(2,8), ipady=5)
        self.sp_redirect_uri.insert(0, "http://localhost:8888/callback")

        # ── Source / Dest ──
        frame_io = tk.LabelFrame(self, text=" Playlist ", bg=BG, fg="#666",
                                  font=("Courier", 9), bd=1, relief="flat",
                                  highlightthickness=1, highlightbackground="#2a2a2a")
        frame_io.pack(fill="x", **pad)

        self._lbl(frame_io, "Source playlist (URL or ID):").pack(anchor="w", padx=10, pady=(8,0))
        self.source_id = self._entry(frame_io)
        self.source_id.pack(fill="x", padx=10, pady=(2,4), ipady=5)

        self._lbl(frame_io, "New destination playlist name:").pack(anchor="w", padx=10)
        self.dest_name = self._entry(frame_io)
        self.dest_name.pack(fill="x", padx=10, pady=(2,4), ipady=5)
        self.dest_name.insert(0, "Imported Playlist")

        self._lbl(frame_io, "Max songs (0 = all):").pack(anchor="w", padx=10)
        self.max_songs = self._entry(frame_io)
        self.max_songs.pack(fill="x", padx=10, pady=(2,8), ipady=5)
        self.max_songs.insert(0, "0")

        # ── Run button ──
        self.run_btn = tk.Button(self, text="▶  RUN IMPORT",
                                  bg="#1DB954", fg="#000", activebackground="#17a348",
                                  font=("Courier", 14, "bold"), relief="flat",
                                  bd=0, padx=20, pady=10, cursor="hand2",
                                  command=self._start_import)
        self.run_btn.pack(fill="x", padx=16, pady=(12, 4))

        # ── Progress ──
        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=16, pady=(0, 4))
        self.progress_lbl = tk.Label(self, text="", bg=BG, fg="#555", font=("Courier", 9))
        self.progress_lbl.pack()

        # ── Log ──
        self.log_box = scrolledtext.ScrolledText(
            self, bg="#080808", fg="#aaa", font=("Courier", 10),
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground="#1a1a1a", wrap="word", height=12
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        self.log_box.tag_config("ok",    foreground="#1DB954")
        self.log_box.tag_config("error", foreground="#ff4444")
        self.log_box.tag_config("warn",  foreground="#ffb700")
        self.log_box.tag_config("info",  foreground="#666")

        self._log("Playlist Bridge ready. Fill in credentials and hit RUN.", "info")

    def _on_direction_change(self):
        pass  # Could swap label hints, currently handled in run logic

    def _log(self, msg, tag=""):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_progress(self, current, total):
        pct = int((current / total) * 100) if total else 0
        self.progress["value"] = pct
        self.progress_lbl.config(text=f"{current} / {total}  ({pct}%)")
        self.update_idletasks()

    def _start_import(self):
        self.run_btn.config(state="disabled", text="⏳  Running...")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.progress["value"] = 0
        threading.Thread(target=self._run_import_thread, daemon=True).start()

    def _run_import_thread(self):
        def log(msg):
            tag = "ok" if "✓" in msg else ("error" if "✗" in msg else "")
            self.after(0, lambda m=msg, t=tag: self._log(m, t))

        def progress(cur, total):
            self.after(0, lambda c=cur, t=total: self._set_progress(c, t))

        try:
            config = {
                "yt_api_key":       self.yt_api_key.get().strip() or None,
                "yt_oauth_json":    self.yt_oauth_json.get().strip() or None,
                "sp_client_id":     self.sp_client_id.get().strip(),
                "sp_client_secret": self.sp_client_secret.get().strip(),
                "sp_redirect_uri":  self.sp_redirect_uri.get().strip(),
                "source_id":        self.source_id.get().strip(),
                "dest_name":        self.dest_name.get().strip() or "Imported Playlist",
                "max_songs":        int(self.max_songs.get().strip() or 0),
            }

            direction = self.direction.get()
            if direction == "yt_to_sp":
                if not config["yt_api_key"]:
                    raise ValueError("YouTube API Key is required for YouTube → Spotify.")
                if not config["sp_client_id"] or not config["sp_client_secret"]:
                    raise ValueError("Spotify Client ID and Secret are required.")
                run_yt_to_sp(config, log=log, progress=progress)
            else:
                if not config["sp_client_id"] or not config["sp_client_secret"]:
                    raise ValueError("Spotify Client ID and Secret are required.")
                if not config["yt_oauth_json"] or not os.path.exists(config["yt_oauth_json"]):
                    raise ValueError("YouTube OAuth JSON file is required for Spotify → YouTube (API key is read-only).")
                run_sp_to_yt(config, log=log, progress=progress)

        except Exception as e:
            self.after(0, lambda: self._log(f"\n❌ ERROR: {e}", "error"))
        finally:
            self.after(0, lambda: self.run_btn.config(state="normal", text="▶  RUN IMPORT"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
