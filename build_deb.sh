#!/usr/bin/env bash
# SatSort - Debian / Ubuntu (.deb) Package Builder
set -e

VERSION="1.0.0"
ARCH="amd64"
PKG_NAME="satsort_${VERSION}_${ARCH}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_TMP="$ROOT_DIR/build_deb_tmp"
OUT_DIR="$ROOT_DIR/release_output"

echo "=== SatSort .deb Paketi Derleniyor (v$VERSION) ==="

# 1. Eski derleme kalıntılarını tamamen temizle
echo "-> Eski derleme klasörleri temizleniyor..."
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist" "$BUILD_TMP"
mkdir -p "$BUILD_TMP" "$OUT_DIR"

# 2. PyInstaller ile standalone binary üret
echo "-> PyInstaller ile ikili dosya derleniyor..."
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Hata: pyinstaller kurulu değil. Lütfen 'pip install pyinstaller' çalıştırın."
    exit 1
fi

cd "$ROOT_DIR"
pyinstaller --clean --noconfirm satsort.spec

# 3. Debian paket ağacını oluştur
echo "-> Debian paket dosya ağacı kuruluyor..."
PKG_ROOT="$BUILD_TMP/$PKG_NAME"
mkdir -p "$PKG_ROOT/DEBIAN"
mkdir -p "$PKG_ROOT/usr/bin"
mkdir -p "$PKG_ROOT/usr/share/applications"
mkdir -p "$PKG_ROOT/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$PKG_ROOT/usr/share/mime/packages"

# Dosyaları kopyala
cp "$ROOT_DIR/dist/satsort" "$PKG_ROOT/usr/bin/satsort"
chmod +x "$PKG_ROOT/usr/bin/satsort"

# Masaüstü dosyası (Exec yolunu sistem yolu olarak ayarla)
sed "s|Exec=.*|Exec=/usr/bin/satsort %f|g" "$ROOT_DIR/satsort.desktop" > "$PKG_ROOT/usr/share/applications/satsort.desktop"
cp "$ROOT_DIR/assets/satsort.svg" "$PKG_ROOT/usr/share/icons/hicolor/scalable/apps/satsort.svg"
cp "$ROOT_DIR/satsort-mime.xml" "$PKG_ROOT/usr/share/mime/packages/satsort.xml"

# 4. DEBIAN/control dosyasını oluştur
cat <<EOF > "$PKG_ROOT/DEBIAN/control"
Package: satsort
Version: $VERSION
Section: video
Priority: optional
Architecture: $ARCH
Maintainer: Gokcan <https://github.com/gokcank>
Depends: libc6
Description: Modern Linux Native SatcoDX Channel List Editor
 SatSort is a visual channel list editor for satellite receivers
 using the SatcoDX (.sdx) format.
EOF

# 5. postinst ve postrm betiklerini oluştur (Masaüstü ve MIME veritabanını güncellemek için)
cat <<EOF > "$PKG_ROOT/DEBIAN/postinst"
#!/bin/sh
set -e
if [ "\$1" = "configure" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications || true
    fi
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database /usr/share/mime || true
    fi
fi
EOF
chmod 755 "$PKG_ROOT/DEBIAN/postinst"

cat <<EOF > "$PKG_ROOT/DEBIAN/postrm"
#!/bin/sh
set -e
if [ "\$1" = "remove" ] || [ "\$1" = "purge" ]; then
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications || true
    fi
    if command -v update-mime-database >/dev/null 2>&1; then
        update-mime-database /usr/share/mime || true
    fi
fi
EOF
chmod 755 "$PKG_ROOT/DEBIAN/postrm"

# 6. .deb paketini oluştur
echo "-> dpkg-deb paketi üretiliyor..."
dpkg-deb --build --root-owner-group "$PKG_ROOT" "$OUT_DIR/${PKG_NAME}.deb"

# 7. Geçici klasörleri temizle
rm -rf "$BUILD_TMP"

echo "✅ Başarılı! Paket konumu: $OUT_DIR/${PKG_NAME}.deb"
