#!/usr/bin/env bash
set -e

echo "Ezan Vakti Pro kaldırılıyor..."

# 1. Çalışan süreçleri durdur
pkill -f "ezan-vakti-pro" 2>/dev/null || true

# 2. Dosyaları temizle
rm -rf "${HOME}/.local/share/ezan-vakti-pro"
rm -f "${HOME}/.local/bin/ezan-vakti-pro"
rm -f "${HOME}/.local/share/applications/ezan-vakti-pro.desktop"
rm -f "${HOME}/.config/autostart/ezan-vakti-pro.desktop"
rm -f "${HOME}/.local/share/dbus-1/services/com.github.erdogan.EzanVaktiPro.service"
rm -f "${HOME}/.local/share/icons/hicolor/256x256/apps/ezan-vakti-pro.png"
rm -f "${HOME}/.local/share/icons/hicolor/scalable/apps/ezan-vakti-pro.svg"
rm -rf "${HOME}/.local/share/gnome-shell/extensions/ezan-vakti-pro@erdogan.github.com"
rm -rf "${HOME}/.local/share/gnome-shell/extensions/ezan-vakti@erdogan.github.com"

# 3. Önbellekleri güncelle
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${HOME}/.local/share/applications" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f "${HOME}/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo "Kaldırma işlemi başarıyla tamamlandı."
