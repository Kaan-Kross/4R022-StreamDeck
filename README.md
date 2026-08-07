<p align="center">
  <img src="assets/icon.png" width="140" alt="4R022 logosu">
</p>

<h1 align="center">4R022 StreamDeck 2.0V</h1>
<p align="center"><b>Fiziksel stream deck cihazlarının bedava, kod tabanlı karşılığı.</b></p>

<p align="center">
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows-0b0b0b?style=flat-square">
  <img alt="python" src="https://img.shields.io/badge/python-3.10%2B-ff2323?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-Proprietary-5a0d0d?style=flat-square">
  <img alt="status" src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square">
</p>

---

## Bu proje ne yapıyor?

**4R022 StreamDeck 2.0V**, klavyeden çağrılan, ekranın kenarından kayarak açılan,
uygulama ve web sitesi kısayollarını **ikon + isim** olarak gösteren kişisel
bir kontrol panelidir. Amaç basit: piyasadaki fiziksel "stream deck"
cihazlarının sunduğu hızlı erişim deneyimini, hiçbir ek donanım almadan,
tamamen yazılımla ve bedava sağlamak.

- 🎛️ Tek tuşla (`-`) açılıp kapanan, kayan ve animasyonlu bir panel
- 🧩 Sınırsız sayıda uygulama/web sitesi kısayolu — ekle, düzenle, kaldır
- 🌐 Web kısayolları için gerçek site favicon'u otomatik indirilir
- ⌨️ Her kısayola özel, atanabilir kendi klavye tuşu
- 🖥️ Çoklu monitör desteği — panelin hangi ekranda çıkacağını seç
- 🕐 4 köşeden birine yerleştirilebilir saat/tarih
- 🎨 Koyu tema, yuvarlak köşeli, hover efektli, elden geçirilmiş bir arayüz

---

## Ekran Görüntüsü

<p align="center">
  <img src="assets/icon.png" width="220" alt="4R022 StreamDeck 2.0V">
</p>

*(Panelin ve ayarlar ekranının gerçek ekran görüntülerini buraya ekleyebilirsin —
`assets/` klasörüne koyup bu satırı güncellemen yeterli.)*

---

## Kurulum

### Seçenek A — Hazır .exe ile (önerilen)

1. [Releases](../../releases) sekmesinden en güncel `4R022_StreamDeck.exe` dosyasını indir.
2. Çift tıkla, çalıştır. Kurulum gerekmez.
3. `keyboard` kütüphanesi global klavye kancası kullandığı için Windows'ta
   **yönetici olarak çalıştırman** gerekebilir.

### Seçenek B — Kaynak koddan çalıştırma

```bash
git clone <bu-repo-linki>
cd 4R022-StreamDeck
pip install -r requirements.txt
pythonw 4R022_StreamDeck.pyw
```

### Seçenek C — Kendi .exe'ni derleme

Windows'ta proje klasöründeyken:

```bash
build.bat
```

Bu script gerekli paketleri (PyInstaller dahil) kurar, ikonlu ve tek dosyalık
bir `.exe` üretir ve `dist/4R022_StreamDeck.exe` içine koyar.

---

## Kullanım

| Eylem | Nasıl |
|---|---|
| Paneli aç/kapat | `-` tuşu — **sadece klavye boştayken** çalışır, yazı yazarken tetiklenmez |
| Programı tamamen kapat | `K` + `R` + `S` tuşlarına 1 saniye içinde bas |
| Ayarları aç | Panelin sağ üstündeki ⚙ ikonuna tıkla |
| Yeni kısayol ekle | Panelin sonundaki **+** kareye tıkla ya da Ayarlar → Kısayollar → "+ Yeni Kısayol Ekle" |
| Kısayolu düzenle/kaldır | Kareye sağ tıkla → Düzenle / Kaldır, ya da Ayarlar listesinden ✎ / ✕ |
| Kısayola özel tuş ata | Ekle/Düzenle penceresinde "Tuş Ata" |
| Panel açma/kapama tuşunu değiştir | Ayarlar → Tuşlar |
| Kapatma kombinasyonunu düzenle | Ayarlar → Tuşlar → "+ Tuş Ekle" / "Kaldır" |
| Saatin yerini değiştir | Ayarlar → Saat (4 köşeden biri) |
| Panelin çıkacağı ekranı seç | Ayarlar → Ekran (çoklu monitör desteği) |

### Web sitesi ikonları

Web türündeki kısayollar için (YouTube, Discord, ChatGPT vb.) gerçek site
favicon'u otomatik indirilir ve yerel olarak önbelleklenir. İnternet yoksa ya
da kaynak yanıt vermezse, program çökmeden isme göre otomatik renkli bir
harf-rozeti üretir.

---

## Yapılandırma

Tüm ayarlar insan-tarafından okunabilir JSON olarak burada tutulur ve her
değişiklikte otomatik kaydedilir:

```
%APPDATA%\4R022\config.json
```

| Klasör/Dosya | İçerik |
|---|---|
| `%APPDATA%\4R022\config.json` | Kısayollar, tuşlar, saat, ekran, renk/boyut ayarları |
| `%APPDATA%\4R022\icon_cache` | İndirilen/çıkarılan ikonların önbelleği |
| `%APPDATA%\4R022\hata.log` | Hata kayıtları (`.pyw` konsolsuz çalıştığı için) |

---

## Mimari

```
ConfigManager     → JSON tabanlı ayar/kısayol saklama
IconManager       → .exe ikon çıkarımı + web favicon indirme + otomatik harf-rozeti
HotkeyManager     → event tabanlı (polling yok), "boşta mı yazıyor mu" tespiti dahil
Panel             → kayan ana pencere, animasyonlu ızgara, shimmer logo, saat
AppTile / AddTile → tıklanabilir kısayol kareleri (ana panelde)
AppRow            → kısayol satırları (Ayarlar listesinde)
SettingsWindow    → Kısayollar / Tuşlar / Saat / Ekran sekmeleri
AppEditDialog     → kısayol ekleme/düzenleme formu
```

Teknik notlar:
- Klavye kısayolları tamamen **event tabanlı** (`keyboard.hook`), polling yok.
- Panel kapanırken **alpha ile soluklaşarak** kayar ve tam kenara ulaşınca
  gizlenir — çoklu monitör kurulumlarında komşu ekranda görünmez.
- Fare tekerleği kaydırması, birden fazla kaydırılabilir pencere arasında
  çakışmayı önlemek için **tek bir global yönlendirici** üzerinden çalışır.

---

## Gereksinimler

```
keyboard>=0.13.5
pillow>=10.0.0
pywin32>=306
requests>=2.31.0
screeninfo>=0.8.1
```

`requirements.txt` içinde tam liste mevcuttur.

---

## Lisans

Bu proje **özel mülk (proprietary)** bir lisansla korunmaktadır — açık kaynak
değildir. Kodun kopyalanması, tersine mühendisliğe tabi tutulması ya da
izinsiz şekilde başka yerlerde paylaşılması yasaktır. Ayrıntılar için
[LICENSE](LICENSE) dosyasına bakın.

**4R022** markası ve bu yazılım © 2026 **Kaan Kross**'a aittir. Tüm hakları
saklıdır.

---

## Teşekkürler 💛

Bu, **4R022**'nin ilk gerçek projesi. Fikirden bu satırlara kadar sabırla,
yeniden yeniden düşünerek ve gerçekten kullanılabilir bir şey ortaya
koyabilmek için özenle inşa edildi.

Bu projeyi indirdiğin, incelediğin ya da kullandığın için — ve en başta
**4R022**'yi seçtiğin için teşekkürler. Daha iyisini yapmaya devam edeceğiz.

— Kaan Kross / 4R022
