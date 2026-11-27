# Open Generative AI — Higgsfield o'rniga

**Nima qiladi:** matndan rasm va video yaratadi. Bitta dasturda rasm, video, lipsync va "kino" studiyalari bor.
**Litsenziya:** MIT (bepul, ochiq kod).
**Muallif:** Anil Matcha (GitHub: Anil-matcha).

## Rasmiy havolalar

| Nima | Havola |
|---|---|
| GitHub sahifasi | https://github.com/Anil-matcha/Open-Generative-AI |
| Yuklab olish (Releases) | https://github.com/Anil-matcha/Open-Generative-AI/releases |
| Brauzer versiyasi | https://muapi.ai/open-generative-ai |

## Qachon bepul, qachon pullik — avval shuni biling

- **Lokal modellar (kompyuterning o'zida) — bepul.** Ular faqat kompyuterga o'rnatilgan dasturda ishlaydi.
- **Bulut modellari (Kling, Veo, Sora va boshqalar) — pullik.** Ular Muapi.ai xizmati orqali ishlaydi va Muapi kaliti (API key) kerak bo'ladi. Narxini muapi.ai saytida ko'ring.
- Brauzer versiyasi faqat bulut modellarini ishlatadi.

## Talablar

| | |
|---|---|
| Mac | Apple Silicon (M1–M4) va Intel uchun alohida fayl bor |
| Windows | 64-bit (x64) |
| Linux | Ubuntu x64 (`.AppImage` yoki `.deb`) |
| RAM | Z-Image modeli uchun 16 GB tavsiya qilinadi. 8 GB'li Mac'da faqat SD 1.5 modellarini ishlating |
| Disk | Har bir rasm modeli taxminan 2–7 GB. Kamida 10–15 GB bo'sh joy |
| Lokal video | Faqat NVIDIA yoki AMD videokarta bilan (Wan2GP orqali). Mac'da lokal video yo'q |

---

## O'rnatish — eng oson yo'l (tayyor dastur)

1. **Releases** sahifasini oching: https://github.com/Anil-matcha/Open-Generative-AI/releases
2. Eng yuqoridagi (eng yangi) versiyaning **Assets** qismidan o'zingizga mos faylni yuklab oling:
   - **Mac, Apple Silicon (M1–M4):** nomida `arm64` bor `.dmg` fayl.
   - **Mac, Intel:** nomida `arm64` yo'q `.dmg` fayl.
   - **Windows:** `Open Generative AI Setup ... .exe`
   - **Linux:** `.deb` (Ubuntu uchun tavsiya qilinadi) yoki `.AppImage`.
3. Faylni oching va o'rnating:
   - **Mac:** `.dmg` ni oching va dastur belgisini **Applications** papkasiga torting.
   - **Windows:** `.exe` ni ishga tushiring. Dastur o'zi o'rnatiladi va **Пуск / Start** menyusida paydo bo'ladi.
   - **Linux (.deb):**
     ```bash
     sudo apt install ./open-generative-ai_*_amd64.deb
     ```
   - **Linux (.AppImage):**
     ```bash
     chmod +x Open\ Generative\ AI-*.AppImage
     ./Open\ Generative\ AI-*.AppImage
     ```

### Mac "ochib bo'lmaydi" desa (bu normal holat)

Dastur Apple'da ro'yxatdan o'tmagan, shuning uchun Mac birinchi marta uni to'sadi. Bu faqat bir marta kerak.

**Terminal'siz yo'l:**
1. Dasturni bir marta ochib ko'ring (to'siladi).
2. **System Settings** ("Tizim sozlamalari") → **Privacy & Security** ("Maxfiylik va xavfsizlik") bo'limiga kiring.
3. Pastroqda **Open Anyway** ("Baribir ochish") tugmasini bosing, keyin **Open**.

**Terminal yo'li:**
```bash
xattr -cr "/Applications/Open Generative AI.app"
```
So'ng **Applications** papkasida dasturni o'ng tugma bilan bosing → **Open** → yana **Open**.

### Windows ogohlantirsa

Ko'k "Windows protected your PC" oynasi chiqsa: **More info** ("Подробнее") → **Run anyway** ("Выполнить в любом случае").

### Ubuntu 24.04 va yangilarida ochilmasa

`.deb` faylini ishlating. U kerakli sozlamani o'zi qo'yadi. AppImage eski tizimda ochilmasa:
```bash
sudo apt install libfuse2
```

---

## Boshqa yo'llar

- **Brauzerda, o'rnatmasdan:** https://muapi.ai/open-generative-ai. Ro'yxatdan o'tish bepul, lekin rasm va videolar bulut modellari orqali yaratiladi, ya'ni pullik.
- **Manba koddan (dasturchilar uchun):** Node.js v18 yoki yangisi kerak.
  ```bash
  git clone --recurse-submodules https://github.com/Anil-matcha/Open-Generative-AI.git
  cd Open-Generative-AI
  npm run setup
  npm run electron:dev
  ```
  `npm install` yetarli emas, `npm run setup` majburiy.

---

## Birinchi marta ishlatish (bepul, lokal model bilan)

1. Dasturni oching va **Settings** ("Sozlamalar") → **Local Models** ("Lokal modellar") bo'limiga kiring.
2. Bitta model tanlab, yuklab oling:
   - 8 GB RAM bo'lsa — **Dreamshaper 8** (taxminan 2 GB).
   - 16 GB va undan ko'p bo'lsa — **Z-Image Turbo**.
3. Yuklab olish tugashini kuting. Internetga qarab bir necha daqiqa ketadi.
4. Rasm studiyasiga o'ting, lokal modelni tanlang, rasm tavsifini yozing va yarating.

Muapi kalitini kiritish shart emas. U faqat bulut modellari uchun kerak.

## Muammo chiqsa

- **Mac'da ochilmayapti** → yuqoridagi "Mac ochib bo'lmaydi desa" bo'limi.
- **8 GB'li Mac qotib qoldi** → dasturni yoping va Z-Image o'rniga SD 1.5 modelini (Dreamshaper 8) tanlang.
- **"API key" so'rayapti** → siz bulut modelini tanlagansiz. Lokal modelga o'ting.
- **Boshqa xato** → https://github.com/Anil-matcha/Open-Generative-AI/issues
