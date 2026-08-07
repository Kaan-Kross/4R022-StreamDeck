# Değişiklik Geçmişi

Bu proje [Semantic Versioning](https://semver.org/lang/tr/) kurallarını takip eder.

## [2.0V] — 2026

### 4R022 StreamDeck 2.0V 🎉
- Kayan, animasyonlu, koyu temalı ana panel
- Sınırsız uygulama/web kısayolu — ekle, düzenle, kaldır (hizalı & animasyonlu ızgara)
- Web kısayolları için otomatik favicon indirme + önbellekleme
- .exe dosyalarından otomatik ikon çıkarımı (pywin32)
- İkon bulunamazsa otomatik renkli harf-rozeti üretimi
- Event tabanlı klavye kısayolları (polling yok):
  - Panel açma/kapama tuşu (varsayılan `-`) — sadece klavye boştayken tetiklenir
  - K+R+S kapatma kombinasyonu
  - Kısayol başına özel tuş atama
- Ayarlar penceresi: Kısayollar / Tuşlar / Saat / Ekran sekmeleri
- Çoklu monitör desteği (screeninfo)
- Saat/tarih için 4 köşe seçeneği
- Alpha destekli, komşu monitörde flaş vermeyen kayma animasyonu
- Kayan "shimmer" logo animasyonu
- Kendi uygulama ikonu (.ico) ve marka kimliği
- Fare tekerleği kaydırması için tek global yönlendirici (çakışma yok)
- Tek dosyalık .exe derleme script'i (`build.bat`)
