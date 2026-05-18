import os
import webbrowser
import threading
import tkinter as tk
import numpy as np
import pyaudio
import time
import torch
import requests
import psutil
import subprocess
import glob
import pygame
from faster_whisper import WhisperModel
from difflib import SequenceMatcher
from PIL import Image, ImageTk

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
torch.set_num_threads(os.cpu_count())

MODEL_SIZE = "large-v3-turbo"
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 500
CF_HANDLE = "Megatron_HACKER"

SAD_WORDS = ["why", "how", "sad", "cry", "crying", "depressed", "alone", "hurt",
             "pain", "sorry", "miss", "lost", "broken", "hate", "tired", "lonely",
             "upset", "angry", "bad", "awful", "terrible", "horrible", "dead",
             "die", "death", "fail", "failed", "ugly", "stupid", "dumb", "idiot",
             "scared", "afraid", "nervous", "anxious", "stress", "stressed", "worried"]

SANS_CONTEST_MSG = "It's time for coding, human. You CAN'T escape this genocide. You will have a BAD TIME."

KILL_MAP = {
    "google":    ["chrome", "googledrivesync", "googleupdate", "google"],
    "chrome":    ["chrome"],
    "discord":   ["discord"],
    "spotify":   ["spotify"],
    "steam":     ["steam"],
    "minecraft": ["minecraft", "javaw"],
    "firefox":   ["firefox"],
    "edge":      ["msedge"],
    "telegram":  ["telegram"],
    "zoom":      ["zoom"],
    "skype":     ["skype"],
    "vlc":       ["vlc"],
    "notepad":   ["notepad"],
    "word":      ["winword"],
    "excel":     ["excel"],
}

OPEN_MAP = {
    "google":        "https://www.google.com",
    "youtube":       "https://www.youtube.com",
    "codeforces":    "https://codeforces.com",
    "leetcode":      "https://leetcode.com",
    "github":        "https://www.github.com",
    "reddit":        "https://www.reddit.com",
    "twitter":       "https://www.twitter.com",
    "discord":       "https://www.discord.com",
    "spotify":       "https://open.spotify.com",
    "netflix":       "https://www.netflix.com",
    "twitch":        "https://www.twitch.tv",
    "gmail":         "https://mail.google.com",
    "instagram":     "https://www.instagram.com",
    "facebook":      "https://www.facebook.com",
    "steam":         "https://store.steampowered.com",
    "wikipedia":     "https://www.wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
}

QUICK_PATHS = {
    "discord":   [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Discord", "Update.exe")],
    "spotify":   [os.path.join(os.environ.get("APPDATA", ""), "Spotify", "Spotify.exe")],
    "steam":     ["C:\\Program Files (x86)\\Steam\\steam.exe", "C:\\Program Files\\Steam\\steam.exe"],
    "chrome":    ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"],
    "firefox":   ["C:\\Program Files\\Mozilla Firefox\\firefox.exe"],
    "edge":      ["C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"],
    "telegram":  [os.path.join(os.environ.get("APPDATA", ""), "Telegram Desktop", "Telegram.exe")],
    "vlc":       ["C:\\Program Files\\VideoLAN\\VLC\\vlc.exe"],
    "zoom":      [os.path.join(os.environ.get("APPDATA", ""), "Zoom", "bin", "Zoom.exe")],
    "notepad":   ["C:\\Windows\\System32\\notepad.exe"],
    "calculator":["C:\\Windows\\System32\\calc.exe"],
    "paint":     ["C:\\Windows\\System32\\mspaint.exe"],
    "word":      ["C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"],
    "excel":     ["C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE"],
}

SEARCH_PATHS = [
    os.environ.get("PROGRAMFILES", "C:\\Program Files"),
    os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
    os.path.join(os.environ.get("APPDATA", ""), "..\\Local"),
    os.path.join(os.environ.get("APPDATA", "")),
    "C:\\Windows\\System32",
]

RUN_MAP = {
    "notepad":    "notepad.exe",
    "calculator": "calc.exe",
    "paint":      "mspaint.exe",
    "discord":    "discord.exe",
    "spotify":    "spotify.exe",
    "steam":      "steam.exe",
    "chrome":     "chrome.exe",
    "firefox":    "firefox.exe",
    "edge":       "msedge.exe",
    "telegram":   "telegram.exe",
    "vlc":        "vlc.exe",
    "zoom":       "zoom.exe",
    "word":       "winword.exe",
    "excel":      "excel.exe",
    "skype":      "skype.exe",
    "minecraft":  "minecraft.exe",
}

def fuzzy_match(text, keyword, threshold=0.75):
    text = text.lower()
    keyword = keyword.lower()
    if keyword in text:
        return True
    words = text.split()
    kwords = keyword.split()
    window = len(kwords)
    for i in range(len(words) - window + 1):
        chunk = " ".join(words[i:i+window])
        if SequenceMatcher(None, chunk, keyword).ratio() >= threshold:
            return True
    return False

def fuzzy_best_match(word, candidates, threshold=0.6):
    best, best_score = None, 0
    for c in candidates:
        score = SequenceMatcher(None, word, c).ratio()
        if score > best_score:
            best, best_score = c, score
    return best if best_score >= threshold else None

def find_exe(name):
    best_key = fuzzy_best_match(name, list(QUICK_PATHS.keys()) + list(RUN_MAP.keys()), threshold=0.6)
    if best_key and best_key in QUICK_PATHS:
        for path in QUICK_PATHS[best_key]:
            if os.path.exists(path):
                return path
    exe_name = RUN_MAP.get(best_key, f"{name}.exe") if best_key else f"{name}.exe"
    for base in SEARCH_PATHS:
        if not base or not os.path.exists(base):
            continue
        pattern = os.path.join(base, "**", exe_name)
        results = glob.glob(pattern, recursive=True)
        if results:
            return results[0]
    return None

def handle_run(target):
    target = target.lower().strip()
    path = find_exe(target)
    if path:
        try:
            subprocess.Popen([path])
            return True, path
        except Exception as e:
            return False, str(e)
    return False, None

def handle_kill(target):
    target = target.lower().strip()
    killed = []
    patterns = None
    for key in KILL_MAP:
        if fuzzy_match(target, key):
            patterns = KILL_MAP[key]
            break
    if not patterns:
        patterns = [target]
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pname = proc.info["name"].lower().replace(".exe", "")
            for pat in patterns:
                if pat in pname or fuzzy_match(pname, pat, threshold=0.7):
                    proc.kill()
                    killed.append(proc.info["name"])
                    break
        except Exception:
            pass
    return killed

def handle_open(target):
    target = target.lower().strip()
    best = fuzzy_best_match(target, list(OPEN_MAP.keys()), threshold=0.6)
    url = OPEN_MAP[best] if best else f"https://www.{target}com"
    return url

def parse_command(text):
    text_lower = text.lower().strip()
    words = text_lower.split()
    for i, word in enumerate(words):
        if fuzzy_match(word, "kill", threshold=0.8) and i + 1 < len(words):
            return "kill", " ".join(words[i+1:])
        if fuzzy_match(word, "close", threshold=0.8) and i + 1 < len(words):
            return "kill", " ".join(words[i+1:])
        if fuzzy_match(word, "open", threshold=0.8) and i + 1 < len(words):
            return "open", " ".join(words[i+1:])
        if fuzzy_match(word, "launch", threshold=0.8) and i + 1 < len(words):
            return "open", " ".join(words[i+1:])
        if fuzzy_match(word, "run", threshold=0.8) and i + 1 < len(words):
            return "run", " ".join(words[i+1:])
        if fuzzy_match(word, "start", threshold=0.8) and i + 1 < len(words):
            return "run", " ".join(words[i+1:])
    return None, None

# ─── SANS WINDOW ─────────────────────────────────────────────────────────────

class SansWindow:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "#010101")
        self.root.configure(bg="#010101")

        self.SANS_W = 225
        self.SANS_H = 225
        self.BOX_W = 260
        self.GAP = 10
        self.PAD = 10
        self.FONT = ("Courier New", 11, "bold")
        self.SPEED = 35
        self.SANSANG_LINGER = 2000
        self._stop_typing = False
        self._current_mode = "normal"
        self._current_sprite_name = "sans"
        self.commands_blocked = False
        self._verdict_lock = False

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        self.pil_sprites = {}
        self.sprites = {}
        for name in ["sans", "sanslis", "sansproceed", "sanser", "sansad", "sansang", "sanswar", "sanswin"]:
            try:
                img = Image.open(f"{name}.png").convert("RGBA")
                img = img.resize((self.SANS_W, self.SANS_H), Image.NEAREST)
                self.pil_sprites[name] = img
                self.sprites[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"[warn] could not load {name}.png: {e}")
                self.pil_sprites[name] = self.pil_sprites.get("sans")
                self.sprites[name] = self.sprites.get("sans")

        self.canvas = tk.Canvas(self.root, width=self.BOX_W, bg="#010101", highlightthickness=0)
        self.canvas.pack()

        sans_x = (self.BOX_W - self.SANS_W) // 2
        self.canvas.create_image(sans_x, 0, anchor="nw",
                                 image=self.sprites["sans"], tags="sans")

        self.box_y = self.SANS_H + self.GAP
        self.canvas.create_rectangle(
            0, self.box_y, self.BOX_W, self.box_y + 40,
            fill="#0d0000", outline="white", width=2, tags="box"
        )
        self.canvas.create_text(
            self.PAD, self.box_y + self.PAD,
            text="", anchor="nw",
            fill="white", font=self.FONT,
            width=self.BOX_W - self.PAD * 2,
            tags="txt"
        )

        self._update_box_size("")
        self._center_window()

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self._drag_x = 0
        self._drag_y = 0

    def set_sprite(self, name):
        if self._verdict_lock:
            return
        sprite = self.sprites.get(name, self.sprites.get("sans"))
        if sprite:
            self._current_sprite_name = name
            self.canvas.itemconfig("sans", image=sprite)
            self.canvas.image = sprite

    def crossfade_to(self, target_name, steps=25, delay=40, on_done=None):
        src = self.pil_sprites.get(self._current_sprite_name, self.pil_sprites.get("sans"))
        dst = self.pil_sprites.get(target_name, self.pil_sprites.get("sans"))
        if src is None or dst is None:
            self._current_sprite_name = target_name
            if on_done:
                on_done()
            return
        self._crossfade_step(src, dst, target_name, 0, steps, delay, on_done)

    def _crossfade_step(self, src, dst, target_name, step, steps, delay, on_done):
        alpha = step / steps
        blended = Image.blend(src.convert("RGBA"), dst.convert("RGBA"), alpha)
        photo = ImageTk.PhotoImage(blended)
        self.canvas.itemconfig("sans", image=photo)
        self.canvas.image = photo

        if step >= steps:
            self._current_sprite_name = target_name
            if on_done:
                on_done()
            return

        self.root.after(delay, lambda: self._crossfade_step(
            src, dst, target_name, step + 1, steps, delay, on_done))

    def play_sound(self, wav_file):
        try:
            pygame.mixer.music.load(wav_file)
            pygame.mixer.music.play()
            print(f"[sound] playing {wav_file}")
        except Exception as e:
            print(f"[sound err] {e}")

    def stop_sound(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def _wait_for_music_end(self):
        if pygame.mixer.music.get_busy():
            self.root.after(500, self._wait_for_music_end)
        else:
            self.root.after(1000, self._end_verdict)

    def trigger_verdict(self, verdict):
        self.commands_blocked = True
        self._stop_typing = True
        self._verdict_lock = True

        if verdict == "AC":
            sprite = "sanswin"
            wav = "sanswin.wav"
            msg = "You did it kid.Do some more!"
        else:
            sprite = "sanswar"
            wav = "sanswar.wav"
            msg = "That WA/TLE was unexcpected.What have u done kid..."

        def after_fade():
            self.play_sound(wav)
            self._stop_typing = False
            self.canvas.itemconfig("txt", text="")
            self._update_box_size("")
            self._type_letter(f"* {msg}", 0, None)
            self._wait_for_music_end()

        self.crossfade_to(sprite, steps=25, delay=40, on_done=after_fade)

    def _end_verdict(self):
        self._verdict_lock = False
        self.stop_sound()
        self.crossfade_to("sanslis", steps=25, delay=40,
                          on_done=lambda: setattr(self, "commands_blocked", False))

    def speak(self, text, mode="normal", on_done=None):
        if self._verdict_lock:
            return
        self._stop_typing = True
        self.root.after(100, lambda: self._start_typewriter(text, mode, on_done))

    def _start_typewriter(self, full_text, mode, on_done):
        self._stop_typing = False
        self._current_mode = mode
        self.canvas.itemconfig("txt", text="")
        self._update_box_size("")

        if not self._verdict_lock:
            if mode == "sad":
                self.set_sprite("sansad")
            elif mode in ("command", "contest", "kill", "run"):
                self.set_sprite("sansang")
            else:
                self.set_sprite("sanslis")

        self._type_letter(f"* {full_text.lower()}.", 0, on_done)

    def _type_letter(self, full_text, i, on_done):
        if self._stop_typing:
            return
        if i > len(full_text):
            if not self._verdict_lock:
                linger = self.SANSANG_LINGER if self._current_mode in ("command", "contest", "kill", "run") else 1000
                if on_done:
                    self.root.after(linger, on_done)
                else:
                    self.root.after(linger, lambda: self.set_sprite("sanslis"))
            return
        self.canvas.itemconfig("txt", text=full_text[:i])
        self._update_box_size(full_text[:i])
        self.root.after(self.SPEED, lambda: self._type_letter(full_text, i + 1, on_done))

    def _update_box_size(self, text):
        self.root.update_idletasks()
        bbox = self.canvas.bbox("txt")
        text_h = (bbox[3] - bbox[1]) if bbox else 16
        box_h = text_h + self.PAD * 2
        total_h = self.SANS_H + self.GAP + box_h
        self.canvas.coords("box", 0, self.box_y, self.BOX_W, self.box_y + box_h)
        self.canvas.coords("txt", self.PAD, self.box_y + self.PAD)
        self.canvas.config(height=total_h)
        self.root.geometry(f"{self.BOX_W}x{total_h}")

    def _center_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw//2}+{sh//2}")

    def start_drag(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def do_drag(self, e):
        x = self.root.winfo_x() + e.x - self._drag_x
        y = self.root.winfo_y() + e.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")


# ─── CF SUBMISSION CHECKER ───────────────────────────────────────────────────

class CFChecker:
    def __init__(self, sans, handle):
        self.sans = sans
        self.handle = handle
        self.seen_ids = set()
        self.running = True
        self._init_seen()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _init_seen(self):
        try:
            resp = requests.get(
                f"https://codeforces.com/api/user.status?handle={self.handle}&from=1&count=10",
                timeout=10)
            data = resp.json()
            if data.get("status") == "OK":
                for sub in data["result"]:
                    self.seen_ids.add(sub["id"])
                print(f"[CF] loaded {len(self.seen_ids)} existing submissions")
        except Exception as e:
            print(f"[CF init err] {e}")

    def _loop(self):
        while self.running:
            try:
                self._check()
            except Exception as e:
                print(f"[CF checker err] {e}")
            time.sleep(3)

    def _check(self):
        resp = requests.get(
            f"https://codeforces.com/api/user.status?handle={self.handle}&from=1&count=5",
            timeout=10)
        data = resp.json()
        if data.get("status") != "OK":
            return

        for sub in data["result"]:
            sid = sub["id"]
            if sid in self.seen_ids:
                continue
            verdict = sub.get("verdict", "")
            if not verdict or verdict == "TESTING":
                continue

            self.seen_ids.add(sid)

            if verdict == "OK":
                self.sans.root.after(0, self.sans.trigger_verdict, "AC")
            else:
                self.sans.root.after(0, self.sans.trigger_verdict, "WA")
            break

    def stop(self):
        self.running = False


# ─── CONTEST CHECKER ─────────────────────────────────────────────────────────

class ContestChecker:
    def __init__(self, sans):
        self.sans = sans
        self.notified = set()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while self.running:
            try:
                self._check()
            except Exception as e:
                print(f"[contest checker err] {e}")
            time.sleep(60)

    def _check(self):
        resp = requests.get("https://codeforces.com/api/contest.list", timeout=10)
        data = resp.json()
        if data.get("status") != "OK":
            return
        now = time.time()
        for contest in data["result"]:
            if contest.get("phase") != "BEFORE":
                continue
            contest_id = contest["id"]
            start = contest["startTimeSeconds"]
            mins_until = (start - now) / 60
            if 4 <= mins_until <= 6 and contest_id not in self.notified:
                self.notified.add(contest_id)
                url = f"https://codeforces.com/contest/{contest_id}"
                self.sans.root.after(0, self._trigger, url)
                break

    def _trigger(self, url):
        def open_cf():
            webbrowser.open(url)
            self.sans.set_sprite("sanslis")
        self.sans.speak(SANS_CONTEST_MSG, "contest", open_cf)

    def stop(self):
        self.running = False


# ─── WHISPER WINDOW ───────────────────────────────────────────────────────────

class WhisperApp:
    def __init__(self, root, sans):
        self.root = root
        self.sans = sans
        self.root.title("Whisper Pro - Large-V3-Turbo")
        self.root.geometry("500x600")
        self.root.configure(bg="#0f0f0f")

        tk.Label(root, text="MIC SENSITIVITY", fg="#555", bg="#0f0f0f", font=("Arial", 7)).pack(pady=(10,0))
        self.canvas = tk.Canvas(root, width=400, height=12, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.bar = self.canvas.create_rectangle(0, 0, 0, 12, fill="#00ffcc", outline="")

        self.status_box = tk.Label(root, text="LOADING MODEL...", fg="white", bg="#333",
                                   font=("Consolas", 11, "bold"), width=22, pady=8)
        self.status_box.pack(pady=15)

        self.textbox = tk.Text(root, height=16, width=55, bg="#161616", fg="#00ffcc",
                               font=("Consolas", 10), padx=15, pady=15, borderwidth=0)
        self.textbox.pack(pady=10)

        btn_frame = tk.Frame(root, bg="#0f0f0f")
        btn_frame.pack(pady=(0, 10))

        tk.Button(btn_frame, text="CLEAR", command=lambda: self.textbox.delete("1.0", tk.END),
                  bg="#222", fg="#888", font=("Consolas", 9), relief="flat", padx=10).pack(side="left", padx=5)

        tk.Button(btn_frame, text="TEST CONTEST", command=self.test_contest,
                  bg="#330000", fg="#ff4444", font=("Consolas", 9), relief="flat", padx=10).pack(side="left", padx=5)

        tk.Button(btn_frame, text="TEST AC", command=lambda: self.sans.root.after(0, self.sans.trigger_verdict, "AC"),
                  bg="#003300", fg="#00ff00", font=("Consolas", 9), relief="flat", padx=10).pack(side="left", padx=5)

        tk.Button(btn_frame, text="TEST WA", command=lambda: self.sans.root.after(0, self.sans.trigger_verdict, "WA"),
                  bg="#330000", fg="#ff4444", font=("Consolas", 9), relief="flat", padx=10).pack(side="left", padx=5)

        self.running = True
        self.last_trigger_time = 0

        self.thread = threading.Thread(target=self.audio_engine, daemon=True)
        self.thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def test_contest(self):
        try:
            resp = requests.get("https://codeforces.com/api/contest.list", timeout=10)
            data = resp.json()
            if data.get("status") == "OK":
                for contest in data["result"]:
                    if contest.get("phase") == "BEFORE":
                        url = f"https://codeforces.com/contest/{contest['id']}"
                        def open_cf(u=url):
                            webbrowser.open(u)
                            self.sans.set_sprite("sanslis")
                        self.sans.root.after(0, self.sans.speak, SANS_CONTEST_MSG, "contest", open_cf)
                        return
        except Exception as e:
            self.root.after(0, self.update_text, f"[test contest err] {e}\n")

    def update_ui_status(self, mode):
        colors = {
            "listening": ("● LISTENING", "#005fcc"),
            "thinking":  ("🧠 THINKING",  "#cc9900"),
            "ready":     ("READY",        "#00cc66"),
            "error":     ("⚠ RESTARTING", "#cc5500"),
        }
        txt, clr = colors.get(mode, ("...", "#333"))
        self.status_box.config(text=txt, bg=clr)

    def open_stream(self, p):
        time.sleep(0.5)
        try:
            return p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=2,
                frames_per_buffer=CHUNK_SIZE
            )
        except OSError as e:
            self.root.after(0, self.update_text, f"[stream error] {e}\n")
            return None

    def audio_engine(self):
        try:
            model = WhisperModel(
                MODEL_SIZE,
                device="cpu",
                compute_type="int8",
                cpu_threads=os.cpu_count(),
                num_workers=4
            )
        except Exception as e:
            self.root.after(0, self.update_text, f"Model load failed: {e}\n")
            return

        self.root.after(0, self.update_ui_status, "ready")
        self.sans.root.after(0, self.sans.set_sprite, "sanslis")

        while self.running:
            p = pyaudio.PyAudio()
            stream = self.open_stream(p)

            if stream is None:
                self.root.after(0, self.update_ui_status, "error")
                self.sans.root.after(0, self.sans.set_sprite, "sanser")
                p.terminate()
                time.sleep(2)
                continue

            self.sans.root.after(0, self.sans.set_sprite, "sanslis")
            stream_dead = False

            while self.running and not stream_dead:
                self.root.after(0, self.update_ui_status, "listening")

                frames = []
                voice_active = False
                silence_chunks = 0
                MAX_SILENCE = int(SAMPLE_RATE / CHUNK_SIZE * 2.5)

                while True:
                    if not self.running or stream_dead:
                        break
                    try:
                        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    except OSError as e:
                        self.root.after(0, self.update_text, f"[read err, restarting] {e}\n")
                        self.sans.root.after(0, self.sans.set_sprite, "sanser")
                        stream_dead = True
                        break

                    audio_np = np.frombuffer(data, dtype=np.int16)
                    rms = np.std(audio_np)
                    self.root.after(0, self.canvas.coords, self.bar, 0, 0, min(400, (rms / 2000) * 400), 12)

                    if rms > SILENCE_THRESHOLD:
                        voice_active = True
                        silence_chunks = 0
                        frames.append(audio_np)
                    elif voice_active:
                        frames.append(audio_np)
                        silence_chunks += 1
                        if silence_chunks >= MAX_SILENCE:
                            break

                if stream_dead:
                    continue
                if not voice_active or not self.running:
                    continue

                if self.sans.commands_blocked:
                    continue

                self.root.after(0, self.update_ui_status, "thinking")
                self.sans.root.after(0, self.sans.set_sprite, "sansproceed")
                audio_data = np.concatenate(frames).astype(np.float32) / 32768.0

                try:
                    segments, _ = model.transcribe(
                        audio_data,
                        beam_size=5,
                        best_of=5,
                        vad_filter=True,
                        vad_parameters=dict(
                            min_silence_duration_ms=250,
                            speech_pad_ms=150,
                        ),
                        temperature=0.0,
                        condition_on_previous_text=False,
                        initial_prompt="Open Google, kill Chrome, run Discord, open Codeforces.",
                        language="en",
                        no_speech_threshold=0.5,
                    )
                except Exception as e:
                    self.root.after(0, self.update_text, f"[transcribe err] {e}\n")
                    self.sans.root.after(0, self.sans.set_sprite, "sanslis")
                    continue

                full_text = ""
                for segment in segments:
                    if segment.no_speech_prob < 0.4:
                        full_text += segment.text.strip() + " "

                full_text = full_text.strip()
                if not full_text:
                    self.sans.root.after(0, self.sans.set_sprite, "sanslis")
                    continue

                self.root.after(0, self.update_text, f">> {full_text}\n")

                action, target = parse_command(full_text)
                text_lower = full_text.lower()

                if action == "kill":
                    def do_kill_after(t=target):
                        killed = handle_kill(t)
                        if killed:
                            self.root.after(0, self.update_text, f"[killed] {', '.join(set(killed))}\n")
                        else:
                            self.root.after(0, self.update_text, f"[kill] nothing found for: {t}\n")
                        self.sans.root.after(0, self.sans.set_sprite, "sanslis")
                    self.sans.root.after(0, self.sans.speak, full_text, "kill",
                                         lambda: threading.Thread(target=do_kill_after, daemon=True).start())

                elif action == "run":
                    def do_run_after(t=target):
                        success, result = handle_run(t)
                        if success:
                            self.root.after(0, self.update_text, f"[launched] {result}\n")
                        else:
                            self.root.after(0, self.update_text, f"[run] couldn't find {t}\n")
                        self.sans.root.after(0, self.sans.set_sprite, "sanslis")
                    self.sans.root.after(0, self.sans.speak, full_text, "run",
                                         lambda: threading.Thread(target=do_run_after, daemon=True).start())

                elif action == "open":
                    url = handle_open(target)
                    self.root.after(0, self.update_text, f"[opening] {url}\n")
                    def do_open(u=url):
                        webbrowser.open(u)
                        self.sans.set_sprite("sanslis")
                    self.sans.root.after(0, self.sans.speak, full_text, "command", do_open)

                else:
                    is_sad = any(word in text_lower for word in SAD_WORDS)
                    if is_sad:
                        self.sans.root.after(0, self.sans.speak, full_text, "sad", None)
                    else:
                        self.sans.root.after(0, self.sans.speak, full_text, "normal", None)

            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            p.terminate()

            if self.running:
                time.sleep(2)

    def update_text(self, text):
        self.textbox.insert(tk.END, text)
        self.textbox.see(tk.END)

    def on_closing(self):
        self.running = False
        self.root.destroy()


# ─── LAUNCH ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pygame.init()

    sans_root = tk.Tk()
    sans = SansWindow(sans_root)

    whisper_root = tk.Toplevel(sans_root)
    app = WhisperApp(whisper_root, sans)

    contest_checker = ContestChecker(sans)
    cf_checker = CFChecker(sans, CF_HANDLE)

    sans_root.mainloop()
    contest_checker.stop()
    cf_checker.stop()
