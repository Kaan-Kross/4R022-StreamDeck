"""
4R022 StreamDeck 2.0V
==============================
Fiziksel "stream deck" cihazlarının yazılım karşılığı.
Klavyeden çağrılan, uygulama/web kısayollarını ikon + isim olarak
gösteren, tamamen ayarlanabilir kayan bir panel.

Geliştiren: 4R022
"""

import os
import sys
import json
import time
import hashlib
import threading
import traceback
import webbrowser
from io import BytesIO
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ----------------------------------------------------------------------------
# Opsiyonel bağımlılıklar (yoksa uygulama yine de düşmeden, sade modda çalışır)
# ----------------------------------------------------------------------------
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import win32gui
    import win32ui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    from screeninfo import get_monitors as _sc_get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False


# ==============================================================================
# YOLLAR / SABİTLER
# ==============================================================================
APP_NAME = "4R022"
PRODUCT_NAME = "StreamDeck"
APP_VERSION = "2.0V"
FULL_TITLE = f"{APP_NAME} {PRODUCT_NAME} {APP_VERSION}"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / APP_NAME
CONFIG_PATH = APP_DIR / "config.json"
ICON_CACHE_DIR = APP_DIR / "icon_cache"
LOG_PATH = APP_DIR / "hata.log"

APP_DIR.mkdir(parents=True, exist_ok=True)
ICON_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def resource_path(relative_path: str) -> str:
    """
    Hem 'python 4R022_StreamDeck.pyw' ile doğrudan çalıştırılırken hem de
    PyInstaller ile tek dosya .exe'ye paketlenmişken (sys._MEIPASS geçici
    açılış klasörünü gösterir) assets/ klasöründeki dosyaları doğru bulur.
    """
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


APP_ICON_PATH = resource_path(os.path.join("assets", "icon.ico"))
APP_LOGO_PNG_PATH = resource_path(os.path.join("assets", "icon.png"))
_logo_photo_cache = {}


def _load_logo_photo(size=40):
    """Ayarlar gibi pencerelerde marka logosunu küçük bir rozet olarak gösterir."""
    if not PIL_AVAILABLE:
        return None
    if size in _logo_photo_cache:
        return _logo_photo_cache[size]
    try:
        if not os.path.exists(APP_LOGO_PNG_PATH):
            return None
        img = Image.open(APP_LOGO_PNG_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _logo_photo_cache[size] = photo
        return photo
    except Exception:
        return None

DEFAULT_CONFIG = {
    "panel": {
        "width": 300,
        "height": 540,
        "y": 100,
        "bg": "#0c0c0c",
        "accent": "#ff2323",
        "accent_dim": "#5a0d0d",
        "tile_bg": "#1a1a1a",
        "tile_hover": "#262626",
        "text": "#f2f2f2",
        "sub_text": "#9a9a9a",
        "corner_radius": 18,
        "columns": 2,
        "monitor_index": 0
    },
    "clock": {
        "corner": "bottom-right",   # bottom-left, bottom-right, top-left, top-right
        "show_date": True,
        "font_size": 12
    },
    "hotkeys": {
        "toggle": "-",
        "close_combo": ["k", "r", "s"],
        "combo_window": 1.0
    },
    "apps": [
        {"id": "chrome",  "name": "Chrome",   "type": "exe", "target": r"C:\Program Files\Google\Chrome\Application\chrome.exe", "hotkey": None},
        {"id": "youtube", "name": "YouTube",  "type": "url", "target": "https://youtube.com", "hotkey": None},
        {"id": "discord", "name": "Discord",  "type": "url", "target": "https://discord.com/app", "hotkey": None},
        {"id": "steam",   "name": "Steam",    "type": "exe", "target": r"C:\Program Files (x86)\Steam\Steam.exe", "hotkey": None},
        {"id": "chatgpt", "name": "ChatGPT",  "type": "url", "target": "https://chat.openai.com", "hotkey": None},
        {"id": "dosyalar","name": "Dosyalar", "type": "exe", "target": r"C:\Windows\explorer.exe", "hotkey": None}
    ]
}

CORNER_LABELS = {
    "bottom-right": "Sağ Alt",
    "bottom-left": "Sol Alt",
    "top-right": "Sağ Üst",
    "top-left": "Sol Üst",
}


def log_error(context=""):
    """.pyw dosyasında konsol olmadığı için hatalar dosyaya yazılır."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().isoformat()}] {context}\n")
            f.write(traceback.format_exc())
            f.write("\n" + "-" * 60 + "\n")
    except Exception:
        pass


def get_monitors(root):
    """
    Sistemdeki tüm monitörleri {index, name, x, y, width, height} olarak döndürür.
    'screeninfo' kuruluysa gerçek çoklu monitör bilgisini verir; değilse
    tek monitör (Tk'nin gördüğü ana ekran) olarak fallback yapar — hiçbir
    zaman boş liste dönmez, çökmez.
    """
    monitors = []
    if SCREENINFO_AVAILABLE:
        try:
            for i, m in enumerate(_sc_get_monitors()):
                monitors.append({
                    "index": i,
                    "name": m.name or f"Ekran {i + 1}",
                    "x": m.x, "y": m.y,
                    "width": m.width, "height": m.height,
                })
        except Exception:
            log_error("Monitörler alınamadı (screeninfo)")

    if not monitors:
        monitors = [{
            "index": 0, "name": "Ana Ekran", "x": 0, "y": 0,
            "width": root.winfo_screenwidth(), "height": root.winfo_screenheight(),
        }]
    return monitors


# ==============================================================================
# CONFIG YÖNETİMİ
# ==============================================================================
class ConfigManager:
    def __init__(self, path: Path, defaults: dict):
        self.path = path
        self.defaults = defaults
        self.data = self._load()
        self.icons = None  # main() tarafından sonradan bağlanır (ikon önbelleğini geçersiz kılmak için)

    def _deep_merge(self, base, override):
        result = dict(base)
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = self._deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                return self._deep_merge(self.defaults, user_cfg)
            except Exception:
                log_error("Config okunamadı, varsayılan kullanılıyor")
        return json.loads(json.dumps(self.defaults))  # derin kopya

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            log_error("Config kaydedilemedi")

    # -- kısayollar --
    def add_app(self, app: dict):
        app["id"] = hashlib.md5((app["name"] + app["target"]).encode("utf-8")).hexdigest()[:10]
        self.data["apps"].append(app)
        self.save()
        return app

    def remove_app(self, app_id: str):
        self.data["apps"] = [a for a in self.data["apps"] if a["id"] != app_id]
        self.save()

    def update_app(self, app_id: str, **fields):
        for a in self.data["apps"]:
            if a["id"] == app_id:
                a.update(fields)
        self.save()
        if self.icons is not None:
            self.icons.invalidate(app_id)  # hedef/isim değişmiş olabilir, ikon yeniden üretilsin


# ==============================================================================
# İKON YÖNETİMİ (uygulama ikonunu çıkarır / önbelleğe alır / yoksa üretir)
# ==============================================================================
class IconManager:
    TILE_SIZE = 56

    def __init__(self):
        self._cache = {}

    def get(self, app: dict):
        """Verilen kısayol için bir tk.PhotoImage döndürür (her zaman)."""
        key = app["id"]
        if key in self._cache:
            return self._cache[key]

        img = None
        if PIL_AVAILABLE:
            if app["type"] == "exe" and WIN32_AVAILABLE:
                img = self._extract_exe_icon(app["target"])
            elif app["type"] == "url":
                img = self._fetch_web_icon(app["target"])
            if img is None:
                img = self._generate_letter_icon(app["name"])

        if img is not None:
            photo = ImageTk.PhotoImage(img)
        else:
            # PIL yoksa boş bırak; buton sadece metinle gösterilecek
            photo = None

        self._cache[key] = photo
        return photo

    def invalidate(self, app_id: str):
        """Bir kısayolun hedefi/ismi değiştiğinde önbellekten düşürür."""
        self._cache.pop(app_id, None)

    def _fetch_web_icon(self, url: str):
        """
        Web sitesinin gerçek favicon'unu indirir (ör. YouTube kısayolunda
        YouTube'un kendi ikonu görünür). İnternet yoksa / indirilemezse
        None döner ve otomatik harf-rozetine düşülür.
        """
        if not REQUESTS_AVAILABLE:
            return None
        try:
            domain = urlparse(url).netloc or urlparse(url).path
            domain = domain.replace("www.", "").strip("/")
            if not domain:
                return None
        except Exception:
            return None

        cache_file = ICON_CACHE_DIR / (hashlib.md5(domain.encode("utf-8")).hexdigest() + "_web.png")
        if cache_file.exists():
            try:
                return Image.open(cache_file).convert("RGBA")
            except Exception:
                pass

        # Birkaç favicon kaynağı sırayla denenir (biri engelliyse/başarısızsa diğerine geçilir)
        sources = [
            f"https://www.google.com/s2/favicons?sz=128&domain={domain}",
            f"https://icons.duckduckgo.com/ip3/{domain}.ico",
            f"https://{domain}/favicon.ico",
        ]
        for src in sources:
            try:
                resp = requests.get(src, timeout=4, headers={"User-Agent": "Mozilla/5.0"})
                resp.raise_for_status()
                raw = Image.open(BytesIO(resp.content)).convert("RGBA")
                if raw.size[0] < 16:  # bazı kaynaklar 1x1 boş görsel döndürebilir
                    continue

                icon = raw.resize((self.TILE_SIZE, self.TILE_SIZE), Image.LANCZOS)
                # beyaz zemin + yuvarlak köşe maskesi: her favicon (şeffaf/kare/vs.)
                # panel stiliyle tutarlı görünsün
                canvas_img = Image.new("RGBA", (self.TILE_SIZE, self.TILE_SIZE), (255, 255, 255, 255))
                canvas_img.alpha_composite(icon)
                mask = Image.new("L", (self.TILE_SIZE, self.TILE_SIZE), 0)
                ImageDraw.Draw(mask).rounded_rectangle(
                    [0, 0, self.TILE_SIZE - 1, self.TILE_SIZE - 1], radius=14, fill=255)
                canvas_img.putalpha(mask)
                canvas_img.save(cache_file)
                return canvas_img
            except Exception:
                continue

        log_error(f"Web ikonu hiçbir kaynaktan alınamadı: {url}")
        return None

    def _extract_exe_icon(self, exe_path: str):
        cache_file = ICON_CACHE_DIR / (hashlib.md5(exe_path.encode("utf-8")).hexdigest() + ".png")
        if cache_file.exists():
            try:
                return Image.open(cache_file).convert("RGBA")
            except Exception:
                pass
        if not os.path.isfile(exe_path):
            return None
        try:
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if not large and not small:
                return None
            hicon = large[0] if large else small[0]

            ico_x = win32gui.GetSystemMetrics(win32con.SM_CXICON)
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
            hdc_mem = hdc.CreateCompatibleDC()
            hdc_mem.SelectObject(hbmp)
            hdc_mem.DrawIcon((0, 0), hicon)

            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGBA",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr, "raw", "BGRA", 0, 1
            )
            img = img.resize((self.TILE_SIZE, self.TILE_SIZE), Image.LANCZOS)
            img.save(cache_file)

            for h in large:
                win32gui.DestroyIcon(h)
            for h in small:
                win32gui.DestroyIcon(h)
            return img
        except Exception:
            log_error(f"İkon çıkarılamadı: {exe_path}")
            return None

    def _generate_letter_icon(self, name: str):
        """İkon bulunamazsa isme göre renkli, harfli bir rozet üretir."""
        size = self.TILE_SIZE
        letter = (name.strip()[:1] or "?").upper()
        # isimden deterministik bir renk üret
        h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
        hue_colors = ["#e63946", "#e07a1f", "#2a9d8f", "#457b9d", "#8338ec", "#d62828", "#0077b6"]
        color = hue_colors[h % len(hue_colors)]

        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=14, fill=color)
        try:
            font = ImageFont.truetype("arialbd.ttf", size // 2)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), letter, fill="white", font=font)
        return img


# ==============================================================================
# TUŞ / KISAYOL YÖNETİMİ (event tabanlı, polling YOK)
# ==============================================================================
ALNUM_KEYS = set("abcdefghijklmnopqrstuvwxyz0123456789")

# "-" tuşuna basılmadan hemen önce/sonra harf-rakam trafiği varsa bu "yazı
# yazma" olarak sayılır ve panel açılmaz. Sadece klavye boştayken basılan
# "-" paneli açar/kapatır.
TYPING_LOOKBACK = 0.6    # "-" basılmadan önceki bu kadar süre içinde yazı yazıldıysa yok say
TYPING_CONFIRM_DELAY = 0.22  # "-" basıldıktan sonra bu kadar bekleyip devamında harf gelip gelmediğine bakılır


class HotkeyManager:
    """
    keyboard kütüphanesinin event-tabanlı hook'unu kullanır (polling YOK).
    - Panel açma/kapama tuşu (sadece klavye boştayken tetiklenir)
    - K+R+S kapatma kombosu
    - Her uygulamaya özel, atanabilir kısayol tuşları
    Tüm geri çağrımlar (toggle/close/launch), Tk ana thread'ine
    `schedule_fn` (ör. root.after) üzerinden güvenle iletilir.
    """

    def __init__(self, config: ConfigManager, on_toggle, on_close, on_launch_app, schedule_fn=None):
        self.config = config
        self.on_toggle = on_toggle
        self.on_close = on_close
        self.on_launch_app = on_launch_app
        self.schedule_fn = schedule_fn or (lambda delay_ms, fn: fn())

        self._pressed = set()
        self._combo_times = {}
        self._last_alnum_time = 0.0
        self._enabled = KEYBOARD_AVAILABLE
        self._capture_mode = False  # yeni tuş yakalarken diğer olayları yut

    def start(self):
        if not self._enabled:
            log_error("keyboard modülü kurulu değil, kısayollar devre dışı")
            return
        keyboard.hook(self._on_event)

    def stop(self):
        if self._enabled:
            try:
                keyboard.unhook_all()
            except Exception:
                pass

    def _run_on_main(self, fn, *args):
        self.schedule_fn(0, lambda: fn(*args))

    def _on_event(self, event):
        if self._capture_mode:
            return  # ayarlar ekranında yeni tuş yakalanıyorsa normal akışı durdur

        name = event.name
        if event.event_type == "down":
            self._pressed.add(name)
            if name in ALNUM_KEYS:
                self._last_alnum_time = time.time()

            toggle_key = self.config.data["hotkeys"]["toggle"]
            if name == toggle_key:
                self._handle_toggle_press()

            combo = self.config.data["hotkeys"]["close_combo"]
            if name in combo:
                self._combo_times[name] = time.time()
                window = self.config.data["hotkeys"]["combo_window"]
                if all(k in self._combo_times for k in combo):
                    times = [self._combo_times[k] for k in combo]
                    if max(times) - min(times) <= window:
                        self._run_on_main(self.on_close)

            for app in self.config.data["apps"]:
                if app.get("hotkey") and app["hotkey"] == name:
                    self._run_on_main(self.on_launch_app, app)

        elif event.event_type == "up":
            self._pressed.discard(name)

    def _handle_toggle_press(self):
        """
        '-' tuşuna basıldı. Ama biri 'a-merhaba' ya da '-merhaba' gibi
        art arda (aynı anda değil) yazı yazıyor olabilir; bunu yakalamak için
        basılmadan hemen önceki trafiğe bakılır, ve basıldıktan kısa bir süre
        sonra hâlâ harf/rakam gelmiyorsa panel açılır/kapanır.
        """
        press_time = time.time()

        # '-' basılmadan hemen önce yazı yazılıyorduysa, muhtemelen kelime
        # içinde bir tire; hiç bekleme, direkt yok say.
        if press_time - self._last_alnum_time < TYPING_LOOKBACK:
            return

        def confirm():
            # Bekleme süresi boyunca herhangi bir harf/rakam basıldıysa
            # ('-' sonrası hızlıca 'merhaba' gibi) bu da yazıdır, iptal.
            if self._last_alnum_time > press_time:
                return
            self._run_on_main(self.on_toggle)

        threading.Timer(TYPING_CONFIRM_DELAY, confirm).start()

    def capture_next_key(self, callback):
        """Ayarlar ekranında 'tuşa basın' özelliği için arka planda çalışır."""
        if not self._enabled:
            callback(None)
            return

        def worker():
            self._capture_mode = True
            try:
                key = keyboard.read_key(suppress=False)
                # tuş bırakılana kadar bekle, çift tetiklemeyi önle
                try:
                    keyboard.wait(key, suppress=False)
                except Exception:
                    pass
            except Exception:
                key = None
            finally:
                self._capture_mode = False
            callback(key)

        threading.Thread(target=worker, daemon=True).start()


# ==============================================================================
# UYGULAMA BAŞLATMA
# ==============================================================================
def launch_shortcut(app: dict):
    try:
        if app["type"] == "url":
            webbrowser.open(app["target"])
        else:
            os.startfile(app["target"])
    except Exception:
        log_error(f"Kısayol başlatılamadı: {app}")


# ==============================================================================
# YUVARLAK KÖŞE YARDIMCI FONKSİYONU
# ==============================================================================
def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# ==============================================================================
# ORTAK ARAYÜZ YARDIMCILARI (buton stili, koyu tema) — Ayarlar & diyaloglarda kullanılır
# ==============================================================================
def make_button(parent, text, colors, command=None, kind="normal", width=None):
    """
    Tutarlı, düz (flat) ve hover efektli buton üretir.
    kind: 'normal' (nötr gri), 'primary' (accent dolgulu, ana eylem), 'danger' (kırmızı metin)
    """
    if kind == "primary":
        bg, fg, hover_bg = colors["accent"], "#ffffff", colors["accent_dim"]
    elif kind == "danger":
        bg, fg, hover_bg = colors["tile_bg"], "#ff5c5c", "#3a1414"
    else:
        bg, fg, hover_bg = colors["tile_bg"], colors["text"], colors["tile_hover"]

    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=hover_bg, activeforeground=fg,
                     relief="flat", bd=0, padx=14, pady=6, cursor="hand2",
                     font=("Segoe UI", 9, "bold"))
    if width:
        btn.configure(width=width)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def section_label(parent, text, colors, top_pad=14):
    """Ayarlar sekmelerinde tutarlı, vurgulu bölüm başlığı."""
    tk.Label(parent, text=text.upper(), bg=colors["bg"], fg=colors["accent"],
              font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(top_pad, 4))


def separator(parent, colors):
    tk.Frame(parent, bg=colors["tile_bg"], height=1).pack(fill="x", padx=14, pady=(4, 2))


def apply_dark_style(colors):
    """Notebook/scrollbar gibi ttk bileşenlerini koyu temayla eşler (bir kez çağrılması yeterli)."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TNotebook", background=colors["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=colors["tile_bg"], foreground=colors["sub_text"],
                     padding=(16, 9), font=("Segoe UI", 9, "bold"), borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", colors["bg"])],
              foreground=[("selected", colors["accent"])])
    style.configure("Vertical.TScrollbar", background=colors["tile_bg"], troughcolor=colors["bg"],
                     bordercolor=colors["bg"], arrowcolor=colors["sub_text"], borderwidth=0)
    style.configure("TSeparator", background=colors["tile_bg"])


# ==============================================================================
# UYGULAMA KAREOSU (ikon + isim, tıklanabilir, sağ tık ile kaldır/düzenle)
# ==============================================================================
class AppTile(tk.Frame):
    SIZE = 118

    def __init__(self, master, app, icon_photo, colors, on_click, on_edit, on_remove):
        super().__init__(master, bg=colors["tile_bg"], width=self.SIZE, height=self.SIZE,
                          highlightthickness=1, highlightbackground=colors["tile_bg"])
        self.pack_propagate(False)
        self.app = app
        self.colors = colors
        self._on_click = on_click
        self._on_edit = on_edit
        self._on_remove = on_remove

        self.icon_label = tk.Label(self, image=icon_photo, bg=colors["tile_bg"])
        self.icon_label.image = icon_photo
        self.icon_label.pack(pady=(14, 6))

        name_text = app["name"]
        if app.get("hotkey"):
            name_text += f"  [{app['hotkey'].upper()}]"
        self.name_label = tk.Label(self, text=name_text, font=("Segoe UI", 9, "bold"),
                                    fg=colors["text"], bg=colors["tile_bg"])
        self.name_label.pack()

        for widget in (self, self.icon_label, self.name_label):
            widget.bind("<Button-1>", self._click)
            widget.bind("<Enter>", self._hover_on)
            widget.bind("<Leave>", self._hover_off)
            widget.bind("<Button-3>", self._context_menu)

        self.menu = tk.Menu(self, tearoff=0, bg=colors["tile_bg"], fg=colors["text"])
        self.menu.add_command(label="Düzenle", command=lambda: self._on_edit(self.app))
        self.menu.add_command(label="Kaldır", command=lambda: self._on_remove(self.app))

    def _click(self, _event=None):
        self.configure(highlightbackground=self.colors["accent"])
        self.after(250, lambda: self.configure(highlightbackground=self.colors["tile_bg"]))
        self._on_click(self.app)

    def _hover_on(self, _event=None):
        self.configure(bg=self.colors["tile_hover"])
        self.icon_label.configure(bg=self.colors["tile_hover"])
        self.name_label.configure(bg=self.colors["tile_hover"])

    def _hover_off(self, _event=None):
        self.configure(bg=self.colors["tile_bg"])
        self.icon_label.configure(bg=self.colors["tile_bg"])
        self.name_label.configure(bg=self.colors["tile_bg"])

    def _context_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def update_content(self, app, icon_photo=None):
        """Widget'ı yeniden yaratmadan isim/tuş/ikon bilgisini günceller."""
        self.app = app
        name_text = app["name"]
        if app.get("hotkey"):
            name_text += f"  [{app['hotkey'].upper()}]"
        self.name_label.configure(text=name_text)
        if icon_photo is not None:
            self.icon_label.configure(image=icon_photo)
            self.icon_label.image = icon_photo


class AddTile(tk.Frame):
    """Izgaranın sonundaki '+' karesi, yeni kısayol eklemek için."""
    SIZE = 118

    def __init__(self, master, colors, on_add):
        super().__init__(master, bg=colors["tile_bg"], width=self.SIZE, height=self.SIZE,
                          highlightthickness=1, highlightbackground=colors["tile_bg"])
        self.pack_propagate(False)
        plus = tk.Label(self, text="+", font=("Segoe UI", 30, "bold"),
                         fg=colors["accent"], bg=colors["tile_bg"])
        plus.pack(expand=True)
        for w in (self, plus):
            w.bind("<Button-1>", lambda e: on_add())
            w.bind("<Enter>", lambda e: (self.configure(bg=colors["tile_hover"]), plus.configure(bg=colors["tile_hover"])))
            w.bind("<Leave>", lambda e: (self.configure(bg=colors["tile_bg"]), plus.configure(bg=colors["tile_bg"])))


# ==============================================================================
# ANA PANEL
# ==============================================================================
def register_scrollable(canvas):
    """Bu canvas'ı fare tekerleği ile kaydırılabilir olarak işaretler."""
    canvas._wheel_scroll_target = canvas


def global_mousewheel_handler(event):
    """
    Uygulama genelinde TEK SEFER bağlanan fare tekerleği yönlendiricisi.
    Panel'in ızgarası ve Ayarlar penceresinin kısayol listesi gibi birden
    fazla kaydırılabilir alan aynı anda var olabiliyor; eskiden her biri
    kendi bind_all()'unu çağırdığı için sonuncusu öncekini eziyordu ve
    Ayarlar bir kez açılınca panelin kaydırması kalıcı olarak bozuluyordu.
    Bunun yerine tek bir global işleyici, olayın geldiği widget'tan
    (event.widget = imlecin tam olarak üzerinde olduğu widget) başlayıp
    ebeveyn zincirinde register_scrollable() ile işaretlenmiş canvas'ı
    bulana kadar yukarı çıkar ve SADECE onu kaydırır.
    """
    w = event.widget
    while w is not None:
        target = getattr(w, "_wheel_scroll_target", None)
        if target is not None:
            try:
                target.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
            return
        w = getattr(w, "master", None)


class Panel:
    def __init__(self, root, config: ConfigManager, icons: IconManager):
        self.root = root
        self.config = config
        self.icons = icons
        self.visible = False
        self.hotkeys = None  # sonradan bağlanacak

        c = self.config.data["panel"]

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 1.0)
            self._alpha_supported = True
        except tk.TclError:
            self._alpha_supported = False

        self.apply_monitor(initial=True)

        # Windows'ta gerçek yuvarlak köşe hissi için transparan renk anahtarı
        self._transparent_key = "#123456"
        try:
            self.win.configure(bg=self._transparent_key)
            self.win.attributes("-transparentcolor", self._transparent_key)
        except tk.TclError:
            self.win.configure(bg=c["bg"])

        self.canvas = tk.Canvas(self.win, width=c["width"], height=c["height"],
                                 bg=self._transparent_key, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        rounded_rect(self.canvas, 2, 2, c["width"] - 2, c["height"] - 2,
                     c["corner_radius"], fill=c["bg"], outline=c["accent_dim"])

        self.content = tk.Frame(self.canvas, bg=c["bg"])
        self.canvas.create_window(c["width"] // 2, c["height"] // 2, window=self.content,
                                   width=c["width"] - 20, height=c["height"] - 20)

        self._build_header()
        self._build_grid_area()
        self._build_clock()

        self._animate_logo_bar()
        self._update_clock()

        # başlangıçta tamamen gizli — hiçbir monitörde görünmesin
        self.win.withdraw()

    # ---------------- MONİTÖR ----------------
    def apply_monitor(self, initial=False):
        """
        Ayarlarda seçilen monitöre göre panelin konum sınırlarını
        (mon_x/mon_y/mon_w/mon_h, açık/kapalı x konumları) hesaplar.
        """
        c = self.config.data["panel"]
        monitors = get_monitors(self.root)
        idx = c.get("monitor_index", 0)
        mon = monitors[idx] if 0 <= idx < len(monitors) else monitors[0]

        self.monitors = monitors
        self.mon_x, self.mon_y = mon["x"], mon["y"]
        self.mon_w, self.mon_h = mon["width"], mon["height"]

        self.panel_y = self.mon_y + c["y"]
        self.open_x = self.mon_x + self.mon_w - c["width"] - 40
        self.closed_x = self.mon_x + self.mon_w  # monitörün kendi sağ kenarı

        if initial:
            self.win.geometry(f"{c['width']}x{c['height']}+{self.closed_x}+{self.panel_y}")

    def reposition_to_monitor(self):
        """Ayarlardan monitör değiştirildiğinde çağrılır."""
        was_visible = self.visible
        self.visible = False
        try:
            self.win.attributes("-alpha", 1.0)
        except tk.TclError:
            pass
        self.win.withdraw()
        self.apply_monitor()
        c = self.config.data["panel"]
        self.win.geometry(f"{c['width']}x{c['height']}+{self.closed_x}+{self.panel_y}")
        if was_visible:
            self.visible = True
            self.slide_in()

    # ---------------- ÜST BAŞLIK ----------------
    def _build_header(self):
        c = self.config.data["panel"]
        top = tk.Frame(self.content, bg=c["bg"])
        top.pack(fill="x", pady=(6, 0))

        self.logo_label = tk.Label(top, text=APP_NAME, font=("Segoe UI", 22, "bold"),
                                    fg=c["accent"], bg=c["bg"])
        self.logo_label.pack(side="left", padx=(6, 0))

        gear = tk.Label(top, text="⚙", font=("Segoe UI", 16), fg=c["sub_text"], bg=c["bg"], cursor="hand2")
        gear.pack(side="right", padx=(0, 6))
        gear.bind("<Button-1>", lambda e: self.open_settings())
        gear.bind("<Enter>", lambda e: gear.configure(fg=c["accent"]))
        gear.bind("<Leave>", lambda e: gear.configure(fg=c["sub_text"]))

        # logonun altında kayan bir "shimmer" çizgisi — yanıp sönme yerine
        # sürekli sağa-sola süzülen ince bir ışık şeridi
        self.logo_bar = tk.Canvas(self.content, height=3, bg=c["bg"], highlightthickness=0)
        self.logo_bar.pack(fill="x", padx=6, pady=(2, 6))
        self._bar_pos = 0
        self._bar_dir = 1

    def _animate_logo_bar(self):
        c = self.config.data["panel"]
        self.logo_bar.delete("all")
        w = self.logo_bar.winfo_width()
        if w <= 1:
            w = c["width"] - 32
        seg = max(30, w // 5)

        # sönük taban çizgisi
        self.logo_bar.create_line(0, 1, w, 1, fill=c["tile_bg"], width=2)
        # parlak, kayan segment
        x1 = self._bar_pos
        x2 = min(w, x1 + seg)
        self.logo_bar.create_line(max(0, x1), 1, x2, 1, fill=c["accent"], width=2)

        self._bar_pos += 6 * self._bar_dir
        if self._bar_pos + seg >= w:
            self._bar_dir = -1
        elif self._bar_pos <= 0:
            self._bar_dir = 1

        self.win.after(35, self._animate_logo_bar)

    # ---------------- IZGARA (kaydırılabilir) ----------------
    def _build_grid_area(self):
        c = self.config.data["panel"]
        wrap = tk.Frame(self.content, bg=c["bg"])
        wrap.pack(fill="both", expand=True, pady=4)

        self.grid_canvas = tk.Canvas(wrap, bg=c["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrap, orient="vertical", command=self.grid_canvas.yview)
        self.grid_canvas.configure(yscrollcommand=scrollbar.set)

        self.grid_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.grid_frame = tk.Frame(self.grid_canvas, bg=c["bg"])
        self.grid_window = self.grid_canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")

        self.grid_frame.bind("<Configure>", lambda e: self.grid_canvas.configure(
            scrollregion=self.grid_canvas.bbox("all")))
        self.grid_canvas.bind("<Configure>", lambda e: self.grid_canvas.itemconfig(
            self.grid_window, width=e.width))
        register_scrollable(self.grid_canvas)

        # Animasyonlu ızgara durumu
        self.tiles = {}      # app_id (veya '__add__') -> widget
        self.tile_geo = {}   # app_id -> (x, y) mevcut hedef konum
        self.TILE_W = 118
        self.TILE_H = 118
        self.GAP = 10
        self.ANIM_STEPS = 9
        self.ANIM_INTERVAL = 12  # ms

        self.refresh_grid(animate=False)

    def _on_mousewheel(self, event):
        self.grid_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ---------------- Izgara düzeni hesaplama ----------------
    def _compute_layout(self):
        c = self.config.data["panel"]
        cols = max(1, c["columns"])
        apps = self.config.data["apps"]
        layout = {}
        for i, app in enumerate(apps):
            row, col = divmod(i, cols)
            layout[app["id"]] = (col * (self.TILE_W + self.GAP), row * (self.TILE_H + self.GAP))
        row, col = divmod(len(apps), cols)
        layout["__add__"] = (col * (self.TILE_W + self.GAP), row * (self.TILE_H + self.GAP))
        return layout, cols, len(apps)

    def refresh_grid(self, animate=True):
        """
        Kısayol listesini panelin geometrisini bozmadan, hizalı ve
        animasyonlu şekilde günceller: yeni kareler büyüyerek belirir,
        kaldırılanlar küçülerek kaybolur, kalanlar gerekiyorsa yeni
        konumlarına doğru kayar.
        """
        c = self.config.data["panel"]
        apps = self.config.data["apps"]
        new_layout, cols, app_count = self._compute_layout()
        new_ids = {a["id"] for a in apps} | {"__add__"}

        # 1) Artık listede olmayanlar: küçülerek kaybol
        for tid in list(self.tiles.keys()):
            if tid not in new_ids:
                self._animate_remove(tid, animate)

        # 2) Kısayollar: var olanı güncelle/kaydır, yoksa büyüyerek ekle
        for app in apps:
            tid = app["id"]
            target = new_layout[tid]
            if tid in self.tiles:
                tile = self.tiles[tid]
                photo = self.icons.get(app)
                tile.update_content(app, photo)
                old = self.tile_geo.get(tid, target)
                self.tile_geo[tid] = target
                if old != target:
                    self._animate_move(tile, old, target, animate)
                else:
                    tile.place(x=target[0], y=target[1], width=self.TILE_W, height=self.TILE_H)
            else:
                photo = self.icons.get(app)
                tile = AppTile(self.grid_frame, app, photo, c,
                                on_click=launch_shortcut,
                                on_edit=self.edit_app,
                                on_remove=self.remove_app)
                self.tiles[tid] = tile
                self.tile_geo[tid] = target
                self._animate_new(tile, target, animate)

        # 3) '+' karesi her zaman en sonda
        add_target = new_layout["__add__"]
        if "__add__" in self.tiles:
            tile = self.tiles["__add__"]
            old = self.tile_geo.get("__add__", add_target)
            self.tile_geo["__add__"] = add_target
            if old != add_target:
                self._animate_move(tile, old, add_target, animate)
            else:
                tile.place(x=add_target[0], y=add_target[1], width=self.TILE_W, height=self.TILE_H)
        else:
            tile = AddTile(self.grid_frame, c, on_add=self.open_settings)
            self.tiles["__add__"] = tile
            self.tile_geo["__add__"] = add_target
            self._animate_new(tile, add_target, animate)

        # 4) Kaydırma alanının boyutunu, düzeni bozmadan güncelle
        total_rows = (app_count // cols) + 1
        frame_h = total_rows * (self.TILE_H + self.GAP) + self.GAP
        frame_w = cols * (self.TILE_W + self.GAP) + self.GAP
        self.grid_frame.configure(width=frame_w, height=frame_h)
        self.grid_frame.after(10, lambda: self.grid_canvas.configure(
            scrollregion=(0, 0, frame_w, frame_h)))

    @staticmethod
    def _ease_out(t):
        return 1 - (1 - t) ** 3

    def _animate_move(self, widget, old_pos, new_pos, animate=True):
        if not animate:
            widget.place(x=new_pos[0], y=new_pos[1], width=self.TILE_W, height=self.TILE_H)
            return
        ox, oy = old_pos
        nx, ny = new_pos
        steps = self.ANIM_STEPS

        def step(i):
            if not widget.winfo_exists():
                return
            t = self._ease_out(i / steps)
            x = ox + (nx - ox) * t
            y = oy + (ny - oy) * t
            try:
                widget.place(x=x, y=y, width=self.TILE_W, height=self.TILE_H)
            except tk.TclError:
                return
            if i < steps:
                widget.after(self.ANIM_INTERVAL, lambda: step(i + 1))

        step(0)

    def _animate_new(self, widget, pos, animate=True):
        x, y = pos
        if not animate:
            widget.place(x=x, y=y, width=self.TILE_W, height=self.TILE_H)
            return
        steps = self.ANIM_STEPS

        def step(i):
            if not widget.winfo_exists():
                return
            t = self._ease_out(i / steps)
            w = max(1, self.TILE_W * t)
            h = max(1, self.TILE_H * t)
            cx = x + (self.TILE_W - w) / 2
            cy = y + (self.TILE_H - h) / 2
            try:
                widget.place(x=cx, y=cy, width=w, height=h)
            except tk.TclError:
                return
            if i < steps:
                widget.after(self.ANIM_INTERVAL, lambda: step(i + 1))
            else:
                widget.place(x=x, y=y, width=self.TILE_W, height=self.TILE_H)

        widget.place(x=x + self.TILE_W / 2, y=y + self.TILE_H / 2, width=1, height=1)
        step(0)

    def _animate_remove(self, tid, animate=True):
        widget = self.tiles.pop(tid, None)
        self.tile_geo.pop(tid, None)
        if widget is None:
            return
        if not animate:
            widget.destroy()
            return
        try:
            info = widget.place_info()
            x, y = float(info.get("x", 0)), float(info.get("y", 0))
        except Exception:
            widget.destroy()
            return
        steps = self.ANIM_STEPS

        def step(i):
            if not widget.winfo_exists():
                return
            t = self._ease_out(i / steps)
            w = max(1, self.TILE_W * (1 - t))
            h = max(1, self.TILE_H * (1 - t))
            cx = x + (self.TILE_W - w) / 2
            cy = y + (self.TILE_H - h) / 2
            try:
                widget.place(x=cx, y=cy, width=w, height=h)
            except tk.TclError:
                widget.destroy()
                return
            if i < steps:
                widget.after(self.ANIM_INTERVAL, lambda: step(i + 1))
            else:
                widget.destroy()

        step(0)

    # ---------------- SAAT / TARİH ----------------
    def _build_clock(self):
        c = self.config.data["panel"]
        self.clock_label = tk.Label(self.content, font=("Segoe UI", self.config.data["clock"]["font_size"]),
                                     fg=c["text"], bg=c["bg"])
        self.date_label = tk.Label(self.content, font=("Segoe UI", self.config.data["clock"]["font_size"]),
                                    fg=c["sub_text"], bg=c["bg"])
        self._place_clock()

    def _place_clock(self):
        corner = self.config.data["clock"]["corner"]
        anchor_map = {
            "bottom-right": dict(relx=0.97, rely=0.98, anchor="se"),
            "bottom-left":  dict(relx=0.03, rely=0.98, anchor="sw"),
            # üst köşeler başlıktaki logo/ayarlar ikonuyla çakışmasın diye
            # başlık şeridinin hemen altına yerleştirilir
            "top-right":    dict(relx=0.97, rely=0.15, anchor="ne"),
            "top-left":     dict(relx=0.03, rely=0.15, anchor="nw"),
        }
        pos = anchor_map.get(corner, anchor_map["bottom-right"])
        self.clock_label.place(**pos)

        if self.config.data["clock"]["show_date"]:
            date_pos = dict(pos)
            # tarihi saatin hemen üstüne/yanına koy
            date_pos["rely"] = max(0.02, pos["rely"] - 0.055) if "bottom" in corner else min(0.98, pos["rely"] + 0.055)
            self.date_label.place(**date_pos)
        else:
            self.date_label.place_forget()

    def _update_clock(self):
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%d/%m/%Y"))
        self.win.after(1000, self._update_clock)

    # ---------------- KAYAR PANEL ----------------
    def slide_in(self):
        c = self.config.data["panel"]
        # başka bir monitörde belirmesin diye önce görünür yap, sonra kaydır
        self.win.deiconify()
        x = self.win.winfo_x()
        target_x = self.open_x
        total = max(1, self.closed_x - target_x)
        if x > target_x:
            x_new = max(target_x, x - 28)
            # kayarken aynı zamanda belirginleşsin: sağdan gelirken saydamdan
            # tam görünür hale geçer, komşu monitörde flaş vermez
            progress = 1.0 - (x_new - target_x) / total
            self._set_alpha(0.15 + 0.85 * progress)
            self.win.geometry(f"{c['width']}x{c['height']}+{x_new}+{self.panel_y}")
            self.win.after(10, self.slide_in)
        else:
            self._set_alpha(1.0)

    def slide_out(self):
        c = self.config.data["panel"]
        x = self.win.winfo_x()
        edge_x = self.closed_x  # seçili monitörün kendi sağ kenarı
        target_x = self.open_x
        total = max(1, edge_x - target_x)
        if x < edge_x:
            x_new = min(edge_x, x + 28)
            # komşu monitöre girmeden önce tamamen saydamlaşır, bu yüzden
            # kısa süreliğine bile olsa orada "flaş" şeklinde görünmez
            progress = (x_new - target_x) / total
            self._set_alpha(max(0.0, 1.0 - progress))
            self.win.geometry(f"{c['width']}x{c['height']}+{x_new}+{self.panel_y}")
            self.win.after(10, self.slide_out)
        else:
            # tamamen kenardan kaydı: pencereyi tamamen gizle ki genişletilmiş
            # masaüstünde ikinci monitörde görünmesin
            self.win.withdraw()
            self._set_alpha(1.0)  # sonraki açılış için sıfırla

    def _set_alpha(self, value):
        if not self._alpha_supported:
            return
        try:
            self.win.attributes("-alpha", value)
        except tk.TclError:
            pass

    def toggle(self):
        if not self.visible:
            self.slide_in()
        else:
            self.slide_out()
        self.visible = not self.visible

    # ---------------- KISAYOL EKLE / DÜZENLE / KALDIR ----------------
    def open_settings(self):
        SettingsWindow(self.win, self.config, self.hotkeys, self, on_change=self._on_config_changed)

    def edit_app(self, app):
        AppEditDialog(self.win, self.config, self.hotkeys, self.icons, app=app, on_saved=self._on_config_changed)

    def remove_app(self, app):
        if messagebox.askyesno(APP_NAME, f"'{app['name']}' kısayolunu kaldırmak istiyor musun?", parent=self.win):
            self.config.remove_app(app["id"])
            self._on_config_changed()

    def _on_config_changed(self):
        self.refresh_grid()
        self._place_clock()


# ==============================================================================
# UYGULAMA EKLE / DÜZENLE PENCERESİ
# ==============================================================================
class AppEditDialog(tk.Toplevel):
    def __init__(self, master, config: ConfigManager, hotkeys: HotkeyManager, icons: IconManager = None,
                 app=None, on_saved=None):
        super().__init__(master)
        self.config = config
        self.hotkeys = hotkeys
        self.icons = icons
        self.app = app
        self.on_saved = on_saved
        self.is_edit = app is not None

        c = config.data["panel"]
        apply_dark_style(c)
        self.title("Kısayolu Düzenle" if self.is_edit else "Yeni Kısayol Ekle")
        self.configure(bg=c["bg"])
        self.geometry("380x460")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.transient(master)

        # ---- başlık şeridi ----
        header = tk.Frame(self, bg=c["bg"])
        header.pack(fill="x")
        tk.Label(header, text=("✎ Kısayolu Düzenle" if self.is_edit else "+ Yeni Kısayol"),
                 bg=c["bg"], fg=c["accent"], font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(16, 2))
        separator(self, c)

        body = tk.Frame(self, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=16)

        tk.Label(body, text="İsim", bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 3))
        self.name_var = tk.StringVar(value=app["name"] if app else "")
        self._styled_entry(body, self.name_var).pack(fill="x", ipady=5)

        tk.Label(body, text="Tür", bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 9)).pack(anchor="w", pady=(14, 3))
        self.type_var = tk.StringVar(value=app["type"] if app else "exe")
        type_frame = tk.Frame(body, bg=c["bg"])
        type_frame.pack(anchor="w")
        tk.Radiobutton(type_frame, text="Uygulama (.exe)", variable=self.type_var, value="exe",
                        bg=c["bg"], fg=c["text"], selectcolor=c["tile_bg"], activebackground=c["bg"],
                        font=("Segoe UI", 9), command=self._toggle_type).pack(side="left")
        tk.Radiobutton(type_frame, text="Web Sitesi", variable=self.type_var, value="url",
                        bg=c["bg"], fg=c["text"], selectcolor=c["tile_bg"], activebackground=c["bg"],
                        font=("Segoe UI", 9), command=self._toggle_type).pack(side="left", padx=(14, 0))

        tk.Label(body, text="Hedef (dosya yolu ya da web adresi)", bg=c["bg"], fg=c["sub_text"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(14, 3))
        target_row = tk.Frame(body, bg=c["bg"])
        target_row.pack(fill="x")
        self.target_var = tk.StringVar(value=app["target"] if app else "")
        self.target_entry = self._styled_entry(target_row, self.target_var)
        self.target_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.browse_btn = make_button(target_row, "Gözat", c, command=self._browse)
        self.browse_btn.pack(side="left", padx=(8, 0))
        self._toggle_type()

        tk.Label(body, text="Kısayol Tuşu (opsiyonel)", bg=c["bg"], fg=c["sub_text"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(14, 3))
        hk_row = tk.Frame(body, bg=c["bg"])
        hk_row.pack(fill="x")
        self.hotkey_var = tk.StringVar(value=(app.get("hotkey") or "Yok") if app else "Yok")
        tk.Label(hk_row, textvariable=self.hotkey_var, width=10, bg=c["tile_bg"], fg=c["accent"],
                 font=("Segoe UI", 9, "bold"), pady=6).pack(side="left")
        make_button(hk_row, "Tuş Ata", c, command=self._capture_hotkey).pack(side="left", padx=6)
        make_button(hk_row, "Temizle", c, command=lambda: self.hotkey_var.set("Yok")).pack(side="left")

        btn_row = tk.Frame(self, bg=c["bg"])
        btn_row.pack(fill="x", padx=16, pady=16, side="bottom")
        make_button(btn_row, "Kaydet", c, kind="primary", command=self._save).pack(side="right")
        make_button(btn_row, "İptal", c, command=self.destroy).pack(side="right", padx=8)

    @staticmethod
    def _styled_entry(parent, var):
        c_bg = "#1a1a1a"
        return tk.Entry(parent, textvariable=var, bg=c_bg, fg="#f2f2f2", insertbackground="#f2f2f2",
                         relief="flat", highlightthickness=1, highlightbackground="#2a2a2a",
                         highlightcolor="#ff2323", font=("Segoe UI", 10))

    def _toggle_type(self):
        if self.type_var.get() == "exe":
            self.browse_btn.configure(state="normal")
        else:
            self.browse_btn.configure(state="disabled")

    def _browse(self):
        path = filedialog.askopenfilename(title="Uygulama Seç", filetypes=[("Uygulamalar", "*.exe"), ("Tüm dosyalar", "*.*")])
        if path:
            self.target_var.set(path)
            if not self.name_var.get():
                self.name_var.set(Path(path).stem)

    def _capture_hotkey(self):
        if not self.hotkeys or not KEYBOARD_AVAILABLE:
            messagebox.showinfo(APP_NAME, "Kısayol tuşu ataması için 'keyboard' modülü gerekli.", parent=self)
            return
        self.hotkey_var.set("Tuşa basın...")

        def done(key):
            self.after(0, lambda: self.hotkey_var.set(key if key else "Yok"))

        self.hotkeys.capture_next_key(done)

    def _save(self):
        name = self.name_var.get().strip()
        target = self.target_var.get().strip()
        if not name or not target:
            messagebox.showwarning(APP_NAME, "İsim ve hedef alanı boş bırakılamaz.", parent=self)
            return

        hotkey_val = self.hotkey_var.get()
        hotkey = None if hotkey_val in ("Yok", "Tuşa basın...") else hotkey_val

        if self.is_edit:
            self.config.update_app(self.app["id"], name=name, type=self.type_var.get(),
                                    target=target, hotkey=hotkey)
        else:
            self.config.add_app({"name": name, "type": self.type_var.get(),
                                  "target": target, "hotkey": hotkey})

        if self.on_saved:
            self.on_saved()
        self.destroy()


# ==============================================================================
# TEK BİR KISAYOL SATIRI (Ayarlar > Kısayollar sekmesinde kullanılır)
# ==============================================================================
class AppRow(tk.Frame):
    def __init__(self, master, app, icon_photo, colors, on_edit, on_remove):
        super().__init__(master, bg=colors["tile_bg"])
        self.app = app

        icon_lbl = tk.Label(self, image=icon_photo, bg=colors["tile_bg"])
        icon_lbl.image = icon_photo
        icon_lbl.pack(side="left", padx=(10, 10), pady=8)

        text_frame = tk.Frame(self, bg=colors["tile_bg"])
        text_frame.pack(side="left", fill="both", expand=True, pady=8)
        tk.Label(text_frame, text=app["name"], bg=colors["tile_bg"], fg=colors["text"],
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
        sub = "Uygulama" if app["type"] == "exe" else "Web Sitesi"
        if app.get("hotkey"):
            sub += f"   ⌨ {app['hotkey'].upper()}"
        tk.Label(text_frame, text=sub, bg=colors["tile_bg"], fg=colors["sub_text"],
                 font=("Segoe UI", 8), anchor="w").pack(fill="x")

        btns = tk.Frame(self, bg=colors["tile_bg"])
        btns.pack(side="right", padx=8)
        edit_btn = tk.Label(btns, text="✎", bg=colors["tile_bg"], fg=colors["sub_text"],
                             font=("Segoe UI", 11), cursor="hand2", padx=6)
        edit_btn.pack(side="left")
        edit_btn.bind("<Button-1>", lambda e: on_edit(app))
        edit_btn.bind("<Enter>", lambda e: edit_btn.configure(fg=colors["accent"]))
        edit_btn.bind("<Leave>", lambda e: edit_btn.configure(fg=colors["sub_text"]))

        del_btn = tk.Label(btns, text="✕", bg=colors["tile_bg"], fg=colors["sub_text"],
                            font=("Segoe UI", 11), cursor="hand2", padx=6)
        del_btn.pack(side="left")
        del_btn.bind("<Button-1>", lambda e: on_remove(app))
        del_btn.bind("<Enter>", lambda e: del_btn.configure(fg="#ff5c5c"))
        del_btn.bind("<Leave>", lambda e: del_btn.configure(fg=colors["sub_text"]))

        for w in (self, icon_lbl, text_frame):
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)
        self._colors = colors
        self._icon_lbl = icon_lbl
        self._text_frame = text_frame

    def _hover_on(self, _e=None):
        self.configure(bg=self._colors["tile_hover"])
        self._icon_lbl.configure(bg=self._colors["tile_hover"])
        self._text_frame.configure(bg=self._colors["tile_hover"])
        for child in self._text_frame.winfo_children():
            child.configure(bg=self._colors["tile_hover"])

    def _hover_off(self, _e=None):
        self.configure(bg=self._colors["tile_bg"])
        self._icon_lbl.configure(bg=self._colors["tile_bg"])
        self._text_frame.configure(bg=self._colors["tile_bg"])
        for child in self._text_frame.winfo_children():
            child.configure(bg=self._colors["tile_bg"])


# ==============================================================================
# AYARLAR PENCERESİ
# ==============================================================================
class SettingsWindow(tk.Toplevel):
    def __init__(self, master, config: ConfigManager, hotkeys: HotkeyManager, panel=None, on_change=None):
        super().__init__(master)
        self.config = config
        self.hotkeys = hotkeys
        self.panel = panel
        self.icons = panel.icons if panel else None
        self.on_change = on_change

        c = config.data["panel"]
        apply_dark_style(c)
        self.title(f"{FULL_TITLE} - Ayarlar")
        self.configure(bg=c["bg"])
        self.geometry("420x580")
        self.minsize(380, 480)
        self.attributes("-topmost", True)
        self.transient(master)

        header = tk.Frame(self, bg=c["bg"])
        header.pack(fill="x")
        header_row = tk.Frame(header, bg=c["bg"])
        header_row.pack(fill="x", padx=16, pady=(14, 0))
        self._logo_photo = _load_logo_photo(size=40)
        if self._logo_photo:
            tk.Label(header_row, image=self._logo_photo, bg=c["bg"]).pack(side="left", padx=(0, 10))
        title_col = tk.Frame(header_row, bg=c["bg"])
        title_col.pack(side="left")
        tk.Label(title_col, text="⚙ Ayarlar", bg=c["bg"], fg=c["accent"],
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(title_col, text=f"{PRODUCT_NAME} {APP_VERSION} — {APP_NAME} kişisel kısayol paneli", bg=c["bg"], fg=c["sub_text"],
                 font=("Segoe UI", 9)).pack(anchor="w")
        tk.Frame(header, bg=c["bg"], height=10).pack(fill="x")
        separator(self, c)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.apps_tab = tk.Frame(nb, bg=c["bg"])
        self.hotkeys_tab = tk.Frame(nb, bg=c["bg"])
        self.clock_tab = tk.Frame(nb, bg=c["bg"])
        self.screen_tab = tk.Frame(nb, bg=c["bg"])
        nb.add(self.apps_tab, text="Kısayollar")
        nb.add(self.hotkeys_tab, text="Tuşlar")
        nb.add(self.clock_tab, text="Saat")
        nb.add(self.screen_tab, text="Ekran")

        self._build_apps_tab()
        self._build_hotkeys_tab()
        self._build_clock_tab()
        self._build_screen_tab()

    # ---------------- Kısayollar sekmesi ----------------
    def _build_apps_tab(self):
        c = self.config.data["panel"]
        section_label(self.apps_tab, "Kayıtlı Kısayollar", c, top_pad=10)

        list_wrap = tk.Frame(self.apps_tab, bg=c["bg"])
        list_wrap.pack(fill="both", expand=True, padx=10)

        self.rows_canvas = tk.Canvas(list_wrap, bg=c["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(list_wrap, orient="vertical", command=self.rows_canvas.yview)
        self.rows_canvas.configure(yscrollcommand=sb.set)
        self.rows_canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.rows_frame = tk.Frame(self.rows_canvas, bg=c["bg"])
        self.rows_window = self.rows_canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.rows_frame.bind("<Configure>", lambda e: self.rows_canvas.configure(
            scrollregion=self.rows_canvas.bbox("all")))
        self.rows_canvas.bind("<Configure>", lambda e: self.rows_canvas.itemconfig(
            self.rows_window, width=e.width))
        register_scrollable(self.rows_canvas)

        self._reload_app_rows()

        btn_row = tk.Frame(self.apps_tab, bg=c["bg"])
        btn_row.pack(fill="x", padx=10, pady=10)
        make_button(btn_row, "+ Yeni Kısayol Ekle", c, kind="primary", command=self._add_app).pack(fill="x")

    def _reload_app_rows(self):
        c = self.config.data["panel"]
        for w in self.rows_frame.winfo_children():
            w.destroy()
        for app in self.config.data["apps"]:
            photo = self.icons.get(app) if self.icons else None
            row = AppRow(self.rows_frame, app, photo, c, on_edit=self._edit_app, on_remove=self._remove_app)
            row.pack(fill="x", pady=3)

    def _add_app(self):
        AppEditDialog(self, self.config, self.hotkeys, self.icons, app=None, on_saved=self._refresh_all)

    def _edit_app(self, app):
        AppEditDialog(self, self.config, self.hotkeys, self.icons, app=app, on_saved=self._refresh_all)

    def _remove_app(self, app):
        if messagebox.askyesno(APP_NAME, f"'{app['name']}' kaldırılsın mı?", parent=self):
            self.config.remove_app(app["id"])
            self._refresh_all()

    def _refresh_all(self):
        self._reload_app_rows()
        if self.on_change:
            self.on_change()

    # ---------------- Tuşlar sekmesi ----------------
    def _build_hotkeys_tab(self):
        c = self.config.data["panel"]
        t = self.hotkeys_tab

        section_label(t, "Panel Açma/Kapama Tuşu", c, top_pad=10)
        row = tk.Frame(t, bg=c["bg"]); row.pack(fill="x", padx=14)
        self.toggle_var = tk.StringVar(value=self.config.data["hotkeys"]["toggle"].upper())
        tk.Label(row, textvariable=self.toggle_var, width=10, bg=c["tile_bg"], fg=c["accent"],
                 font=("Segoe UI", 9, "bold"), pady=6).pack(side="left")
        make_button(row, "Değiştir", c, command=self._capture_toggle).pack(side="left", padx=6)
        tk.Label(t, text="Sadece klavye boştayken (yazı yazmıyorken) basıldığında paneli açar/kapatır.",
                 bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 8), wraplength=360, justify="left"
                 ).pack(anchor="w", padx=14, pady=(4, 0))

        section_label(t, "Kapatma Kombinasyonu (aynı anda basılır)", c)
        self.combo_frame = tk.Frame(t, bg=c["bg"])
        self.combo_frame.pack(fill="x", padx=14)
        self._render_combo()

        combo_btns = tk.Frame(t, bg=c["bg"]); combo_btns.pack(fill="x", padx=14, pady=8)
        make_button(combo_btns, "+ Tuş Ekle", c, command=self._add_combo_key).pack(side="left")

        note = ("Not: 'keyboard' modülü kurulu değilse kısayollar çalışmaz."
                if not KEYBOARD_AVAILABLE else
                "K, R ve S tuşlarına 1 saniye içinde basmak uygulamayı tamamen kapatır.")
        tk.Label(t, text=note, bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 8),
                 wraplength=360, justify="left").pack(anchor="w", padx=14, pady=16)

    def _render_combo(self):
        for w in self.combo_frame.winfo_children():
            w.destroy()
        c = self.config.data["panel"]
        combo = self.config.data["hotkeys"]["close_combo"]
        for i, key in enumerate(combo):
            row = tk.Frame(self.combo_frame, bg=c["bg"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=key.upper(), width=10, bg=c["tile_bg"], fg=c["text"],
                     font=("Segoe UI", 9, "bold"), pady=5).pack(side="left")
            make_button(row, "Değiştir", c, command=lambda idx=i: self._capture_combo_key(idx)).pack(side="left", padx=4)
            make_button(row, "Kaldır", c, kind="danger", command=lambda idx=i: self._remove_combo_key(idx)).pack(side="left")

    def _capture_toggle(self):
        if not self.hotkeys or not KEYBOARD_AVAILABLE:
            messagebox.showinfo(APP_NAME, "'keyboard' modülü kurulu değil.", parent=self)
            return
        self.toggle_var.set("Tuşa basın...")

        def done(key):
            if key:
                self.config.data["hotkeys"]["toggle"] = key
                self.config.save()
            self.after(0, lambda: self.toggle_var.set(self.config.data["hotkeys"]["toggle"].upper()))

        self.hotkeys.capture_next_key(done)

    def _capture_combo_key(self, idx):
        if not self.hotkeys or not KEYBOARD_AVAILABLE:
            return

        def done(key):
            if key:
                self.config.data["hotkeys"]["close_combo"][idx] = key
                self.config.save()
            self.after(0, self._render_combo)

        self.hotkeys.capture_next_key(done)

    def _remove_combo_key(self, idx):
        combo = self.config.data["hotkeys"]["close_combo"]
        if len(combo) <= 1:
            messagebox.showinfo(APP_NAME, "En az 1 tuş kalmalı.", parent=self)
            return
        combo.pop(idx)
        self.config.save()
        self._render_combo()

    def _add_combo_key(self):
        if not self.hotkeys or not KEYBOARD_AVAILABLE:
            return

        def done(key):
            if key and key not in self.config.data["hotkeys"]["close_combo"]:
                self.config.data["hotkeys"]["close_combo"].append(key)
                self.config.save()
            self.after(0, self._render_combo)

        self.hotkeys.capture_next_key(done)

    # ---------------- Saat sekmesi ----------------
    def _build_clock_tab(self):
        c = self.config.data["panel"]
        t = self.clock_tab

        section_label(t, "Saatin Konumu", c, top_pad=10)
        corner_frame = tk.Frame(t, bg=c["bg"])
        corner_frame.pack(anchor="w", padx=14)
        self.corner_var = tk.StringVar(value=self.config.data["clock"]["corner"])
        for key, label in CORNER_LABELS.items():
            tk.Radiobutton(corner_frame, text=label, variable=self.corner_var, value=key,
                            bg=c["bg"], fg=c["text"], selectcolor=c["tile_bg"], activebackground=c["bg"],
                            font=("Segoe UI", 9), command=self._apply_clock).pack(anchor="w", pady=2)

        section_label(t, "Görünüm", c)
        self.show_date_var = tk.BooleanVar(value=self.config.data["clock"]["show_date"])
        tk.Checkbutton(t, text="Tarihi de göster", variable=self.show_date_var, bg=c["bg"], fg=c["text"],
                        selectcolor=c["tile_bg"], activebackground=c["bg"], font=("Segoe UI", 9),
                        command=self._apply_clock).pack(anchor="w", padx=14, pady=(2, 0))

    def _apply_clock(self):
        self.config.data["clock"]["corner"] = self.corner_var.get()
        self.config.data["clock"]["show_date"] = self.show_date_var.get()
        self.config.save()
        if self.on_change:
            self.on_change()

    # ---------------- Ekran sekmesi ----------------
    def _build_screen_tab(self):
        c = self.config.data["panel"]
        t = self.screen_tab

        section_label(t, "Panelin Çıkacağı Ekran", c, top_pad=10)
        tk.Label(t, text="Birden fazla monitörün varsa, panelin hangisinde belireceğini seç.",
                 bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 8), wraplength=360, justify="left"
                 ).pack(anchor="w", padx=14, pady=(0, 8))

        monitors = self.panel.monitors if self.panel else get_monitors(self)
        current_idx = self.config.data["panel"].get("monitor_index", 0)
        self.monitor_var = tk.IntVar(value=current_idx if current_idx < len(monitors) else 0)

        list_frame = tk.Frame(t, bg=c["bg"])
        list_frame.pack(fill="x", padx=14)
        for mon in monitors:
            row = tk.Frame(list_frame, bg=c["tile_bg"])
            row.pack(fill="x", pady=3)
            label = f"Ekran {mon['index'] + 1} — {mon['width']}x{mon['height']}"
            if mon["index"] == 0:
                label += "  (Ana Ekran)"
            rb = tk.Radiobutton(row, text=label, variable=self.monitor_var, value=mon["index"],
                                 bg=c["tile_bg"], fg=c["text"], selectcolor=c["bg"],
                                 activebackground=c["tile_bg"], font=("Segoe UI", 9),
                                 command=self._apply_monitor, anchor="w", padx=10, pady=8)
            rb.pack(fill="x")

        if not SCREENINFO_AVAILABLE:
            tk.Label(t, text="Not: birden fazla ekranı doğru algılamak için 'screeninfo' paketini "
                              "kurman gerekiyor (pip install screeninfo). Şu an sadece ana ekran görünüyor.",
                     bg=c["bg"], fg=c["sub_text"], font=("Segoe UI", 8), wraplength=360, justify="left"
                     ).pack(anchor="w", padx=14, pady=14)

    def _apply_monitor(self):
        self.config.data["panel"]["monitor_index"] = self.monitor_var.get()
        self.config.save()
        if self.panel:
            self.panel.reposition_to_monitor()

# ==============================================================================
# ANA GİRİŞ NOKTASI
# ==============================================================================
def main():
    sys.excepthook = lambda *args: log_error("Yakalanmamış hata")

    root = tk.Tk()
    root.withdraw()
    # fare tekerleği için TEK global yönlendirici — birden fazla kaydırılabilir
    # pencere (panel ızgarası + ayarlar listesi) arasında çakışmayı engeller
    root.bind_all("<MouseWheel>", global_mousewheel_handler)

    # Uygulama ikonu: bundan sonra açılan TÜM Toplevel pencereler (Ayarlar,
    # Kısayol Ekle/Düzenle) bunu otomatik miras alır. .pyw doğrudan
    # çalıştırılırken de, PyInstaller ile .exe'ye paketlenmişken de çalışır.
    try:
        if os.path.exists(APP_ICON_PATH):
            root.iconbitmap(default=APP_ICON_PATH)
    except Exception:
        log_error("Uygulama ikonu yüklenemedi")

    config = ConfigManager(CONFIG_PATH, DEFAULT_CONFIG)
    icons = IconManager()
    config.icons = icons
    panel = Panel(root, config, icons)

    def close_program():
        try:
            hotkeys.stop()
        except Exception:
            pass
        panel.win.destroy()
        sys.exit()

    hotkeys = HotkeyManager(
        config,
        on_toggle=panel.toggle,
        on_close=close_program,
        on_launch_app=launch_shortcut,
        schedule_fn=root.after
    )
    panel.hotkeys = hotkeys
    hotkeys.start()

    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log_error("main() genel hata")
        raise
