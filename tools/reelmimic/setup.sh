#!/bin/sh
# ReelMimic'ni (github.com/edenfunf/reelmimic) yuklab, o'rnatadi va Loyha'ning o'zbekcha ovozini ulaydi.
#   sh tools/reelmimic/setup.sh [maqsad papka, standart: ../reelmimic]
set -e
HERE=$(cd "$(dirname "$0")" && pwd); LOYHA=$(cd "$HERE/../.." && pwd)
DEST=${1:-$LOYHA/../reelmimic}
[ -d "$DEST/.git" ] || git clone --depth 1 https://github.com/edenfunf/reelmimic.git "$DEST"
cp "$HERE/uz_tts.py" "$DEST/.claude/skills/video-clone/scripts/uz_tts.py"
grep -q "O‘zbekcha ovoz (ElevenLabs)" "$DEST/CLAUDE.md" || { echo; cat "$HERE/UZBEK.md"; } >> "$DEST/CLAUDE.md"
grep -q "O‘zbekcha ovoz (ElevenLabs)" "$DEST/AGENTS.md" || { echo; cat "$HERE/UZBEK.md"; } >> "$DEST/AGENTS.md"
mkdir -p "$HOME/.reelmimic"
if [ ! -f "$HOME/.reelmimic/secrets.json" ]; then
  CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)
  printf '{\n  "CHROME_PATH": "%s",\n  "BUILDERS": "3",\n  "MAX_AGENTS": "6"\n}\n' "$CH" > "$HOME/.reelmimic/secrets.json"
fi
cd "$DEST" && bash install.sh
echo "Tayyor. Ishga tushirish: cd $DEST && bash start.sh  ->  http://localhost:4318"
