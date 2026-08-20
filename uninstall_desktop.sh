#!/usr/bin/env bash
# SatSort - Linux Desktop & MIME Association Uninstaller
set -e

APP_FILE="$HOME/.local/share/applications/satsort.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/scalable/apps/satsort.svg"
MIME_FILE="$HOME/.local/share/mime/packages/satsort.xml"

echo "=== SatSort Linux Desktop Entegrasyonu Kaldırılıyor ==="

rm -f "$APP_FILE"
rm -f "$ICON_FILE"
rm -f "$MIME_FILE"

if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database "$HOME/.local/share/mime"
fi

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications"
fi

echo "✅ SatSort masaüstü entegrasyonu başarıyla kaldırıldı."
