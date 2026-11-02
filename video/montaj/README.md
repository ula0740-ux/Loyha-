# Montaj: "Birinchi qadamlar"

- `namuna/namuna.mp4`: foydalanuvchi bergan namuna (Sony kino-reklama uslubi, "Olov, Havo, Suv, Yer"), 720×480, 24 fps, 66.8 s.
- `tahlil/`: namuna tahlili. `ref.json` kesishlar (47 ta, o'rtacha 1.42 s), palitra va loudness (−15.9 LUFS); `beats.js` tempo (143.93 BPM).
- `kirish/`: foydalanuvchi videolari (IMG_2026–2036) va rasmlari (rasm_01–10).
- `montaj.py`: montaj dvigateli (Python + OpenCV, kadrma-kadr).
- `chiqish/Birinchi_qadamlar.mp4`: tayyor montaj.

## Uslub
- Namunaning 47 ta kesish vaqti va musiqasi aynan saqlangan, shuning uchun har bir kesish zarbga tushadi.
- Tuzilishi: kirish (16:9 kino oynasi, detallar) → "bir kichik / qahramon haqida" → 4 bo'lim:
  KASHFIYOT (iliq oltin), JASORAT (sovuq po'lat), QUVONCH (firuza), QADAM (tuproq rangi, musiqa cho'qqisi) → tez kesishlar va oq chaqnashlar → epilog "Har bir qadam / bir kashfiyot" → "BIRINCHI QADAMLAR".
- O'tishlar: zarbdagi punch-in, whip (21.6 s, 33.6 s), drop nur portlashi (12.1 s, 47.9 s), iliq nur oqimi, oq chaqnash.
- Ko'rinish: har bo'limga alohida rang, halation, vinyetka, plyonka donadorligi.

## Qayta yasash
```bash
cd video/montaj && mkdir -p ish/src
for n in 2026 2027 2028 2029 2031 2032 2036; do ffmpeg -y -i kirish/IMG_$n.MOV -an -vf "hqdn3d=1.5:1.5:4:4,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,setsar=1,format=yuv420p" -r 30 -c:v libx264 -crf 14 -g 1 ish/src/$n.mp4; done
pip install opencv-python-headless
python3 montaj.py probe 3.6 13 49   # tekshiruv kadrlari
python3 montaj.py render
```
