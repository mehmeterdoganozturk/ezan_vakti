# Ezan Vakti Pro 🕌
**Ubuntu 26.04 (Wayland + GNOME 50) için Modern Diyanet Ezan Vakti ve Takvim Uygulaması**

Diyanet İşleri Başkanlığı'nın resmi verilerini baz alan, modern **GTK4 / Libadwaita** arayüzü, gelişmiş geri sayım sayacı, vakit öncesi uyarıları, sesli bildirimleri ve **GNOME Shell Üst Bar Uzantısı (Top Bar Extension)** ile donatılmış masaüstü ezan vakti uygulaması.

---

## ✨ Özellikler

1. **Resmi Diyanet Takvimi**:
   - Diyanet API'si üzerinden 32 günlük vakit verilerini otomatik çeker ve yerel diskte önbelleğe alır. Çevrimdışı (internetsiz) ortamlarda da sorunsuz çalışır.
   - İl ve İlçe arama/seçme diyaloğu ile Türkiye'deki tüm il ve ilçeler desteklenir.
2. **Modern ve Sade Arayüz (Libadwaita / GTK4)**:
   - Aktif vakit ve sıradaki vakit için özel renkli vurgu kartları.
   - Saniyeli hassas geri sayım sayacı (`06:42:57`).
   - Hicri tarih gösterimi (Örn: *18 Cemaziyelevvel 1448*).
   - Kıble açısı ve günlük Kıble saati bilgisi.
   - Kaydırma çubuğu gerektirmeyen, ekrana tam oturan kompakt ve zarif kart tasarımı.
3. **GNOME Shell Top Bar Uzantısı**:
   - Üst barda sıradaki vakit adını ve kalan süreyi canlı gösterir (Örn: `🕌 İmsak 06:05:12`).
   - Tıklandığında açılan menüden tüm günün vakitlerini, kıble bilgilerini ve ses durumunu gösterir.
   - **Dinamik Panel Yerleşimi**: Menüden veya ayarlardan **Sol Taraf**, **Orta Kısım** veya **Sağ Taraf** seçilerek paneldeki konumu anında değiştirilebilir (Top Bar Organizer uyumlu).
4. **Akıllı Bildirim ve Ses Sistemi**:
   - **Vakit Öncesi Uyarılar**: İsteğe bağlı olarak vakit girmeden 5-60 dk önce erken hatırlatma bildirimi ve melodi çalar.
   - **Vakit Anında Uyarılar**: Vakit girdiğinde sistem masaüstü afiş bildirimi ve ezan/çan sesi çalar.
   - Tek tıkla sesi tamamen sessize alma (Mute) desteği.
5. **Arka Plan ve Otomatik Başlatma (Autostart)**:
   - Pencere kapatıldığında arka planda sessizce çalışmaya devam eder.
   - Bilgisayar veya oturum açıldığında `--hidden` parametresiyle arka planda otomatik başlar.
   - D-Bus Service Auto-Activation desteği (`com.github.erdogan.EzanVaktiPro`).

---

## 🚀 Kurulum Seçenekleri

### Seçenek 1: Hızlı Kullanıcı Kurulumu (Önerilen)
```bash
cd /home/erdogan/Projects/ezan_vakti
./install.sh
```
Kurulum otomatik olarak:
* Uygulamayı `~/.local/share/ezan-vakti-pro` dizinine yükler.
* `~/.local/bin/ezan-vakti-pro` başlatıcısını oluşturur.
* GNOME uzantısını `~/.local/share/gnome-shell/extensions/` dizinine kurar ve aktifleştirir.
* Otomatik başlatma (autostart) ve D-Bus servislerini kaydeder.

### Seçenek 2: Debian (.deb) Paketi ile Sistem Geneline Kurulum
Paketi derlemek ve kurmak için:
```bash
cd /home/erdogan/Projects/ezan_vakti
./build_deb.sh
sudo apt install ./ezan-vakti-pro_1.0.0_all.deb
```

---

## ⚙️ Yapılandırma ve Veri Konumu
* Ayarlar ve önbelleğe alınmış takvim verileri `~/.config/ezan-vakti-pro/config.json` dosyasında tutulur.
* Ayarlar penceresinden tema (Karanlık / Aydınlık / Sistem), erken uyarı süreleri, her vakit için ayrı ayrı ses/bildirim tercihleri değiştirilebilir.

---

## 🗑️ Kaldırma
```bash
cd /home/erdogan/Projects/ezan_vakti
./uninstall.sh
```
Veya `.deb` paketi ile kurulduysa:
```bash
sudo apt remove ezan-vakti-pro
```
