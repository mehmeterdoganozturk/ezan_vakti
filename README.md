# Ezan Vakti Pro 🕌
**Ubuntu 26.04 (Wayland + GNOME 50) için Modern Diyanet Ezan Vakti ve Masaüstü Takvim Sistemi**

Diyanet İşleri Başkanlığı'nın resmi verilerini baz alan, modern **GTK4 / Libadwaita** arayüzü, saniyeli geri sayım sayacı, vakit öncesi uyarıları, sesli bildirimleri ve **GNOME Shell Üst Bar Uzantısı (Top Bar Extension)** ile donatılmış yeni nesil masaüstü ezan vakti uygulaması.

---

## 📑 İçindekiler
- [✨ Temel Özellikler](#-temel-özellikler)
- [🏗️ Sistem Mimarisi](#️-sistem-mimarisi)
- [🖥️ Ekranlar & Arayüz](#️-ekranlar--arayüz)
  - [Ana Sayaç Penceresi](#ana-sayaç-penceresi)
  - [GNOME Shell Üst Bar Uzantısı](#gnome-shell-üst-bar-uzantısı)
  - [Ayarlar & Bildirim Yönetimi](#ayarlar--bildirim-yönetimi)
- [🚀 Kurulum Seçenekleri](#-kurulum-seçenekleri)
  - [Seçenek 1: Hızlı Kullanıcı Kurulumu (Önerilen)](#seçenek-1-hızlı-kullanıcı-kurulumu-önerilen)
  - [Seçenek 2: Debian (.deb) Paketi ile Sistem Geneline Kurulum](#seçenek-2-debian-deb-paketi-ile-sistem-geneline-kurulum)
  - [Seçenek 3: Kaynak Koddan Doğrudan Çalıştırma](#seçenek-3-kaynak-koddan-doğrudan-çalıştırma)
- [🧩 GNOME Shell Uzantısı & Panel Konumlandırma](#-gnome-shell-uzantısı--panel-konumlandırma)
- [⚙️ Yapılandırma & Veri Depolama](#️-yapılandırma--veri-depolama)
- [📂 Proje Dizin Yapısı](#-proje-dizin-yapısı)
- [🗑️ Kaldırma](#️-kaldırma)
- [📜 Lisans & Telif Hakkı](#-lisans--telif-hakkı)

---

## ✨ Temel Özellikler

1. **Resmi Diyanet İşleri Başkanlığı Takvimi**:
   * Diyanet API'si üzerinden 30+ günlük vakit verilerini otomatik çeker ve yerel diskte önbelleğe alır.
   * **Çevrimdışı Güvencesi**: İnternet bağlantınız olmasa bile önbellekteki veriler sayesinde ezan saatleri ve geri sayım kesintisiz çalışır.
   * **İl & İlçe Arama Motoru**: Türkiye'nin 81 ili ve tüm ilçelerini (Ankara/Gölbaşı, Çankaya, Kadıköy vb.) tek tıkla arayıp seçebilirsiniz.
2. **Modern GTK4 & Libadwaita Tasarımı**:
   * **Sıfır Kaydırma (Zero Scroll)**: Ekrana tam oturan kompakt ve şık 2×3 vakit ızgarası (İmsak, Güneş, Öğle, İkindi, Akşam, Yatsı).
   * **Büyük Dijital Sayaç**: Vaktin çıkmasına veya sıradaki vakte kalan süreyi saniyesi saniyesine gösterir (`06:42:57`).
   * **Hicri Takvim & Kıble**: Miladi ve Hicri tarih gösterimi (Örn: *18 Cemaziyelevvel 1448*), Kıble açısı ve günlük Kıble saati bilgisi.
3. **GNOME Shell Üst Bar Uzantısı (Top Bar Extension)**:
   * Üst panelde canlı sayaç: `🕌 İmsak 06:05:12` (İkon + Vakit Adı + Kalan Süre).
   * Menü üzerinden tüm vakitler, kıble pusulası, ses aç/kapat ve hızlı pencere açma.
   * **Dinamik Konumlandırma**: Menüden veya ayarlardan **Sol**, **Orta** veya **Sağ** panel seçimi yapılabilir (Top Bar Organizer ile tam senkronize).
4. **Akıllı Ses & Uyarı Sistemi**:
   * **Erken Hatırlatma**: Vakit girmeden 5 ile 60 dakika önce hatırlatma bildirimi ve melodi.
   * **Vakit Anında Uyarı**: Vakit girdiği anda masaüstü afiş bildirimi ve ezan/tekbir sesi.
   * **Hızlı Sessize Alma (Mute)**: Tek tıkla tüm sesleri susturma seçeneği.
5. **Arka Plan Servisi & Otomatik Başlatma (Autostart)**:
   * Pencere kapatıldığında sistem tepsisinde/üst barda arka planda sessizce çalışmaya devam eder.
   * Bilgisayar veya oturum açıldığında `--hidden` parametresiyle arka planda otomatik başlar.
   * D-Bus Service Auto-Activation (`com.github.erdogan.EzanVaktiPro`) desteği.

---

## 🏗️ Sistem Mimarisi

```
+-------------------------------------------------------------+
|                     GNOME Shell 50                          |
|  [ 🕌 İmsak 05:43:21 ] -> Top Bar Extension (JavaScript)    |
+------------------------------▲------------------------------+
                               │ D-Bus IPC
                               ▼
+-------------------------------------------------------------+
|             Ezan Vakti Pro Arka Plan Servisi                |
|           (com.github.erdogan.EzanVaktiPro)                 |
|                                                             |
|  * Geri Sayım Motoru (Countdown Engine)                     |
|  * Diyanet & Aladhan API İstemcisi                          |
|  * 30 Günlük Yerel JSON Önbellek (Offline Cache)            |
|  * Ses Motoru (GSound / canberra / paplay / pw-play)        |
|  * GTK4 / Libadwaita Ana Arayüz Penceresi                   |
+-------------------------------------------------------------+
```

---

## 🖥️ Ekranlar & Arayüz

### Ana Sayaç Penceresi
* **Başlık**: İlçe Adı ve Diyanet Takvimi ibaresi.
* **Sayaç**: İçinde bulunulan vaktin çıkmasına kalan süre.
* **6'lı Vakit Izgarası**:
  * **İmsak / Güneş / Öğle / İkindi / Akşam / Yatsı** kartları.
  * İçinde bulunulan vakit altın sarısı/turuncu parıltıyla vurgulanır; sıradaki vakit yeşil çerçeveyle işaretlenir.
* **Alt Bilgi Çubuğu**: Kıble açısı ve Kıble saati rozeti, ses aç/kapat butonu, ayarlar düğmesi.

### GNOME Shell Üst Bar Uzantısı
* Üst barın solunda, ortasında veya sağında yer alır.
* Tıklandığında açılan açılır menü (dropdown):
  * Günün tüm vakitleri ve saatleri
  * Kıble bilgileri
  * Panel konumu değiştirme alt menüsü (⬅️ Sol / ⏸️ Orta / ➡️ Sağ)
  * Sesli uyarıları aç / kapat
  * Pencereyi Göster / Gizle
  * Uygulamayı Tamamen Kapat

---

## 🚀 Kurulum Seçenekleri

### Seçenek 1: Hızlı Kullanıcı Kurulumu (Önerilen)

Root yetkisi (`sudo`) gerektirmeden kullanıcı dizinine tek tıkla kurar:

```bash
cd /home/erdogan/Projects/ezan_vakti
chmod +x install.sh
./install.sh
```

**Bu betik otomatik olarak:**
1. Python uygulamasını ve ses dosyalarını `~/.local/share/ezan-vakti-pro/` dizinine kurar.
2. Terminalden çalıştırmak için `~/.local/bin/ezan-vakti-pro` sembolik linkini oluşturur.
3. GNOME masaüstü kısayolunu (`~/.local/share/applications/ezan-vakti-pro.desktop`) ekler.
4. GNOME Shell uzantısını `~/.local/share/gnome-shell/extensions/ezan-vakti-pro@erdogan.github.com` konumuna kurar ve etkinleştirir.
5. Oturum açılışında otomatik başlaması için `~/.config/autostart/ezan-vakti-pro.desktop` dosyasını yapılandırır.
6. D-Bus otomatik servis aktivasyonunu kaydeder.

### Seçenek 2: Debian (.deb) Paketi ile Sistem Geneline Kurulum

Ubuntu / Debian sistem genelinde (`/usr/bin`, `/usr/share`) kurmak için paket derleme:

```bash
cd /home/erdogan/Projects/ezan_vakti
chmod +x build_deb.sh
./build_deb.sh
```

Üretilen `.deb` paketini kurmak için:
```bash
sudo apt install ./ezan-vakti-pro_1.0.0_all.deb
```

Kaldırmak için:
```bash
sudo apt remove ezan-vakti-pro
```

### Seçenek 3: Kaynak Koddan Doğrudan Çalıştırma

Geliştirme veya test amacıyla derlemeden çalıştırmak için:

```bash
cd /home/erdogan/Projects/ezan_vakti
python3 main.py
```
Arka planda sessizce (penceresiz) başlatmak için:
```bash
python3 main.py --hidden
```

---

## 🧩 GNOME Shell Uzantısı & Panel Konumlandırma

Ezan Vakti Pro uzantısı, paneldeki konumunu dinamik olarak değiştirebilir:
* **Uzantı Menüsünden:** Panel simgesine tıklayın → `📍 Panel Konumu` alt menüsünden **Sol Taraf (Left)**, **Orta Kısım (Center)** veya **Sağ Taraf (Right)** seçeneğini işaretleyin.
* **Ayarlar Penceresinden:** Ayarlar ikonuna tıklayarak panel yerleşimini değiştirebilirsiniz.
* **Top Bar Organizer Uyumluluğu:** Sisteminizde `top-bar-organizer` eklentisi kuruluysa dconf konfigürasyonu otomatik senkronize edilir.

Uzantıyı manuel yeniden yüklemek gerekirse:
```bash
gnome-extensions disable ezan-vakti-pro@erdogan.github.com
gnome-extensions enable ezan-vakti-pro@erdogan.github.com
```

---

## ⚙️ Yapılandırma & Veri Depolama

Tüm kullanıcı tercihleri ve indirilen 30 günlük namaz vakitleri şu konumda saklanır:
* **Konfigürasyon Dosyası:** `~/.config/ezan-vakti-pro/config.json`
* **Yapılandırma Parametreleri**:
  * `country`: Ülke (Varsayılan: `Türkiye`)
  * `city`: İl (Örn: `Ankara`)
  * `district`: İlçe (Örn: `Gölbaşı`)
  * `panel_position`: Üst panel konumu (`"left"`, `"center"`, `"right"`)
  * `sound_enabled`: Sesli uyarılar açık/kapalı (`true`/`false`)
  * `early_warning_minutes`: Vakit öncesi hatırlatma süresi (Varsayılan: `15`)
  * `theme`: Arayüz teması (`"dark"`, `"light"`, `"system"`)

---

## 📂 Proje Dizin Yapısı

```
ezan_vakti/
├── LICENSE                        # Resmi MIT Lisans belgesi
├── README.md                      # Proje ana kullanım kılavuzu
├── install.sh                     # Kullanıcı dizinine otomatik kurulum betiği
├── uninstall.sh                   # Temiz kaldırma betiği
├── build_deb.sh                   # Debian (.deb) paketi derleme betiği
├── ezan-vakti-pro.desktop         # Masaüstü uygulama kısayolu
├── main.py                        # Python başlatıcı giriş noktası
├── ezan_vakti_pro/                # Çekirdek Python paketi
│   ├── app.py                     # Libadwaita / GTK4 ana penceresi ve ayarlar
│   ├── api.py                     # Diyanet & Aladhan API istemcisi
│   ├── dbus_service.py            # GNOME Shell D-Bus IPC servisi
│   ├── engine.py                  # Geri sayım, kıble ve vakit hesap motoru
│   ├── sound.py                   # Ses çalma yöneticisi (GSound, paplay, canberra)
│   └── assets/                    # İkonlar ve ses efektleri (.wav, .svg, .png)
└── gnome_extension/               # GNOME Shell Eklentisi
    └── ezan-vakti-pro@.../        # extension.js, metadata.json, stylesheet.css
```

---

## 🗑️ Kaldırma

Uygulamayı ve uzantıyı sistemden tamamen temizlemek için:

```bash
cd /home/erdogan/Projects/ezan_vakti
./uninstall.sh
```

---

## 📜 Lisans & Telif Hakkı

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak lisanslanmıştır.  
© 2026 **Mehmet Erdoğan Öztürk** <mehmeterdoganozturk@gmail.com>
