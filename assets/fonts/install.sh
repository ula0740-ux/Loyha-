#!/bin/sh
# Loyha shriftlarini tizimga o'rnatadi (PIL, LibreOffice/PowerPoint render, ffmpeg drawtext uchun).
# Yangi sessiyada bir marta: sh assets/fonts/install.sh
set -e
dir=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$HOME/.local/share/fonts"
cp "$dir"/*/*.ttf "$HOME/.local/share/fonts/"
fc-cache -f >/dev/null 2>&1 || true
echo "Shriftlar o'rnatildi: $(ls "$dir"/*/*.ttf | wc -l) fayl"
