---
name: cinematic-shorts
description: The user's standing quality bar for EVERY video (2026-10-18): only perfect, motion-rich videos with cinematic effects, and short-form (9:16 Shorts/Reels/TikTok) motion-graphics videos made from the user's own videos or in the style of reference videos they send. Use for any video request — cinematic film, short-form reel, "make a short from this video", "make it like this video", motion graphics with film look. Builds on motion-design / motion-reel (engine, render, audio) and adds the cinefx.js effects library, footage prep, reference analysis and a mandatory QA gate.
---

# Cinematic shorts — har bir video uchun sifat talabi

Foydalanuvchining doimiy talabi (2026-10-18): **faqat mukammal, motion effektlarga boy, kino effektli videolar**, hamda u yuborgan videolardan **Short-form Motion Graphics** (9:16) videolar.
Bu skill `motion-design` (seek(t) dvigateli, Playwright render, Mixkit/SFX, critique loop) va `motion-reel` (springs, beat grid) ustiga quriladi — o'shalarning qoidalari ham amal qiladi. O'zbekcha ovoz faqat `uzbek-tts` orqali.

## Tarkib
- `lib/cinefx.js` — kino effektlari (faqat t dan hisoblanadi, deterministik):
  - kamera: `shake` (qo'l kamerasi), `punch` (zarba), `zoomKeys` (log fazoda zoom), `keys` (kalit kadrlar), `spring` (yopiq prujina);
  - o'tishlar: `whip` (whip-pan, o'rtada kesish + blur), `flash`, `iris`, `glitch` (tilimli siljish), `chroma` (xromatik aberratsiya);
  - matn: `rise` (maskadan so'zma-so'z ko'tarilish), `decode` (scramble/dekoder), `counter` (raqam sanagich), `splitChars`;
  - post qatlam `mount(stage).frame(t, {...})`: `grain` (plyonka donasi, 24 fps), `vignette`, `letterbox` (2.39:1 gacha animatsiya), `leak` (light leak), `flare` (anamorf flare), `flash`, `grade` (`teal`/`warm`/`cold`/`mono`);
  - `dof(depth, focus)` — fokus xiralashuvi, `Footage` — video kadrlari ketma-ketligi, `ramp` — speed ramp (slow-mo ↔ tez).
- `scripts/analyze_ref.py VIDEO OUT` — namuna tahlili: o'lcham, fps, shotlar/kesishlar, o'rtacha shot uzunligi, palitra, LUFS, `shots.png` + `grid.png`.
- `scripts/prep_footage.py VIDEO OUT --ss --to --fps 30 --mode fill|crop|fit [--x 0.5]` — foydalanuvchi videosini 1080×1920 kadrlar ketma-ketligiga (+audio.wav) aylantiradi. `crop` — markazdan (yoki `--x` fokus), `fill` — xiralashgan fon (gorizontal videoni vertikalga), `fit` — qora maydon.
- `scripts/render_short.py HTML OUT.mp4 --dur S [--w 1080 --h 1920 --fps 30 --sub 4 --shutter .5 --cuts a,b --audio x.wav --root REPO --probe t1,t2 --chunk k/n --port P]` — subkadrli kino motion blur (180° shutter), kesishlarda ikki sahna ustma-ust tushmaydi, parallel bo'laklar.
- `scripts/matte.py FRAMES OUT [--model u2net_human_seg|birefnet-portrait|multiclass|selfie] [--smooth .6] [--feather 2]` — odamni fondan ajratish (alfa niqob `m_000001.png`). Bilan: **fon almashtirish**, **matn odam orqasida**, odam atrofida glow/outline, relight, faqat fonni xiralashtirish. HTML da: fon → orqa matn/grafika → `<img>` kadr + CSS `mask-image: url(m_XXXX.png)` (yoki canvas `destination-in`) → old grafika.
  - `u2net_human_seg` standart (~2-3 s/kadr, 4 yadro); `birefnet-portrait` eng aniq (soch), sekin — faqat master; MediaPipe `multiclass`/`selfie` tez, faqat yaqin kadr.
  - Talab: `pip install mediapipe "rembg[cpu]"`, `apt-get install -y libegl1 libgles2` (MediaPipe uchun). Modellar: `models/` (MediaPipe) va `~/.rembg/models` (rembg, birinchi ishlatishda yuklanadi).
  - Uzun klip uchun niqobni fonda ishga tushir; 30 fps × 20 s ≈ 600 kadr ≈ 25-30 daqiqa (u2net).
- Namuna: `video/shorts/demo_formulalar/` (short.html, audio.py — sintez saundtrek, build.sh).

## Ish tartibi
1. **Brif**: maqsad, platforma (Shorts/Reels/TikTok = 1080×1920, 30 yoki 60 fps; YouTube = 1920×1080), davomiylik (short 8–30 s), til, ovoz/musiqa. Savol qolsa — tavsiya bilan bitta savol.
2. **Namuna video berilgan bo'lsa**: `analyze_ref.py` → `grid.png`/`shots.png` ni ko'r (Read) → uslub kartasi yoz: kompozitsiya, kamera harakati, o'tishlar turi, matn animatsiyasi va shrifti, ranglar, ritm (shot uzunligi, BPM), effektlar. Faqat texnika olinadi; birovning kadrlari, qahramonlari, logolari, musiqasi ko'chirilmaydi. Juda murakkab boshqa birovning uslubi → `ReelMimic` (CLAUDE.md qoidasi: limit og'ir, avval ayt).
3. **Foydalanuvchi videosidan short**: `analyze_ref.py` bilan eng kuchli lahzalarni top (grid) → 3–6 klip × 1.5–4 s → `prep_footage.py` (gorizontal bo'lsa `fill` yoki fokusli `crop`) → `footage/` (git'ga kirmaydi).
4. **Beat map**: BPM → har kesish urg'uda; birinchi **1 soniyada hook** (kuchli sarlavha/harakat/savol); har 1.5–3 s da yangi vizual hodisa; hech narsa 1 s dan ortiq qotib turmaydi; eng kuchli lahza musiqa "drop"ida.
5. **Sahna HTML**: `cinefx.js` ni ulab, `window.seek(t)` ichida hammasini t dan hisobla. Har bir videoda kamida: kamera harakati (push-in/shake/punch), 2+ turdagi o'tish (whip, flash, iris, glitch, match-cut), kinetik matn, post qatlam (grain + vignette + rang + light leak/flare), kesishlarda zarba (punch + chroma), letterbox ochilish/yopilish kirish-chiqishda.
6. **Probe** (`--probe`, 6–12 kadr) → ko'r → tuzat. Keyin to'liq render (`--sub 4`, uzun bo'lsa `--chunk` 3 parallel) → audio mux.
7. **Ovoz**: Mixkit musiqa/SFX (`motion-design` §4) yoki `audio.py` uslubida sintez (drone, riser, boom, whoosh, kick); har SFX vizual hodisaga kadr aniqligida; `loudnorm -14 LUFS`. O'zbekcha diktor — faqat `uzbek-tts`, musiqa ovoz ostida ~9 dB pasaytiriladi.

## "Before → After" talking-head uslubi (namuna 2026-10-18)
Oddiy studiya intervyusi → premium reel: fon almashtirilgan (rangli devor + gobo/palma soyalari), iliq grade, katta sarlavha **odam orqasida** (matte), punch-in zoom (keng ↔ yaqin, crop bilan), kinetik sarlavha + subtitr, shisha (glassmorphism) UI kartochkalar, yoy chiziqlari, nur (light streak) chiziqlari, yumaloq burchakli "telefon" ramka. Before/After taqqoslash ko'rinishi: ikki ramka yonma-yon.
Kerak: foydalanuvchining xom (before) videosi ≥ 1080p, ovozi bilan. Ovozdan subtitr: so'zma-so'z timing (Whisper/ElevenLabs STT).

## Short-form qoidalari (9:16)
- Xavfsiz zona: matn tepadan ≥ 220 px, pastdan ≥ 380 px (platforma tugmalari), o'ngdan ≥ 140 px.
- Sarlavhalar: Montserrat/Unbounded 900 (raqamlar Oswald), o'zbek harflari faqat Inter/Montserrat/Onest/Oswald da to'liq; video ustida o'qilishi uchun to'q kartochka yoki kuchli soya.
- Ritm: o'rtacha shot 1.2–2.5 s; slow-mo faqat urg'u uchun (speed ramp); oxirida logo/CTA 1.5–2 s.
- Progress chizig'i, so'zma-so'z subtitrlar (ovoz bo'lsa: `remotion-captions` yoki o'z timing.json).

## Majburiy sifat tekshiruvi (yuborishdan oldin hammasi ✓)
- [ ] Hook birinchi 1 s da; hech bir kadr 1 s dan ortiq harakatsiz emas.
- [ ] Probe varaqda: matn kesilmagan, xavfsiz zonada, video matni bilan to'qnashmaydi.
- [ ] O'tishlar silliq (kesishda ikki sahna aralashmaydi — `--cuts`), motion blur bor (`--sub ≥ 4`).
- [ ] Post: grain + vignette + rang + flare/leak bor, lekin kontentni bosib ketmaydi.
- [ ] Ovoz: SFX hodisalarga mos, −14 LUFS, oxirida fade.
- [ ] Yakuniy faylni o'zing ko'r (kadrlar varag'i) va rostini ayt: nima zo'r, nima cheklov.
- [ ] Fayl hajmi > 30 MB bo'lsa, yuborish uchun siqilgan nusxa.
