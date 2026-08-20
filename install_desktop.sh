#!/usr/bin/env bash
# SatSort - Linux Desktop & MIME Association Installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
MIME_DIR="$HOME/.local/share/mime/packages"

echo "=== SatSort Linux Desktop Entegrasyonu Kuruluyor ==="

# 1. Dizinleri oluştur
mkdir -p "$APP_DIR" "$ICON_DIR" "$MIME_DIR"

# 2. İkonu kopyala
echo "-> İkon kopyalanıyor..."
cp "$SCRIPT_DIR/assets/satsort.svg" "$ICON_DIR/satsort.svg"

# 3. MIME tanımını kopyala ve güncelle
echo "-> .sdx MIME tipi kaydediliyor..."
cp "$SCRIPT_DIR/satsort-mime.xml" "$MIME_DIR/satsort.xml"
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database "$HOME/.local/share/mime"
fi

# 4. Masaüstü dosyasını dinamik yol ile kur
echo "-> Masaüstü kısayolu (desktop entry) kuruluyor..."
sed "s|Exec=.*|Exec=python3 $SCRIPT_DIR/main.py %f|g" "$SCRIPT_DIR/satsort.desktop" > "$APP_DIR/satsort.desktop"
chmod +x "$APP_DIR/satsort.desktop"

# 5. Masaüstü veritabanını güncelle
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR"
fi

echo "✅ SatSort başarıyla sisteme entegre edildi!"
echo "Artık .sdx dosyalarına çift tıklayarak doğrudan SatSort ile açabilirsiniz."
