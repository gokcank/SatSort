#!/usr/bin/env bash
# SatSort - Universal Linux AppImage Builder
set -e

VERSION="${TAG_NAME:-1.0.1}"
VERSION="${VERSION#v}"
APP_NAME="SatSort"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$ROOT_DIR/AppDir"
OUT_DIR="$ROOT_DIR/release_output"
APPIMAGE_TOOL="$ROOT_DIR/appimagetool-x86_64.AppImage"

echo "=== SatSort AppImage Paketi Derleniyor (v$VERSION) ==="

# 1. Eski derleme klasörlerini ve çıktıları temizle
echo "-> Eski derleme klasörleri temizleniyor..."
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist" "$APP_DIR"
mkdir -p "$APP_DIR" "$OUT_DIR"

# 2. PyInstaller ile standalone binary üret
echo "-> PyInstaller ile ikili dosya derleniyor..."
if ! command -v pyinstaller >/dev/null 2>&1; then
    echo "Hata: pyinstaller kurulu değil. Lütfen 'pip install pyinstaller' çalıştırın."
    exit 1
fi

cd "$ROOT_DIR"
pyinstaller --clean --noconfirm satsort.spec

# 3. AppDir yapısını oluştur
echo "-> AppDir dosya ağacı oluşturuluyor..."
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$APP_DIR/usr/share/mime/packages"

# İkili dosyayı ve varlıkları taşı
cp "$ROOT_DIR/dist/satsort" "$APP_DIR/usr/bin/satsort"
chmod +x "$APP_DIR/usr/bin/satsort"

# Masaüstü dosyası ve ikonları AppDir köküne ve sistem dizinlerine yerleştir
sed "s|Exec=.*|Exec=satsort %f|g" "$ROOT_DIR/satsort.desktop" > "$APP_DIR/satsort.desktop"
cp "$ROOT_DIR/assets/satsort.svg" "$APP_DIR/satsort.svg"
cp "$ROOT_DIR/assets/satsort.svg" "$APP_DIR/usr/share/icons/hicolor/scalable/apps/satsort.svg"
cp "$ROOT_DIR/assets/satsort.svg" "$APP_DIR/.DirIcon"
cp "$ROOT_DIR/satsort-mime.xml" "$APP_DIR/usr/share/mime/packages/satsort.xml"

# AppRun başlatıcı betiği
cat <<'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share:${XDG_DATA_DIRS}"
exec "${HERE}/usr/bin/satsort" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# 4. appimagetool indir (eğer yoksa)
if [ ! -f "$APPIMAGE_TOOL" ]; then
    echo "-> appimagetool indiriliyor..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$APPIMAGE_TOOL"
    chmod +x "$APPIMAGE_TOOL"
fi

# 5. AppImage oluştur
echo "-> AppImage paketi paketleniyor..."
export ARCH=x86_64
"$APPIMAGE_TOOL" "$APP_DIR" "$OUT_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"

# 6. Geçici klasörleri temizle
rm -rf "$APP_DIR"

echo "✅ Başarılı! AppImage konumu: $OUT_DIR/${APP_NAME}-${VERSION}-x86_64.AppImage"
