#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_NAME="ezan-vakti-pro"
VERSION="1.0.0"
ARCH="all"
BUILD_ROOT="${REPO_DIR}/build_pkg/${PKG_NAME}_${VERSION}_${ARCH}"

echo "======================================================"
echo " Building Debian (.deb) Package: ${PKG_NAME}_${VERSION}"
echo "======================================================"

rm -rf "${REPO_DIR}/build_pkg"
mkdir -p "${BUILD_ROOT}/DEBIAN"
mkdir -p "${BUILD_ROOT}/usr/bin"
mkdir -p "${BUILD_ROOT}/usr/share/applications"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/256x256/apps"
mkdir -p "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${BUILD_ROOT}/usr/share/ezan-vakti-pro"
mkdir -p "${BUILD_ROOT}/usr/share/gnome-shell/extensions/ezan-vakti-pro@erdogan.github.com"

# 1. Control File
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/control"
Package: ezan-vakti-pro
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Maintainer: Erdoğan <erdogan@local>
Depends: python3, python3-gi, python3-cairo, gir1.2-gtk-4.0, gir1.2-adw-1, libnotify-bin
Description: Modern Diyanet Prayer Times for Ubuntu GNOME Wayland
 Ezan Vakti Pro is a sleek, modern Islamic prayer times and countdown
 application designed specifically for Ubuntu 26.04 Wayland and GNOME desktop.
 Features official Diyanet calculations, pre-prayer alarms, audio alerts,
 and GNOME top bar extension with customizable placement (right/center/left).
EOF

# 2. Post-installation Hook
cat << 'EOF' > "${BUILD_ROOT}/DEBIAN/postinst"
#!/bin/sh
set -e
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || true
fi
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"

# 3. Bin Launcher
cat << 'EOF' > "${BUILD_ROOT}/usr/bin/ezan-vakti-pro"
#!/bin/sh
exec /usr/bin/python3 /usr/share/ezan-vakti-pro/main.py "$@"
EOF
chmod 755 "${BUILD_ROOT}/usr/bin/ezan-vakti-pro"

# 4. Copy Codebase to /usr/share/ezan-vakti-pro/
cp "${REPO_DIR}/main.py" "${BUILD_ROOT}/usr/share/ezan-vakti-pro/"
cp -r "${REPO_DIR}/ezan_vakti_pro" "${BUILD_ROOT}/usr/share/ezan-vakti-pro/"

# 5. Desktop File
cp "${REPO_DIR}/ezan-vakti-pro.desktop" "${BUILD_ROOT}/usr/share/applications/"

# 6. Icons
cp "${REPO_DIR}/ezan_vakti_pro/assets/icon.png" "${BUILD_ROOT}/usr/share/icons/hicolor/256x256/apps/ezan-vakti-pro.png"
cp "${REPO_DIR}/ezan_vakti_pro/assets/icon.svg" "${BUILD_ROOT}/usr/share/icons/hicolor/scalable/apps/ezan-vakti-pro.svg"

# 7. GNOME Shell Extension
cp -r "${REPO_DIR}/gnome_extension/ezan-vakti-pro@erdogan.github.com"/* "${BUILD_ROOT}/usr/share/gnome-shell/extensions/ezan-vakti-pro@erdogan.github.com/"

# Set permissions
find "${BUILD_ROOT}/usr/share" -type d -exec chmod 755 {} +
find "${BUILD_ROOT}/usr/share" -type f -exec chmod 644 {} +
chmod 755 "${BUILD_ROOT}/usr/share/ezan-vakti-pro/main.py"
chmod 755 "${BUILD_ROOT}/DEBIAN/postinst"
chmod 755 "${BUILD_ROOT}/usr/bin/ezan-vakti-pro"

# 8. Build package with dpkg-deb
DEB_OUTPUT="${REPO_DIR}/${PKG_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "${BUILD_ROOT}" "${DEB_OUTPUT}"

echo "======================================================"
echo " SUCCESS! Package generated at:"
echo " ${DEB_OUTPUT}"
echo " Install with: sudo apt install ${DEB_OUTPUT}"
echo "======================================================"
