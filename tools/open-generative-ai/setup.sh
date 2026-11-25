#!/bin/sh
# Open Generative AI (github.com/Anil-matcha/Open-Generative-AI, MIT) manbasini
# qotirilgan commit bilan shu papkaga yuklab, o'rnatadi. Manba, node_modules va
# build natijalari repoga kiritilmaydi (.gitignore) — faqat shu skript kiritiladi.
#   sh tools/open-generative-ai/setup.sh
#   Web (Next.js, faqat bulut modellari, Muapi kaliti kerak):  npm run dev  ->  http://localhost:3000
#   Desktop (Electron, lokal modellar): npm run electron:dev — faqat displeyli kompyuterda.
# README'dagi `npm run setup` = submodule update + npm install + build:packages.
# Bu yerda submodullar vaqtinchalik klonda olinadi, .git papkalar ko'chirilmaydi
# (aks holda Loyha repo ichida ichma-ich repo paydo bo'ladi), shuning uchun
# setup'ning qolgan ikki qadami to'g'ridan-to'g'ri chaqiriladi.
set -e
COMMIT=f1b8359baecab053d177b1b6df60704db6ea0fa4   # main, 2026-11-24 (v2.0.0)
HERE=$(cd "$(dirname "$0")" && pwd)
if [ ! -f "$HERE/package.json" ]; then
  TMP=$(mktemp -d)
  git -C "$TMP" init -q src
  git -C "$TMP/src" remote add origin https://github.com/Anil-matcha/Open-Generative-AI.git
  git -C "$TMP/src" fetch -q --depth 1 origin "$COMMIT"
  git -C "$TMP/src" checkout -q FETCH_HEAD
  git -C "$TMP/src" submodule update --init --recursive --depth 1
  (cd "$TMP/src" && tar --exclude=.git -cf - .) | (cd "$HERE" && tar -xf -)
  rm -rf "$TMP"
fi
cd "$HERE"
npm install
npm run build:packages
echo "Tayyor. Web: cd $HERE && npm run dev  ->  http://localhost:3000"
