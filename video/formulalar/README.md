# Ishlab chiqarish formulalari: video

## Holat (2026-10-15)

- **`Formulalar_v5.mp4` foydalanuvchi tomonidan maʼqullangan ("Juda ajoyib").** Keyingi versiyalar shu asosda davom etadi.
- **Uslub:** namuna video (noutbuk ekranidagi motion-design). Uning belgilari:
  - koʻk chizma toʻri va neon-yashil yorugʻlik;
  - bitta katta kanvas, kamera yashil lazer chizigʻi ortidan oʻngga, pastga yoki tepaga siljiydi;
  - uchqunli "payvandlash" yozuvi;
  - yashil→oq kinetik soʻzlar;
  - chizilib chiqadigan panellar va kursorli mono matn;
  - ↵ belgili yashil chaqnash, glitch va oq FORMA varagʻi.
  - Faqat 2D va 2.5D. Namunada yoʻq 3D va effektlar qoʻshilmaydi.
- **Fon:** misollar orqasida 2D ishlab chiqarish liniyalari:
  - payvandlash (robot qoʻllar, uchqunlar);
  - boʻyash (purkagichlar);
  - yigʻish (kran gʻildirak oʻrnatadi).
  - Sex nomlari hech qayerda yozilmaydi.
- **Matn:** qisqartmalar aytilmaydi, toʻliq nomlari aytiladi. Har bir formula uchun taʼrif va misol beriladi.
  - Inglizcha atamalar `{...}` ichida yoziladi va inglizcha oʻqiladi.
  - "ME Technology Department" yozuvi yoʻq.

## Foydalanuvchi quloq bilan tanlagan qoidalar

- ADM: oʻzbekcha "A-de-em".
- "Formula" soʻzi gap boshida emas, **"Formulasi quyidagicha: …"** shaklida ishlatiladi (C varianti).
- 100–199 soni "yuz" deb oʻqiladi, "bir yuz" emas.
- Qoʻshni jumlalar konteksti har doim `prepareUzbek` orqali yuboriladi.

## Keyingi ish (foydalanuvchi "kechga qilamiz" dedi)

- [ ] Foydalanuvchi **Uptime formulasini** yuboradi. Uni Uptime boʻlimiga qoʻshish kerak: formula, misol va animatsiya.
- [ ] Foydalanuvchi aytadigan boshqa qoʻshimchalarni kiritib, qayta ishlash.

## Qanday davom ettirish

```sh
cd video/formulalar
# 1) narration.json ga yangi jumlalarni yozing ({English} = inglizcha oʻqiladi)
# 2) faqat oʻzgargan jumlalarni qayta yozdiring:
(cd ../../studio && ONLY=up ATTEMPTS=3 npx tsx ../video/formulalar/narrate.mts)
python3 timeline.py   # VIEW/ORDER yangi jumla qoʻshilsa: timeline.py ORDER va film.html VIEW
#    so'z indekslari W('id', i) — timing.json dagi soʻzlar boʻyicha
# 3) serverni repo ildizidan ishga tushiring:
(cd ../.. && python3 -m http.server 8768 &)
python3 render.py probe 70 75     # tekshirish kadrlari -> probe/sheet.png
python3 audio.py && python3 render.py full
ffmpeg -i out/video.mp4 -i out/audio.wav -c:v libx264 -crf 22 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart Formulalar_v6.mp4
```
