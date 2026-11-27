#!/bin/sh
# VoiceStudio (github.com/debpalash/VoiceStudio, AGPL-3.0; standart OmniVoice modeli
# CC-BY-NC — faqat notijorat) manbasini qotirilgan commit bilan shu papkaga yuklab,
# docs/install/linux.md "Building from source" bo'yicha o'rnatadi. Manba repoga kiritilmaydi.
#   sh tools/voicestudio/setup.sh        # bun install + Python backend (uv, CPU PyTorch)
#   Brauzer UI + backend (displeysiz):   bun run dev:web
# Kerak: bun, uv, Node 22.12+. Backend PyTorch'ni download.pytorch.org'dan, ovoz
# modellarini huggingface.co'dan oladi — bu hostlar tarmoqda ochiq bo'lishi shart.
set -e
COMMIT=202e2139814897a438541c707668e6ae90c159d2   # main, 2026-11-24 (0.5.9-beta.9)
HERE=$(cd "$(dirname "$0")" && pwd)
if [ ! -f "$HERE/package.json" ]; then
  TMP=$(mktemp -d)
  git -C "$TMP" init -q src
  git -C "$TMP/src" remote add origin https://github.com/debpalash/VoiceStudio.git
  git -C "$TMP/src" fetch -q --depth 1 origin "$COMMIT"
  git -C "$TMP/src" checkout -q FETCH_HEAD
  (cd "$TMP/src" && tar --exclude=.git -cf - .) | (cd "$HERE" && tar -xf -)
  rm -rf "$TMP"
fi
cd "$HERE"
node electron/scripts/node-version.mjs
bun install
bun run setup:api
echo "Tayyor. cd $HERE && bun run dev:web"
