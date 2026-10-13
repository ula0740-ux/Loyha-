# Motion Studio: Remotion + oʻzbekcha ovoz

Matn yozasiz, ovoz tanlaysiz va MP4 video olasiz. Animatsiyalar **Remotion + React** da yasaladi. Ovoz har bir sahnaga sinxron qoʻyiladi: sahna aynan ovoz davomida turadi, soʻzlar esa aytilgan paytda ekranga chiqadi.

- Tillar: **oʻzbekcha** (lotin va kirill), **ruscha**, **inglizcha**.
- Ovozlar: **ayol** va **erkak**.
- Interfeys: brauzerda ochiladi, oʻzbek tilida.
- Eksport: **MP4** (H.264 + AAC) uch formatda: 9:16, 16:9, 1:1.

## Ishga tushirish

```bash
sudo apt-get install -y espeak-ng ffmpeg   # bepul oflayn ovoz + audio/video
pip install edge-tts                        # ixtiyoriy: Microsoft bepul ovozlari
npm install
npm run verify-tts                          # qaysi ovozlar haqiqatan ishlashini tekshiradi
npm start                                   # http://localhost:3000
```

Animatsiyani ovozsiz koʻrish va tahrirlash uchun Remotion Studio'ni oching: `npm run studio`.

## Ovoz xizmatlari va ularning tekshiruv natijasi

Interfeysda ovoz **“tekshirildi”** deb faqat bitta holatda belgilanadi: `npm run verify-tts` shu ovoz bilan oʻzbekcha (lotin va kirill), ruscha yoki inglizcha namunani gapirtirib, haqiqiy nutq olgan boʻlsa. Hech bir xizmatga oldindan “oʻzbek tilini biladi” deb belgi qoʻyilmagan.

| Xizmat | Turi | Holat (shu muhitda, 2026-10-12) |
|---|---|---|
| **eSpeak NG** | bepul, ochiq manba (GPL), oflayn | ✓ 6/6 ovoz tekshirildi: uz/ru/en × ayol/erkak. Oʻzbekcha **ishlaydi, lekin robotga oʻxshaydi** (formant sintez). |
| **Microsoft Edge** (Madina, Sardor…) | bepul, kalitsiz, onlayn (ochiq manba emas) | ✗ sinab boʻlmadi: tarmoq `speech.platform.bing.com` ni bloklagan. Kod tayyor. |
| **Azure AI Speech** | pullik, kalit | ulanmagan (`AZURE_SPEECH_KEY` kerak). Tekshirilmagan. |
| **Google Cloud TTS** | pullik, kalit | ulanmagan (`GOOGLE_TTS_API_KEY` kerak). Tillar API dan jonli olinadi. Tekshirilmagan. |
| **ElevenLabs** | pullik, kalit | ulanmagan. Oʻzbekcha sifati tekshirilmagan. |

Boshqa ochiq manbali variantlar ham koʻrib chiqildi:
- **Meta MMS-TTS** (oʻzbek modeli bor) va **Piper**: modellar HuggingFace'da turadi, bu muhitda u bloklangani uchun **sinab boʻlmadi**.
- **Coqui XTTS**: oʻzbek tilini qoʻllamaydi.

### Kirill yozuvi qanday ishlaydi

Testda eSpeak oʻzbekcha **kirill** matnni xato oʻqidi: `я`, `ш` harflari notoʻgʻri chiqdi. Lotin matnni esa toʻgʻri oʻqidi (gʻ, sh, ch, ng). Shuning uchun dastur kirill matnni ovozga yuborishdan oldin **avtomatik lotinga oʻgiradi**, ekranda esa matn siz yozgan yozuvda qoladi. Transliteratsiya 1995-yilgi rasmiy lotin alifbosi qoidalari asosida ishlaydi (`е`→`ye/e`, `ц`→`s/ts`, `ў`→`oʻ`, `ғ`→`gʻ`…). Interfeysdagi **“Matnni shu yozuvga oʻgirish”** tugmasi matnni ikki tomonga ham oʻgiradi.

### Pullik xizmat ulash

1. `cp .env.example .env` buyrugʻi bilan nusxa oling va kalitni yozing.
2. `npm run verify-tts` buyrugʻini ishga tushiring. Natija `data/tts-status.json` ga yoziladi, namunalarni interfeysda eshitish mumkin.
3. `npm start` bilan serverni qayta ishga tushiring. Yangi ovozlar roʻyxatda “tekshirildi” yoki “ishlamadi” belgisi bilan chiqadi.

Bulut muhitida (Claude Code on the web) xizmat manzilini **Network access → Allowed domains** ga qoʻshish kerak:
- Edge uchun: `speech.platform.bing.com`
- Azure uchun: `<region>.tts.speech.microsoft.com`
- ElevenLabs uchun: `api.elevenlabs.io`

## ElevenLabs (tabiiy ovoz, MP3)

Funksiya: `textToSpeechMp3(matn, "chiqish.mp3", { voiceId?, modelId?, languageCode? })`, fayli `server/tts/elevenlabsMp3.ts`.

- API kalit **faqat** `ELEVENLABS_API_KEY` muhit oʻzgaruvchisidan yoki `studio/.env` faylidan oʻqiladi. U kodga yozilmaydi, logga chiqmaydi va xato xabarlariga tushmaydi.
- `.env` fayli `.gitignore` da, shuning uchun GitHub'ga yuklanmaydi. Buni `git check-ignore -v studio/.env` buyrugʻi bilan tekshirish mumkin.

**Sozlash (oʻz kompyuteringizda):**
1. elevenlabs.io → Profile → **API Keys** boʻlimida kalit yarating.
2. **Voice Library** dan ovoz tanlang va uning **Voice ID** sini nusxalang.
3. `studio/.env` faylini toʻldiring:
   ```
   ELEVENLABS_API_KEY=...
   ELEVENLABS_VOICE_FEMALE=...
   ELEVENLABS_VOICE_MALE=...
   ```

**Bulut sessiyasida (Claude Code on the web):** kalitni chatga yozmang. Uni environment sozlamalariga kiriting: **Edit → Network secrets** yoki **environment variables**. Oʻsha yerda **Allowed domains** roʻyxatiga `api.elevenlabs.io` ni qoʻshing. Sozlamalar faqat yangi sessiyada kuchga kiradi.

**Testlar:**
- `npm test`: internetsiz unit testlar (fetch soxtalashtirilgan). Ular kalit faqat sarlavhada yuborilishini, xatolarda koʻrinmasligini, MP3 tekshiruvini va 401/tarmoq xatolarini sinaydi.
- `npm run test:elevenlabs ["matn"]`: haqiqiy API bilan sinov. Avval kalit va tarmoqni tekshiradi (`/v1/voices`), keyin oʻzbekcha MP3 yaratadi (`out/elevenlabs-test.mp3`) va uni ffprobe bilan tekshiradi. Oʻzbekcha talaffuz sifatini faylni tinglab, oʻzingiz baholaysiz.

## Oʻzbekcha talaffuz tizimi (lotin + kirill)

Fayllar: `server/uz/prepare.ts` (matnni tayyorlash), `server/uz/numbers.ts` (sonlar), `server/uz/lexicon.ts` va `lexicon/uz-lexicon.json` (talaffuz lugʻati), `server/uz/eleven.ts` (TTS, STT va A/B test), `scripts/uz.ts` (buyruqlar).

**Doimiy qoidalar:**
- **x = х** (chuqur x) va **h = ҳ** (yumshoq h). Bu ikki harf hech qachon bir-biriga almashtirilmaydi va tushirib qoldirilmaydi. Matn doim toʻgʻri adabiy imloda yoziladi.
- Harflar bittaga-bitta mos keladi: oʻ=ў, gʻ=ғ, q=қ, sh=ш, ch=ч, ng=нг, sʼh=сҳ.
- Lotincha x ni model inglizcha "eks" deb oʻqisa, imloni oʻzgartirib boʻlmaydi. Uning oʻrniga soʻz lugʻatga kirill shakli bilan yoziladi. Misol: Jizzax → `Жиззах` (STT testi: 100%).
- Aralash matnda har bir soʻzning tili aniqlanadi. Oʻzbekcha soʻzlar bitta tanlangan yozuvga oʻtkaziladi, ruscha va inglizcha soʻzlar oʻzgarmaydi, asl matn alohida saqlanadi.
- Sonlar, foizlar, sanalar, oraliqlar va qisqartmalar soʻz bilan yoziladi. Misollar: 2026-yil → "ikki ming yigirma oltinchi yil", 80,1% → "sakson butun oʻndan bir foiz", 5–7 → "beshdan yettigacha".
- API ga faqat model tekshiruvda qabul qilgan parametrlar yuboriladi. `language_code: "uz"` ni faqat `eleven_v4` qabul qiladi. `eleven_v3` va boshqa modellar 400 qaytaradi, shuning uchun ularga bu parametr yuborilmaydi. Standart model: `eleven_v3` (testda eng yaxshisi).

**Buyruqlar** (`studio/` ichida):
```
npm run uz -- prepare "ADM Jizzax 2026-yil"            # TTS ga nima ketishini koʻrsatadi (internetsiz)
npm run uz -- test "matn" [--model eleven_v4]          # lotin va kirillni ovozlab, STT bilan solishtiradi
npm run uz -- say "matn" out/a.mp3 [--min 0.9]         # eng yaxshi yozuvni tanlab MP3 yozadi + .json hisobot
npm run uz -- word Jizzax [--extra "Жиззах,..."]       # notoʻgʻri oʻqilgan soʻzni qayta sinab, lugʻatga yozadi
npm run uz -- lexicon list | add | approve | remove    # lugʻatni boshqarish
npm run uz -- stt fayl.mp3 "kutilgan matn"            # tayyor faylni tekshirish
```
STT orqali beriladigan baho taxminiy, chunki "eshituvchi" ham xato qilishi mumkin. Lugʻatdagi `candidate` shakllar quloq bilan tinglanib, `approve` buyrugʻi bilan tasdiqlanadi. Studiyada ElevenLabs bilan oʻzbekcha ovoz tanlansa, matn avtomatik shu tizimdan oʻtadi (yozuvni `UZ_SCRIPT=cyrillic` bilan tanlash mumkin). Subtitrda esa yozilgan asl soʻzlar koʻrinadi.

## Sinxronlash qanday ishlaydi

1. Har bir qator alohida sahna boʻladi va alohida ovozlashtiriladi.
2. Sahna davomiyligi quyidagicha hisoblanadi: 0.45 s (oʻtish animatsiyasi) + ovoz davomiyligi + 0.65 s.
3. Soʻzlarning vaqti ikki xil manbadan olinadi:
   - Edge va ElevenLabs soʻz chegaralarini aniq beradi.
   - eSpeak, Azure (REST) va Google bermaydi. Ular uchun vaqt nutqning haqiqiy boshlanish va tugash nuqtalari orasida boʻgʻin soniga qarab taqsimlanadi. Interfeys buni “taxminiy” deb koʻrsatadi.
4. `npm run test:e2e` tayyor MP4 dagi nutq boshlanishini oʻlchaydi va birinchi soʻz ekranga chiqqan vaqt bilan solishtiradi. Ruxsat etilgan farq ±0.2 s. Oxirgi natija: 0.01–0.03 s.

## Buyruqlar

| Buyruq | Vazifasi |
|---|---|
| `npm start` | Interfeys va render serveri |
| `npm run studio` | Remotion Studio (animatsiyani tahrirlash) |
| `npm run verify-tts [provider]` | Ovozlarni sinash |
| `npm run render-demo -- espeak:uz+f3 9:16` | Interfeyssiz demo video |
| `npm test` | Unit testlar (transliteratsiya, vaqt) |
| `npm run test:e2e` | Toʻliq zanjir + ovoz-tasvir sinxron testi |

## Tuzilma

```
src/            Remotion kompozitsiyasi (React): Video.tsx, Root.tsx, lib/uzbek.ts
server/         Express server, render pipeline, tts/ (espeak, edge, azure, google, elevenlabs)
ui/index.html   Oddiy veb-interfeys
scripts/        verify-tts, render-demo
tests/          unit + e2e testlar
```

## Litsenziya eslatmasi

Remotion jismoniy shaxslar va kichik kompaniyalar uchun bepul. Kattaroq kompaniyalar uchun kompaniya litsenziyasi talab qilinadi: https://remotion.dev/license. eSpeak NG GPL-3 litsenziyasida tarqatiladi.
