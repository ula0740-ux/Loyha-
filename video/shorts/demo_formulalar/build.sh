#!/bin/sh
# Demo short (13 s, 1080x1920) ni noldan qayta yig'ish. Repo ildizidan: sh video/shorts/demo_formulalar/build.sh
set -e
D=video/shorts/demo_formulalar; S=.claude/skills/cinematic-shorts/scripts; V=video/formulalar/Formulalar_v5.mp4
python3 $S/prep_footage.py $V $D/footage/a --ss 22.8 --to 25.8 --fps 30 --mode crop
python3 $S/prep_footage.py $V $D/footage/b --ss 55.2 --to 58.4 --fps 30 --mode crop
python3 $S/prep_footage.py $V $D/footage/c --ss 71.4 --to 75.6 --fps 30 --mode crop
python3 $S/prep_footage.py $V $D/footage/d --ss 249.4 --to 253.0 --fps 30 --mode crop
(cd $D && python3 audio.py)
for k in 0 1 2; do python3 $S/render_short.py $D/short.html $D/part$k.mp4 --root . --dur 13 --fps 30 --sub 4 --chunk $k/3 --port 879$k --cuts 1.6,9.4 & done; wait
printf "file 'part0.mp4'\nfile 'part1.mp4'\nfile 'part2.mp4'\n" > $D/parts.txt
ffmpeg -v error -y -f concat -safe 0 -i $D/parts.txt -i $D/audio.wav -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart $D/Formulalar_short_demo.mp4
rm -f $D/part?.mp4 $D/parts.txt
