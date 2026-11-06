# ADM JIZZAX AJ — yig'uv paneli: o'rnatish (taxminan 15 daqiqa, bir marta)

Kerak: Google (Gmail) hisobi va kompyuterda Chrome.

## 1. Google jadval ochish
1. [sheets.new](https://sheets.new) manzilini oching. Yangi bo'sh jadval ochiladi.
2. Chap yuqoridagi nomini bosing va **ADM JIZZAX AJ — panel ma'lumotlari** deb yozing.

Bu jadval ma'lumotlar ombori bo'ladi. Varaqlar (Avto, Kunlik, MQS, Reja, Grafik va boshqalar) o'zi yaratiladi, ularni qo'lda o'zgartirmang.

## 2. Kodni qo'yish
1. Jadvalda menyudan **Kengaytmalar → Apps Script** (Extensions → Apps Script) ni bosing.
2. Ochilgan oynada `Code.gs` faylidagi hamma matnni o'chiring va shu papkadagi **Code.gs** faylining ichini to'liq nusxalab qo'ying.
3. Chapdagi **Fayllar** yonidagi **+** belgisini bosing va **HTML** ni tanlang. Nomiga `index` deb yozing (".html" qo'shilmaydi).
4. Ichidagi matnni o'chirib, shu papkadagi **index.html** faylining ichini to'liq qo'ying.
5. Yuqoridagi 💾 (Saqlash) tugmasini bosing.

## 3. Saytni ishga tushirish (Deploy)
1. O'ng yuqoridagi **Deploy (Joylashtirish) → New deployment (Yangi joylashtirish)** ni bosing.
2. ⚙ belgisini bosib, **Web app (Veb-ilova)** ni tanlang.
3. Sozlamalar:
   - **Execute as (Kim nomidan ishlaydi):** *Me (siz)*
   - **Who has access (Kim kira oladi):**
     - *Anyone* — havolani bilgan hamma (Google hisobsiz ham) ko'radi;
     - *Anyone with Google account* — faqat Google hisobi bilan kirganlar.
4. **Deploy** ni bosing. Google ruxsat so'raydi: **Authorize access → hisobingizni tanlang → Advanced → Go to ... (unsafe) → Allow**. Bu sizning o'z skriptingiz, xavfsiz.
5. **Web app URL** chiqadi — bu saytning havolasi.

## 4. Ikki xil havola
- **Ko'rish uchun** (rahbariyat, boshqa bo'limlar): `.../exec`
- **Yurituvchilar uchun** (Boshqaruv tugmasi ko'rinadi): `.../exec?boshqaruv`

Birinchi marta `?boshqaruv` havolasini ochib, **Boshqaruv**ga kiring va **PIN-kod o'rnating**. PIN-kodni faqat yurituvchilarga ayting.
Boshqaruv havolasini bilgan odam ham PIN-kodsiz hech narsa o'zgartira olmaydi.

## 5. Kompyuterda ilova kabi
Chrome'da saytni oching → o'ng yuqoridagi ⋮ → **Saqlash va ulashish → Ilova sifatida o'rnatish** (Install page as app).
Ish stolida "ADM JIZZAX AJ" ikonkasi paydo bo'ladi va sayt alohida oynada ochiladi.

## Har kungi ish
1. Boshqaruv → **Natijalar va fayllar** → 630 va 700 fayllarini tashlang → **Tasdiqlash**.
   Sana va tur fayl nomidan aniqlanadi (`630__04.11.2026.xlsx`). Har avtomobil VIN bo'yicha bir marta sanaladi.
2. Boshqaruv → **MQS ma'lumotlari** → MQS faylini tashlang → **Tasdiqlash**.
3. Oy boshida: **Reja va ish grafigi** — oylik reja va ikki sexning ish kunlari.

Birinchi marta yuklashda: agar fayllar o'sha kunniki emas, balki shu kungacha to'plangan ro'yxat bo'lsa,
**"boshlang'ich qoldiq"** belgisini qo'yib yuklang — avtomobillar eslab qolinadi, lekin hech bir kunga sanalmaydi.
Keyingi kunlardan boshlab faqat yangi paydo bo'lgan avtomobillar o'sha kunga yoziladi.

## Kodni yangilash
Yangi `Code.gs` / `index.html` kelganda: Apps Script'da ichini almashtiring → 💾 →
**Deploy → Manage deployments → ✎ → Version: New version → Deploy**. Havola o'zgarmaydi.

## Dizayn yangilanishi (2026-11-06)
- `index.html`: Home Control uslubidagi shisha kartalar, KPI qatori, "Oy davomida" chiziqli grafigi, "Modellar bo'yicha" paneli; asosiy navigatsiya — A variant (yonuvchi kontur).
- `Code.gs`: o'zgarmadi (server funksiyalari avvalgidek).
- `nav-variantlar.html`: to'rt navigatsiya variantining (A, B, C, D) alohida namunasi — brauzerda ochib ko'rish uchun, Apps Script'ga qo'yish shart emas.
- `arxiv/`: o'zgarishdan oldingi `index.html` va `Code.gs` nusxalari. Eskisiga qaytish uchun shu fayllarni Apps Script'ga qo'ying.
