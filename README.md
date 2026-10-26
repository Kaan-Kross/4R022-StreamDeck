<p align="center">
  <img src="assets/icon.png" width="140" alt="4R022 logosu / 4R022 logo">
</p>

<h1 align="center">4R022 StreamDeck 3.0V</h1>
<p align="center"><b>Fiziksel stream deck cihazlarının bedava, kod tabanlı karşılığı.</b></p>
<p align="center"><i>The free, code-based alternative to physical stream deck devices.</i></p>

<p align="center">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-0b0b0b?style=flat-square">
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-ff2323?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-Proprietary-5a0d0d?style=flat-square">
  <img alt="version" src="https://img.shields.io/badge/version-3.0V-brightgreen?style=flat-square">
  <img alt="languages" src="https://img.shields.io/badge/dil%2Flanguage-TR%20%7C%20EN-blue?style=flat-square">
</p>
<p align="center">
  <img alt="CI" src="https://github.com/REPO_OWNER/REPO_NAME/actions/workflows/ci.yml/badge.svg">
  <img alt="Release" src="https://github.com/REPO_OWNER/REPO_NAME/actions/workflows/release.yml/badge.svg">
</p>

> Not / Note: Yukarıdaki iki CI/Release rozetinin çalışması için
> `REPO_OWNER/REPO_NAME` kısmını depoyu yükledikten sonra kendi
> kullanıcı adın/depo isminle değiştirmen gerekir (ör. `KaanKross/4R022-StreamDeck`).
> / For the two CI/Release badges above to work, replace `REPO_OWNER/REPO_NAME`
> with your actual username/repo name after uploading (e.g. `KaanKross/4R022-StreamDeck`).

---

## Bu proje ne yapıyor?

**4R022 StreamDeck**, klavyeden çağrılan, ekranın kenarından kayarak açılan,
uygulama ve web sitesi kısayollarını **ikon + isim** olarak gösteren kişisel
bir kontrol panelidir. Amaç basit: piyasadaki fiziksel "stream deck"
cihazlarının sunduğu hızlı erişim deneyimini, hiçbir ek donanım almadan,
tamamen yazılımla ve bedava sağlamak.

### What does this project do?

**4R022 StreamDeck** is a personal control panel, summoned from the
keyboard, that slides in from the edge of the screen and shows your
application and website shortcuts as **icon + name** tiles. The goal is
simple: deliver the same quick-access experience physical "stream deck"
devices offer, entirely in software, with no extra hardware and no cost.

---

## 🎉 3.0V ile gelenler — İlk büyük sürüm atlamamız

Bu sürüm, **4R022 StreamDeck**'in ilk gerçek büyük sürüm atlaması. 2.0V'dan
buraya, sadece küçük düzeltmelerle değil; alt yapının önemli bir kısmının
yeniden düşünüldüğü, gerçek çoklu-platform desteğinin ve çok dilli
arayüzün geldiği, tüm arayüzün gözden geçirildiği kapsamlı bir güncelleme
ile geldik.

### What's new in 3.0V — Our first major version leap

This release marks **4R022 StreamDeck**'s first true major version jump.
This isn't a small patch from 2.0V — it's a substantial update that
rethinks a meaningful part of the infrastructure, brings real
cross-platform support and a multi-language interface, and gives the
entire UI a thorough overhaul.

### ✅ Eklenenler (Added)

- **3 platform desteği**: Windows, Linux ve macOS artık resmi olarak
  destekleniyor. Uygulama veri klasörü, uygulama başlatma yöntemi ve fare
  tekerleği olayları her işletim sistemine göre otomatik uyarlanıyor.
- **Dil seçimi (TR/EN)**: Ayarlar'a yeni bir **"Genel"** sekmesi eklendi.
  Türkçe ve İngilizce arasında anında geçiş yapılabiliyor; dil değişince
  ilgili pencere otomatik olarak yeni dille yeniden açılıyor.
- **Monitör taşma güvenliği**: Panelin "kapalı" konumu artık matematiksel
  olarak monitör sınırını asla aşamayacak şekilde hesaplanıyor
  (`safe_x` kenetlemesi). Windows'ta ayrıca işlem, DPI-aware olarak
  işaretleniyor; bu da Tkinter'ın gördüğü koordinatlarla gerçek fiziksel
  monitör koordinatları arasındaki ölçekleme kaymasını ortadan kaldırıyor.
- **Profesyonel arayüz yenilemesi**:
  - Ayarlar penceresi artık ana panelden belirgin şekilde daha açık,
    katmanlı bir antrasit palet kullanıyor (simsiyah değil).
  - Tüm butonlar yuvarlak köşeli, hover'da yumuşak renk geçişli, tıklamada
    hafif "bas" animasyonlu yeni bir `RoundedButton` bileşenine taşındı.
  - Kısayol listesi kart tasarımına kavuştu (ikon + isim + tür/tuş rozeti
    + düzenle/kaldır simgeleri).
  - Sekme başlıklarındaki emojiler kaldırılıp sade, tutarlı bir tipografiye
    geçildi.
  - Ayarlar ve Ekle/Düzenle pencereleri artık yumuşak bir "fade-in" ile
    açılıyor.
  - Panel'deki kısayol kareleri artık ani değil, yumuşak geçişli hover
    animasyonu kullanıyor; panel çerçevesine ince bir "cam panel" highlight
    detayı eklendi.
- **Klavye kısayolları için çökmeyen hata yönetimi**: `keyboard` modülü
  Linux'ta izin sorunu yaşarsa ya da macOS'ta Erişilebilirlik izni
  verilmemişse, uygulama artık çökmüyor — Ayarlar'da nedenini ve çözümünü
  açıkça gösteriyor.
- **Genel/Platform bilgisi**: Ayarlar'daki yeni sekmede uygulamanın hangi
  işletim sisteminde çalıştığı görüntüleniyor.

### ➖ Kaldırılanlar / Değişenler (Removed / Changed)

- Ayarlar'daki eski düz `tk.Button` tabanlı butonlar tamamen kaldırıldı,
  yerini `RoundedButton` aldı.
- Sekme başlıklarındaki renkli emoji simgeler (🧩 ⌨ 🕐 🖥 🌐) kaldırıldı.
- Ayarlar ve Panel artık **ayrı renk paletleri** kullanıyor
  (`config["panel"]` ve `config["settings"]`) — önceden ikisi de aynı
  simsiyah paleti paylaşıyordu.
- Fare tekerleği kaydırması artık uygulama genelinde **tek bir global
  yönlendirici** üzerinden çalışıyor; önceki sürümde birden fazla
  kaydırılabilir pencere açıldığında birbirini eziyordu.

### Added

- **3-platform support**: Windows, Linux, and macOS are now officially
  supported. The app data directory, the app-launch method, and mouse
  wheel event handling all adapt automatically per operating system.
- **Language selection (TR/EN)**: A new **"General"** tab was added to
  Settings. You can switch instantly between Turkish and English; the
  relevant window automatically reopens in the new language.
- **Monitor overflow safety**: The panel's "closed" position is now
  computed so it can mathematically never exceed the monitor boundary
  (the `safe_x` clamp). On Windows, the process is also marked
  DPI-aware, eliminating the scaling mismatch that previously existed
  between Tkinter's reported coordinates and the real physical monitor
  coordinates.
- **Professional UI overhaul**:
  - The Settings window now uses a noticeably lighter, layered charcoal
    palette instead of near-black.
  - All buttons were migrated to a new `RoundedButton` component with
    rounded corners, smooth hover color transitions, and a subtle
    "press" animation on click.
  - The shortcut list now uses a card design (icon + name + type/hotkey
    badge + edit/remove icons).
  - Emoji were removed from tab labels in favor of clean, consistent
    typography.
  - Settings and Add/Edit windows now open with a smooth fade-in.
  - Shortcut tiles on the main panel now use smooth hover transitions
    instead of instant color swaps; a subtle "glass panel" highlight
    line was added to the panel's outer frame.
- **Crash-proof hotkey handling**: if the `keyboard` module fails to
  start due to a Linux permissions issue or a missing macOS
  Accessibility permission, the app no longer crashes — Settings now
  clearly explains why and how to fix it.
- **General/Platform info**: the new Settings tab shows which operating
  system the app is currently running on.

### Removed / Changed

- The old flat `tk.Button`-based buttons in Settings were fully removed
  and replaced with `RoundedButton`.
- Colorful emoji icons on tab labels (🧩 ⌨ 🕐 🖥 🌐) were removed.
- Settings and the Panel now use **separate color palettes**
  (`config["panel"]` and `config["settings"]`) — previously both shared
  the same near-black palette.
- Mouse wheel scrolling now runs through a **single global router** for
  the whole app; in the previous version, opening more than one
  scrollable window at once could break the other's scrolling.

---

## Ekran Görüntüleri / Screenshots

<table>
<tr>
<td align="center"><b>Panel</b></td>
<td align="center"><b>Ayarlar — Kısayollar / Settings — Shortcuts</b></td>
</tr>
<tr>
<td><img src="assets/screenshots/panel.png" width="260"></td>
<td><img src="assets/screenshots/settings.png" width="380"></td>
</tr>
<tr>
<td align="center"><b>Ayarlar — Genel (Dil) / Settings — General (Language)</b></td>
<td align="center"><b>Kısayol Ekle / Add Shortcut</b></td>
</tr>
<tr>
<td><img src="assets/screenshots/general.png" width="380"></td>
<td><img src="assets/screenshots/dialog.png" width="340"></td>
</tr>
</table>

---

## Özellikler / Features

- 🎛️ Tek tuşla (`-`) açılıp kapanan, kayan ve animasyonlu bir panel
- 🧩 Sınırsız sayıda uygulama/web sitesi kısayolu — ekle, düzenle, kaldır
- 🌐 Web kısayolları için gerçek site favicon'u otomatik indirilir
- ⌨️ Her kısayola özel, atanabilir kendi klavye tuşu
- 🖥️ Çoklu monitör desteği — panelin hangi ekranda çıkacağını seç
- 🕐 4 köşeden birine yerleştirilebilir saat/tarih
- 🌍 **Yeni:** Türkçe / İngilizce arayüz dili
- 💻 **Yeni:** Windows, Linux ve macOS desteği
- 🎨 Profesyonel, katmanlı, yuvarlak köşeli ve animasyonlu arayüz

<br>

- 🎛️ A single key (`-`) toggles a sliding, animated panel
- 🧩 Unlimited app/website shortcuts — add, edit, remove
- 🌐 Real site favicons are downloaded automatically for web shortcuts
- ⌨️ Each shortcut can have its own assignable hotkey
- 🖥️ Multi-monitor support — choose which screen the panel appears on
- 🕐 Clock/date placeable in any of the 4 corners
- 🌍 **New:** Turkish / English interface language
- 💻 **New:** Windows, Linux, and macOS support
- 🎨 A professional, layered, rounded-corner, animated interface

---

## Kurulum / Installation

> ⚠️ **Önemli:** Bu depoda hazır bir `.exe`/çalıştırılabilir dosya
> **yoktur**. Aşağıdaki "Kendi çalıştırılabilir dosyanı oluştur"
> adımıyla kendi platformun için birini üretebilirsin.

> ⚠️ **Important:** This repository does **not** include a pre-built
> `.exe`/executable. Use the "Build your own executable" step below to
> produce one for your platform.

### 🤖 Otomatik derleme (GitHub Actions ile) / Automatic builds (via GitHub Actions)

Bu depo, `.github/workflows/release.yml` içinde bir GitHub Actions
iş akışı içerir. Bir sürüm etiketi (ör. `v3.0.0`) gönderdiğinde, Windows
(.exe), Linux ve macOS için otomatik olarak çalıştırılabilir dosyalar
derlenir ve doğrudan **Releases** sayfasına eklenir — elle `build.bat`
çalıştırmana gerek kalmaz:

```bash
git tag v3.0.0
git push origin v3.0.0
```

This repository includes a GitHub Actions workflow at
`.github/workflows/release.yml`. When you push a version tag (e.g.
`v3.0.0`), it automatically builds executables for Windows (.exe),
Linux, and macOS and attaches them directly to the **Releases** page —
no need to run `build.bat` by hand:

```bash
git tag v3.0.0
git push origin v3.0.0
```

### 🔧 Kendi çalıştırılabilir dosyanı oluştur (Windows, elle)

1. Bu depoyu indir (yeşil **Code** butonu → **Download ZIP**, ya da `git clone`)
2. Zip'i çıkar, klasörün içine gir
3. **`build.bat`** dosyasına çift tıkla
4. Açılan pencere otomatik olarak gerekli her şeyi kurup derleyecek — bekle
5. İşlem bitince şurada hazır `.exe`'n olacak: `dist\4R022_StreamDeck.exe`

### 🔧 Build your own executable (Windows, manual)

1. Download this repository (green **Code** button → **Download ZIP**, or `git clone`)
2. Extract the zip and enter the folder
3. Double-click **`build.bat`**
4. The window that opens will automatically install everything needed and
   build the app — just wait
5. When it's done, your `.exe` will be at: `dist\4R022_StreamDeck.exe`

### 🐍 Doğrudan Python ile çalıştırma (tüm platformlar)

```bash
git clone <bu-repo-linki>
cd 4R022-StreamDeck
pip install -r requirements.txt
python 4R022_StreamDeck.pyw
```

Windows'ta konsol penceresi açılmasın istiyorsan `python` yerine
`pythonw` kullanabilirsin.

### 🐍 Running directly with Python (all platforms)

```bash
git clone <this-repo-link>
cd 4R022-StreamDeck
pip install -r requirements.txt
python 4R022_StreamDeck.pyw
```

On Windows, use `pythonw` instead of `python` if you don't want a
console window to appear.

> **Not / Note:** `keyboard` kütüphanesi global klavye kancası
> kullandığı için Windows'ta yönetici olarak, Linux'ta `sudo` ile ya da
> kullanıcını `input` grubuna ekleyerek çalıştırman gerekebilir.
> macOS'ta Sistem Ayarları → Gizlilik ve Güvenlik → Erişilebilirlik'ten
> izin vermen gerekir. / The `keyboard` library uses a global keyboard
> hook, so on Windows you may need to run as administrator, on Linux
> with `sudo` or by adding your user to the `input` group, and on macOS
> you need to grant permission under System Settings → Privacy &
> Security → Accessibility.

---

## Kullanım / Usage

| Eylem / Action | Nasıl / How |
|---|---|
| Paneli aç/kapat / Toggle the panel | `-` tuşu — sadece klavye boştayken çalışır / the `-` key — only triggers when the keyboard is idle |
| Programı tamamen kapat / Fully quit the app | `K` + `R` + `S` tuşlarına 1 saniye içinde bas / press `K` + `R` + `S` within 1 second |
| Ayarları aç / Open Settings | Panelin sağ üstündeki ⚙ ikonuna tıkla / click the ⚙ icon top-right of the panel |
| Yeni kısayol ekle / Add a new shortcut | Panelin sonundaki **+** kareye tıkla ya da Ayarlar → Kısayollar / click the **+** tile at the end of the panel, or Settings → Shortcuts |
| Kısayolu düzenle/kaldır / Edit or remove a shortcut | Kareye sağ tıkla, ya da Ayarlar listesinden ✎/✕ / right-click the tile, or use ✎/✕ in the Settings list |
| Kısayola özel tuş ata / Assign a hotkey to a shortcut | Ekle/Düzenle penceresinde "Tuş Ata" / "Assign Key" in the Add/Edit window |
| Panel açma/kapama tuşunu değiştir / Change the toggle key | Ayarlar → Tuşlar / Settings → Hotkeys |
| Kapatma kombinasyonunu düzenle / Edit the quit combo | Ayarlar → Tuşlar → "+ Tuş Ekle" / Settings → Hotkeys → "+ Add Key" |
| Saatin yerini değiştir / Move the clock | Ayarlar → Saat / Settings → Clock |
| Panelin çıkacağı ekranı seç / Choose which monitor the panel appears on | Ayarlar → Ekran / Settings → Display |
| **Arayüz dilini değiştir / Change the interface language** | **Ayarlar → Genel / Settings → General** |

---

## Yapılandırma / Configuration

Tüm ayarlar insan-tarafından okunabilir JSON olarak saklanır ve her
değişiklikte otomatik kaydedilir. Konum işletim sistemine göre değişir:

All settings are stored as human-readable JSON and saved automatically
on every change. The location depends on your operating system:

| Platform | Konum / Location |
|---|---|
| Windows | `%APPDATA%\4R022\` |
| macOS | `~/Library/Application Support/4R022/` |
| Linux | `~/.config/4R022/` (ya da `$XDG_CONFIG_HOME/4R022/`) |

| Dosya / File | İçerik / Content |
|---|---|
| `config.json` | Kısayollar, tuşlar, saat, ekran, dil, renk/boyut ayarları / shortcuts, hotkeys, clock, display, language, color/size settings |
| `icon_cache/` | İndirilen/çıkarılan ikonların önbelleği / cache of downloaded/extracted icons |
| `hata.log` | Hata kayıtları / error log |

---

## Mimari / Architecture

```
ConfigManager     → JSON tabanlı ayar/kısayol saklama / JSON-based settings & shortcut storage
IconManager       → .exe ikon çıkarımı + web favicon indirme + otomatik harf-rozeti
                     .exe icon extraction + web favicon download + automatic letter-badge fallback
HotkeyManager     → event tabanlı, çapraz-platform toleranslı kısayol yönetimi
                     event-based, cross-platform-tolerant hotkey management
Panel             → kayan ana pencere, animasyonlu ızgara, shimmer logo, saat
                     the sliding main window, animated grid, shimmer logo, clock
RoundedButton     → yuvarlak köşeli, hover/tıklama animasyonlu profesyonel buton bileşeni
                     rounded-corner professional button component with hover/click animation
AppTile / AddTile → tıklanabilir kısayol kareleri (ana panelde) / clickable shortcut tiles (on the panel)
AppRow            → kısayol satırları (Ayarlar listesinde) / shortcut rows (in the Settings list)
SettingsWindow    → Kısayollar / Tuşlar / Saat / Ekran / Genel sekmeleri
                     Shortcuts / Hotkeys / Clock / Display / General tabs
AppEditDialog     → kısayol ekleme/düzenleme formu / the add/edit shortcut form
STRINGS / t()     → TR/EN çeviri sözlüğü ve çeviri yardımcı fonksiyonu
                     the TR/EN translation dictionary and translation helper function
```

### Teknik notlar / Technical notes

- Klavye kısayolları tamamen **event tabanlı**'dır (`keyboard.hook`), polling yok.
  / Hotkeys are fully **event-based** (`keyboard.hook`), no polling.
- Panel kapanırken **alpha ile soluklaşarak** kayar ve tam kenara ulaşınca
  gizlenir — çoklu monitör kurulumlarında komşu ekranda görünmez.
  / The panel fades via **alpha** while sliding closed and is hidden
  once it reaches the edge — it never appears on a neighboring monitor
  in multi-monitor setups.
- Panelin kapalı konumu, monitör genişliğini asla aşamayacak şekilde
  matematiksel olarak kenetlenir (`safe_x`); Windows'ta ayrıca işlem
  DPI-aware işaretlenir.
  / The panel's closed position is mathematically clamped so it can
  never exceed the monitor width (`safe_x`); on Windows the process is
  also marked DPI-aware.
- Fare tekerleği kaydırması, birden fazla kaydırılabilir pencere
  arasında çakışmayı önlemek için **tek bir global yönlendirici**
  üzerinden çalışır.
  / Mouse wheel scrolling runs through a **single global router** to
  prevent conflicts between multiple scrollable windows.
- Renk paletleri Panel ve Ayarlar için **ayrı** tutulur
  (`config["panel"]` / `config["settings"]`), böylece Ayarlar her zaman
  daha açık ve okunur kalır.
  / Color palettes are kept **separate** for the Panel and Settings
  (`config["panel"]` / `config["settings"]`), so Settings always stays
  lighter and more readable.

---

## Gereksinimler / Requirements

```
keyboard>=0.13.5
pillow>=10.0.0
pywin32>=306      (yalnızca Windows / Windows only)
requests>=2.31.0
screeninfo>=0.8.1
```

`requirements.txt` içinde tam liste mevcuttur. `pywin32`, Windows dışı
platformlarda otomatik atlanır — kurulmasa da uygulama çökmez.

The full list is in `requirements.txt`. `pywin32` is automatically
skipped on non-Windows platforms — the app won't crash if it's missing.

---

## Lisans / License

Bu proje **özel mülk (proprietary)** bir lisansla korunmaktadır — açık
kaynak değildir. Kodun kopyalanması, tersine mühendisliğe tabi
tutulması ya da izinsiz şekilde başka yerlerde paylaşılması yasaktır.
Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.

This project is protected under a **proprietary** license — it is not
open source. Copying the code, reverse-engineering it, or
redistributing it without permission is prohibited. See the
[LICENSE](LICENSE) file for details.

**4R022** markası ve bu yazılım © 2026 **Kaan Kross**'a aittir. Tüm
hakları saklıdır.

The **4R022** brand and this software are © 2026 **Kaan Kross**. All
rights reserved.

---

## Teşekkürler / Acknowledgements

Bu, 4R022 StreamDeck'in ilk büyük sürüm atlaması — ayrıntılı bir
teşekkür notu için [TEŞEKKÜRLER.md](TEŞEKKÜRLER.md) dosyasına bakabilirsin.

This is 4R022 StreamDeck's first major version leap — see
[TEŞEKKÜRLER.md](TEŞEKKÜRLER.md) for a detailed note of thanks.

— Kaan Kross / 4R022
