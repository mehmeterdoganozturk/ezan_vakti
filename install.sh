#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.local/share/ezan-vakti-pro"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
AUTOSTART_DIR="${HOME}/.config/autostart"
DBUS_DIR="${HOME}/.local/share/dbus-1/services"
ICON_DIR_PNG="${HOME}/.local/share/icons/hicolor/256x256/apps"
ICON_DIR_SVG="${HOME}/.local/share/icons/hicolor/scalable/apps"
EXT_DIR="${HOME}/.local/share/gnome-shell/extensions/ezan-vakti-pro@erdogan.github.com"

echo "=========================================================="
echo " Kurulum Başlatılıyor: Ezan Vakti Pro (Ubuntu Wayland / GNOME)"
echo "=========================================================="

mkdir -p "${TARGET_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${DESKTOP_DIR}"
mkdir -p "${AUTOSTART_DIR}"
mkdir -p "${DBUS_DIR}"
mkdir -p "${ICON_DIR_PNG}"
mkdir -p "${ICON_DIR_SVG}"
mkdir -p "${EXT_DIR}"

# 1. Copy Application
cp -r "${REPO_DIR}/main.py" "${TARGET_DIR}/"
cp -r "${REPO_DIR}/ezan_vakti_pro" "${TARGET_DIR}/"

# 2. Binary Launcher
cat << 'EOF' > "${BIN_DIR}/ezan-vakti-pro"
#!/usr/bin/env bash
exec /usr/bin/python3 "${HOME}/.local/share/ezan-vakti-pro/main.py" "$@"
EOF
chmod +x "${BIN_DIR}/ezan-vakti-pro"

# 3. Icons
cp "${REPO_DIR}/ezan_vakti_pro/assets/icon.png" "${ICON_DIR_PNG}/ezan-vakti-pro.png"
cp "${REPO_DIR}/ezan_vakti_pro/assets/icon.svg" "${ICON_DIR_SVG}/ezan-vakti-pro.svg"

# 4. Desktop Entry (Uygulama Menüsü)
cat << EOF > "${DESKTOP_DIR}/ezan-vakti-pro.desktop"
[Desktop Entry]
Name=Ezan Vakti Pro
GenericName=Ezan Vakti ve Namaz Takvimi
Comment=Ubuntu GNOME için Modern Diyanet Ezan Vakti ve Geri Sayım Uygulaması
Exec=${BIN_DIR}/ezan-vakti-pro %U
Icon=ezan-vakti-pro
Terminal=false
Type=Application
Categories=Utility;Clock;
Keywords=ezan;vakti;namaz;diyanet;takvim;imsakiye;kible;saat;prayer;
StartupNotify=true
StartupWMClass=com.github.erdogan.EzanVaktiPro
EOF
chmod +x "${DESKTOP_DIR}/ezan-vakti-pro.desktop"

# 4b. Autostart Desktop Entry (Oturum Açılışında Otomatik Başlama)
cat << EOF > "${AUTOSTART_DIR}/ezan-vakti-pro.desktop"
[Desktop Entry]
Type=Application
Name=Ezan Vakti Pro
GenericName=Ezan Vakti ve Namaz Takvimi
Comment=Ubuntu GNOME için Modern Diyanet Ezan Vakti ve Geri Sayım Uygulaması
Exec=${BIN_DIR}/ezan-vakti-pro --hidden
Icon=ezan-vakti-pro
Terminal=false
Categories=Utility;Clock;
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=1
StartupNotify=false
EOF
chmod +x "${AUTOSTART_DIR}/ezan-vakti-pro.desktop"

# 4c. D-Bus Service Auto-Activation (İhtiyaç Anında Otomatik Uyandırma)
cat << EOF > "${DBUS_DIR}/com.github.erdogan.EzanVaktiPro.service"
[D-BUS Service]
Name=com.github.erdogan.EzanVaktiPro
Exec=${BIN_DIR}/ezan-vakti-pro --hidden
EOF

# 5. GNOME Shell Extension
cp -r "${REPO_DIR}/gnome_extension/ezan-vakti-pro@erdogan.github.com"/* "${EXT_DIR}/"

# 6. Update Caches
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
fi

# 7. Enable Extension
python3 -c "
import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio
try:
    settings = Gio.Settings.new('org.gnome.shell')
    exts = list(settings.get_strv('enabled-extensions'))
    uuid = 'ezan-vakti-pro@erdogan.github.com'
    if uuid not in exts:
        exts.append(uuid)
        settings.set_strv('enabled-extensions', exts)
except Exception:
    pass
" 2>/dev/null || true

echo "=========================================================="
echo " TEBRİKLER! Ezan Vakti Pro & GNOME Extension Kuruldu!"
echo ""
echo " 1. Uygulama: 'ezan-vakti-pro' veya menüden açabilirsiniz."
echo " 2. Üst Bar: GNOME Extension 'ezan-vakti-pro@erdogan.github.com'"
echo "    sisteme kaydedildi ve aktifleştirildi."
echo " 3. Panel Yerleşimi: Ayarlardan Sağ / Orta / Sol seçebilirsiniz."
echo "=========================================================="
