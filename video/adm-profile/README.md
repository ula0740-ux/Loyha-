# ADM Jizzakh — korporativ profil filmi (v3)

- **Fayl:** `ADM_Global_Profile_v3.mp4` — 1920×1080, 30 fps, H.264 + AAC, 4:38 (277,8 s), 83,6 MB, ovoz −16,0 LUFS, true peak −1,9 dBFS. Oldingi versiyalar (`…_v1.mp4`, `…_v2.mp4`) taqqoslash uchun saqlangan.
- **Manba:** `src/ADM_Global_Company_Profile_UZB.pptx` (12 slayd) — yagona faktlar manbai. Uslub uchun namunalar: `src/reference.mp4` (umumiy uslub) va `src/reference_map.mp4` (klaster xaritasi). `src/` papkasi repoga kirmaydi.
- **Ovoz:** ElevenLabs, `eleven_v4` modeli, `language_code: uz`, Sarah ovozi. Matn `prepareUzbek` orqali yuboriladi (x → kh, F varianti), qoʻshni jumlalar kontekst sifatida beriladi va har jumla STT bilan tekshiriladi. Tasdiqlangan baza sozlamalari oʻzgartirilmagan, ovoz tezlashtirilmagan (TEMPO = 1.0).
- **Foydalanuvchining keyingi talablari (2026-11):** slayd emas, original kino dunyosi; hikoya tartibi;
  - bosh sarlavha "ADM JIZZAKH" (v3; v1–v2 da "ADM JIZZAX");
  - furgonlar sahnaning ichkarisidan haydab kelib, fotodagi joyida toʻxtaydi;
  - 3D ustunli maqsadlar grafigi;
  - klaster xaritasi `reference_map` uslubida: kamera har bir sexga uchadi.

## Konsepsiya: slaydlar animatsiyasi emas
PowerPoint faqat **faktlar manbai** sifatida ishlatildi. Slayd renderlari fon qilinmagan, slayd maketlari ham koʻchirilmagan. Film bitta yaxlit, oʻziga xos dunyoda qurilgan:
- **Muhit:** qorongʻi grafit "sanoat" fazosi, diagonal yorugʻlik nurlari, harakatlanuvchi yumshoq nur dogʻi, havodagi zarrachalar, plyonka donasi va vinyetka.
- **Materiallar:** shisha va qorongʻi glass panellar.
- **Rang urgʻusi:** bitta, ADM logosidagi apelsin rang (#E97132).
- **Shriftlar:** Montserrat (sarlavhalar), Oswald (raqamlar), Inter (matn).

Manba fotolari (zavod, DOST avtomobili, furgonlar, R&D binosi, havodan olingan sxema, xaritalar, avtomobil kesmalari) shu dunyoga **3D qatlam** sifatida joylandi. Ular suzib turuvchi plitalar boʻlib, chuqurlik, aks, nur va kamera harakati bilan ishlaydi. Furgonlar fotodan kesib olindi, fon esa slayd interfeysisiz qayta tozalandi.

Foydalanuvchi talabi bilan ikki namunaning **effektlari va koʻrinishi yaqindan takrorlandi**, faqat oʻz kontentimiz bilan. Logolar, kadrlar va musiqa koʻchirilmadi.
- **`reference.mp4`dan:**
  - grafit fon va unda suzuvchi yumshoq nur dogʻi;
  - har bir akt boshida qorongʻi parda va nur ustida ingichka (Inter 200) soʻzning harfma-harf xira holatdan ochilishi, keyin xiralashib kattalashib ketishi ("Rivojlanish", "Koʻlam", "Natijalar", "Klaster", "Milliy brend", "Innovatsiya", "Lokalizatsiya", "Logistika", "Maqsadlar", "Ekotizim");
  - devorlari "ekranlar" bilan qoplangan 3D tunnel va unda kameraning chuqurlikka uchishi (ekranlarda filmning oʻz fotolari);
  - egilib koʻtariladigan shisha panel;
  - kamera yonidan uchib oʻtadigan ekranlar;
  - foiz sanaydigan yaltiroq shisha trubka;
  - oxirida oq chaqnash va oq kartada logo;
  - neytral grafit rang grade.
- **`reference_map.mp4`dan:**
  - qorongʻi fazoda qiyalangan 3D plita;
  - kameraning har bir maydonga uchib yaqinlashishi va qaytib uzoqlashishi;
  - maydon ustida yorugʻ hajm (light pillar) koʻtarilishi va toʻlqinlanuvchi halqa;
  - yon tomonda maʼlumot paneli;
  - oxirida umumiy koʻrinish va yorliqlar.

**Hikoya tartibi** slayd tartibi emas: kimmiz → qayerdan keldik → bugungi koʻlam → bozordagi oʻrnimiz → ishlab chiqarish yuragi (klaster) → milliy brend DOST → innovatsiya (R&D) → portfel → qamrov (lokalizatsiya, logistika) → 2035 maqsadlari → ekotizim → yakun.

Statistikalar koʻrsatilayotganda ekrandagi har bir tasvir harakatda boʻladi: parallaks, kameraning oldinga siljishi, orbita boʻylab aylanish, nur va zarrachalar. Sonlar diktor ularni aytayotgan soʻzda sanagich bilan ochiladi.

## Storyboard (yakuniy vaqtlar)

| Vaqt | Slayd | Maʼlumot | Vizual / 3D / kamera / oʻtish / effekt | Ekrandagi matn |
|---|---|---|---|---|
| 0:00–0:10 | 1 | Kim: koʻp brendli ishlab chiqaruvchi | Qorongʻi fazo, nur dogʻi, letterbox ochiladi; logo chiqadi, sarlavha harfma-harf xira holatdan ochiladi; zavod fotosi suzuvchi 3D plita boʻlib pastdan koʻtariladi va egilishdan tekislanadi; ustidan nur oʻtadi, flare bor | ADM JIZZAX · MULTI BREND AVTOMOBIL ISHLAB CHIQARUVCHI |
| 0:10–0:58 | 2 | Tarix: 6 bosqich, har yil alohida aytiladi | "Rivojlanish" soʻzi ochiladi; devorlari foto-ekranlar bilan qoplangan 3D tunnel: kamera chuqurlikka uchadi; har bir yil kartochkasi oʻz jumlasi aytilayotgan butun vaqt davomida markazda turadi, kamera faqat pauzalarda keyingisiga uchadi; oxirgi kartochka (2026) markazda; apelsin rang ramka halqalari (push oʻtish) | 2014 … Aprel 2026, slayddagi matnlar bilan |
| 0:58–1:04 | 2 | Tuzilma | Egilgan shisha panel, 33 va 5 900 sanagichlari, 4 tugun | KOMPANIYA TUZILMASI va 4 boʻgʻin izohlari |
| 1:04–1:19 | 2 | Savdo va ulush | Shisha progress-trubka 0,5% dan 11% gacha toʻladi, yillar belgilari, sotuv sanagichi, prognoz chiplari | 2017 0,5% / 650 … 2025 11% / 46 439; 2030 PROG. 30% · 130 000; 2035 PROG. 35% · 210 000 |
| 1:19–1:31 | 3 | Koʻrsatkichlar | $1 024 mln sanagichi; 5 kartochka 3D da kirib keladi, №2 belgilanadi (whip oʻtish) | BIRINCHI, №2, TOP-10, YETAKCHI ×2 |
| 1:31–1:38 | 3 | Brendlar, DOST | DOST avtomobili fotosi suzuvchi plita boʻlib turadi; dolly, orbita, nur va flare | JORIY BRENDLAR roʻyxati · MARKAZIY OSIYODAGI BIRINCHI MILLIY AVTOMOBIL BRENDI |
| 1:38–2:58 | 5 | Klaster: 7 sex | Chaqnash va impact bilan kirish. Havodan olingan sxema qorongʻi fazoda 3D plita. Kamera navbat bilan uchadi: KIA CKD → SKD → Lokalizatsiya klasteri → Shtamplash sexi → CKD NEV → R&D → DOST CKD. Har sexda bino yorugʻ hajm boʻlib koʻtariladi, halqa toʻlqinlanadi, xarita xiralashadi, panel va yetakchi chiziq chiqadi. Oxirida umumiy koʻrinish: 7 yorliq va model paneli | Har panelda yillar, nomi, investitsiya va ish oʻrni (slayd 5). SKD panelida "DASTLAB · SKD SEXI 250 nafar xodim". CKD loyihalari 100 000 (yiliga) (ICE + NEV); modellar 2024–2030 |
| 2:58–3:19 | 9 | DOST tijorat transporti | Ikki furgon tozalangan fon plitasida chuqurlikdan haydab keladi: uzoqda kichik va xira, faralari yongan; fotodagi joyida toʻxtaydi, ostida soya va pol aksi bor. Keyin 3 tur ham chuqurlikdan haydab kelib qatorga turadi | JIZZAX COMMERCIAL VEHICLE; 30 mln $, Yiliga 30 ming, 30 %, 1200, I chorak 2027, III chorak 2028; 3 tur nomi |
| 3:19–3:34 | 10–11 | R&D | R&D binosi 3D ramkada (dolly va nur); 4 bosqich kartochkasi, maqsadlar narratsiya bilan yonadi. Keyin ESKIZ → RENDER → CAD-CHIZMA → PROTOTIP rasmlari kamera yonidan uchib oʻtadi (flash oʻtish) | slayd 10/11 matnlari |
| 3:34–3:38 | 8 | Segmentlar | Avtomobil kesmalari 3D cover-flow qatorida oʻtadi (ovozsiz koʻprik sahna) | ISHTIROK SEGMENTLARI; model nomlari va segmentlar |
| 3:38–3:50 | 6 | Lokalizatsiya geografiyasi | Manbadagi 3D xarita qiyalanib aylanadi; pinlar narratsiya bilan birga koʻtariladi | 7 nom; JAMI ISH OʻRINLARI: 5900 |
| 3:50–4:00 | 7 | Logistika | Manbadagi rangli 3D xarita qiyalanib aylanadi; Jizzaxdan hududlarga harakatlanuvchi yoy chiziqlar | MARKAZLASHGAN LOGISTIKA; 14 hudud; slayd 7 dagi ikki izoh |
| 4:00–4:12 | 4 | 2035 maqsadlari | Oʻz dunyosidagi fon (slayd foni emas). Jadval qatorlari birma-bir sanagich bilan ochiladi. 3 ta 3D ustun navbat bilan koʻtariladi (nisbat 0,53 : 0,70 : 1), polda aks va nur bor, kamera orbita boʻylab aylanadi, strelka yuqoriga chiziladi | 2026-2035 MAQSADLARI: 7 qator |
| 4:12–4:24 | 12 | Ekotizim | Oʻz dunyosidagi fon. 4 shisha ustun 3D da koʻtariladi, xizmat chiplari | ADM ekotizimi … toʻrtta biznes yoʻnalishini birlashtiradi; 4 yoʻnalish; 11 ta xizmat |
| 4:24–4:38 | 10 | Yakun | Logo (ADM / JIZZAKH), "ADM JIZZAKH", shior; oq chaqnash musiqaning yakuniy urgʻusida; oq chaqnash, oq kartada logo; letterbox yopiladi, qorongʻilashadi | Innovatsiyalar orqali kelajak mobilligi uchun yechimlar yaratamiz |

## Sahnalar boʻyicha vizual promptlar (literal / abstrakt)
Har bir prompt kodda bajarilgan; generativ AI tasvirlari ishlatilmagan.

| Sahna | Prompt | Turi |
|---|---|---|
| title | "Grafit fazo, chapdan oʻngga suzuvchi yumshoq oq nur dogʻi; zavod fotosi suzuvchi plita boʻlib egilishdan tekislanadi, ustidan iliq nur oʻtadi" | foto **literal** (manba), muhit **abstrakt** |
| hist | "Apelsin ramka halqalaridan iborat qorongʻi tunnel, ichida shisha kartochkalar; kamera ular orasidan uchadi" | **abstrakt** |
| struct / sales | "Egilgan shisha panel, katta raqamlar; yaltiroq apelsin suyuqlik bilan toʻladigan shisha trubka" | **abstrakt** grafika, raqamlar literal |
| kpi | "Shisha kartochkalar kaskadi; DOST avtomobili fotosi plita boʻlib turadi, nur va flare bilan" | foto **literal** |
| cluster | "Havodan olingan haqiqiy sxema qorongʻi fazoda 3D plita; har bir sex oʻrnida apelsin rang yorugʻ hajm koʻtariladi" | sxema **literal**. Hajmlar sxemadagi binolarni ajratib koʻrsatadigan **abstrakt** belgilar, haqiqiy balandlik emas |
| dost | "Fotodagi ikki furgon showroom chuqurligidan haydab kelib, fotodagi aniq joyida toʻxtaydi" | **literal** (fotoning oʻzi). Harakat illyustrativ, furgonlar koʻrinishi oʻzgartirilmagan |
| rnd | "R&D binosi fotosi 3D ramkada; dizayn bosqichlari rasmlari kamera yonidan uchadi" | **literal** |
| seg | "Avtomobil kesmalari cover-flow qatori" | **literal** |
| geo / logi | "Manbadagi 3D xaritalar qiyalanib aylanadi; pinlar, yoylar" | **literal** xarita (slayd tasviri). Yoylar **abstrakt** (yoʻnalishni bildiradi, aniq marshrut emas) |
| goals | "Uchta yorugʻ apelsin 3D ustun navbat bilan koʻtariladi, ustidan strelka" | **abstrakt** illyustratsiya: haqiqiy raqamlar faqat jadvalda. Ustunlar soni, nisbati va rangi slayd rasmidagidek |
| eco | "Toʻrtta shisha ustun, xizmat chiplari" | **abstrakt** |
| outro | "Logo kartasi, oq chaqnash" | — |

### Xarita va binolar aniqligi haqida
- **Klaster:** asos slayd 5 dagi havodan olingan haqiqiy rasm, faqat kesib olingan va 2× kattalashtirilgan. Har bir sexning joyi slayddagi callout chizigʻi tugaydigan nuqtadan olindi. Atrofidagi bino chegarasi fotoga qarab qoʻlda belgilandi. Yorugʻ hajmlar belgi xolos: bino balandligini anglatmaydi.
- **Geografiya (slayd 6) va logistika (slayd 7):** manbadagi xarita tasvirlarining oʻzi ishlatildi. Pinlar va hudud yorliqlari slayddagi oʻrinlarida.
  - Andijon va Fargʻona pinlari slayddagi chiziqlar boʻyicha joylangan, geografik jihatdan teskari koʻrinadi.
  - Logistika yoylari aniq marshrut emas, yoʻnalish belgisi.
- **Yangi landshaft yoki bino qoʻshilmagan.**

## Narratsiya (sahnalar boʻyicha) va talaffuz izohlari

| Sahna | Matn (yozma shakl; TTS ga `prepareUzbek` orqali boradi) |
|---|---|
| title | ADM Jizzax, koʻp brendli avtomobil ishlab chiqaruvchi kompaniya. |
| hist1 | Kompaniyaga 2014-yilda asos solingan. |
| h2020 | 2020-yilda ADM Jizzax avtozavodi qurilishi boshlandi. Birinchi bosqich SKD boʻldi. |
| h2021 | 2021-yil martda mijozlarga ilk avtomobillar yetkazildi. |
| h2022 | 2022-yil oktabrda Chery avtomobillarini SKD texnologiyasida, yaʼni yirik uzellardan yigʻish boshlandi. |
| h2024 | 2024-yil martda CKD texnologiyasida Kia Sonet yigʻish boshlandi. |
| h2026 | 2026-yil aprelda esa Kia K3 uchun yangi CKD ishlab chiqarish liniyasi ishga tushirildi. |
| struct | Guruh tarkibida 33 ta kompaniya va 5 900 nafar xodim bor. |
| sales | 2017-yilda bozor ulushi 0,5 foiz edi. 2025-yilga kelib ulush 11 foizga, sotuv esa 46 439 taga yetdi. |
| kpi | 2025-yilda yillik aylanma 1 024 million dollarni tashkil etdi. Kompaniya avtomobil sotuvi hajmi boʻyicha ikkinchi oʻrinda. |
| brands | DOST esa Markaziy Osiyodagi birinchi milliy avtomobil brendi. |
| cl0 | Endi ADM Jizzax avtomobil klasteriga nazar tashlaymiz. |
| c_kia | Kia CKD loyihasi: investitsiya 242 million dollar, 2 700 ish oʻrni. |
| c_skd | SKD sexi: investitsiya 12,6 million dollar, 450 ish oʻrni. **Zavod faoliyatini dastlab aynan shu SKD sexida 250 nafar xodim bilan boshlagan.** |
| c_lok | Lokalizatsiya klasteri: investitsiya 150 million dollar, 350 ish oʻrni. |
| c_sht | Shtamplash sexi: investitsiya 55 million dollar, 150 ish oʻrni. |
| c_nev | Yangi loyihalar. CKD, {"New energy vehicle"}, investitsiya 100 million dollar, 1 200 ish oʻrni. (`{…}` qismi inglizcha oʻqiladi) |
| c_rd | Ilmiy-tadqiqot markazi: investitsiya 100 million dollar, 500 muhandis. |
| c_dost | DOST tijorat avtomobillari: investitsiya 30 million dollar, 1 200 ish oʻrni. |
| cl4 | CKD loyihalari yiliga 100 000 avtomobilga moʻljallangan. |
| geo | Lokalizatsiya loyihalari Jizzax, Toshkent, Fargʻona, Andijon, Nukus va Xorazmda, shuningdek Qozogʻistonda joylashgan. |
| logi | United Auto Alliance KD toʻplamlar va tayyor mahsulotni Jizzaxdan har bir hududga yetkazadi. |
| dost1 | Jizzax tijorat transporti loyihasida DOST milliy brendi ostida mikroavtobus, bortli yuk mashinasi va furgon ishlab chiqariladi. |
| dost2 | Investitsiya 30 million dollar, 1 200 ish oʻrni. SKD starti 2027-yilning birinchi choragida. |
| rnd | Tadqiqot va ishlanmalar markazining maqsadi: texnologik mustaqillik, DOST brendi ostida yangi modellar va jahon bozoriga chiqish. |
| goals | 2027-yildan 2035-yilgacha qoʻshimcha 400 million dollar investitsiya va 5 000 ta yangi ish oʻrni koʻzda tutilgan. |
| eco | ADM ekotizimi toʻrt yoʻnalishni birlashtiradi: avtomobil ishlab chiqarish, savdo, sotuvdan keyingi xizmat va yangi mobillik. |
| outro | ADM Jizzax: innovatsiyalar orqali kelajak mobilligi uchun yechimlar yaratamiz. |

**Talaffuz (v2, foydalanuvchi quloq bilan tanlagan, 2026-11-24):**
- **CKD → "Si-Ke-Di"**. Lugʻatda `abbr`, approved. Sinalgan variantlar: Si-Ka-De, Si-Ke-Di, Se-Ka-De, Si-Kay-Di.
- **SKD → "Es-Ki-Di"**. Lugʻatda `abbr`, approved.
- **KD → "Ke-Di"** (CKD ga moslab). Avvalgi "Ka-de" yozuvi almashtirildi.
- **"sex"** ning barcha shakllari (sexi, sexida …) ovozga **"tsekh…"** boʻlib boradi ("Si-Ke-Di tsekhida"). Bu harflarni oʻzgartiradi, shuning uchun lugʻatga yozilmadi (`sameLetters` qoidasi). Almashtirish faqat shu filmning `narrate.mts` skriptida, `tsekh()` funksiyasida bajariladi, kontekst jumlalarida ham. Yozma matn, ekrandagi yozuvlar va STT etaloni "sex" boʻlib qoladi.
- **ADM →** lugʻatdagi "A-de-em," (1-variant, tasdiqlangan baza). v1 da notoʻgʻri eshitilgan "ADM ekotizimi …" jumlasi qayta yozildi; STT endi "ADM ekotizimi" deb eshitadi.
- Namunalar `audio/variants/` papkasida (`CKD_*`, `SKD_*`, `ADM_*`, `*_variantlar.mp3`). Skript: `build/variants.mts`.
- **CKD NEV → "Si-Ke-Di, New energy vehicle"**. "New energy vehicle" foydalanuvchining aniq tanlovi bilan **inglizcha** oʻqiladi. Narratsiyada `{"New energy vehicle"}` shaklida yoziladi va `prepareUzbek` dan oʻtmaydi. Ekrandagi kartochkada slayddagidek "CKD NEV" qoladi.
  - 4 ta variant sinaldi: `audio/variants5/CKD_NEV_variantlar.mp3`, skript `build/variants_nev.mts`.
  - Filmda 2-variant ishlatildi: qoʻshtirnoq va vergullar bilan, bitta jumla. STT (uz va en) "CKD New Energy Vehicle" deb eshitdi.
  - Uch boʻlakdan ulangan 3-variantda inglizcha STT "CKG" deb eshitdi.
  - Lugʻatdagi `NEV → En-e-ve` yozuvi bu filmda endi ishlatilmaydi.
- **Jizzax** ovozga "Jizzakh" boʻlib boradi, yozuvda x saqlanadi.
- **R&D** narratsiyada "ilmiy-tadqiqot markazi" va "tadqiqot va ishlanmalar markazi" deb aytiladi.
- Sonlar soʻz bilan oʻqiladi: 100–199 oraligʻi "yuz …", "12,6" esa "oʻn ikki butun oʻndan olti".
- **STT:** har jumla tekshirildi, natija 92,9–100%. Yakuniy natijalar `audio/stt_report.json` da.
  - `cl4` (92,9%) da STT "CKD"ni "sekedi" deb yozadi, bu qisqartmaning harf nomi bilan oʻqilishidan.
  - Yakuniy baho foydalanuvchi qulogʻida.
- **Temp:** 219,1 s ovoz ichida 317 ta yozma soʻz, oʻrtacha 1,45 soʻz/s, eng tez jumla 1,94 soʻz/s (talab ≤ 2,3).

## v2 da tuzatilganlar (foydalanuvchi talabi va oʻz tekshiruvim)
1. **Talaffuz:** CKD, SKD, KD, "sex" va ADM yuqoridagidek. Bu soʻzlar bor barcha jumlalar qayta yozildi: tarix, c_kia, c_skd, c_sht, c_nev, cl4, logi, dost2, eco.
2. **Tarix:**
   - 2020, 2021 va 2022-yillar har biri alohida, toʻliq aytiladi.
   - 2024-yil uchun yigʻila boshlagan model aytiladi: slayd 2 dagi "CKD texnologiyasida yigʻish boshlandi (Kia Sonet)" asosida.
   - Har kartochka oʻz jumlasi davomida ekranda turadi; v1 da 2021 va 2022 bir zumda oʻtib ketardi.
   - Kartochkalar endi kadr chetidan chiqib ketmaydi, oxirgisi markazda.
3. **Sanagichlar:**
   - Klaster panellari va $1 024 mln sanagichi aytilishidan oldin "0" ni koʻrsatmaydi: raqam xira turadi va aytilgan soʻzda sanay boshlaydi.
   - Barcha sanagichlar 0,6–0,7 s ichida aniq yakuniy qiymatga yetadi va kamera ketguncha shu qiymatda turadi. v1 da CKD NEV kartochkasida "99 mln $" va "0 ish oʻrni" koʻrinib qolgan edi. Raqam soʻzlari endi matn boʻyicha topiladi (`WI()`), shuning uchun qayta yozilgan jumlalarda sinxron buzilmaydi.
4. **Oʻtishlar:** klaster va R&D ga kirishdagi kulrang "flash", akt soʻzining qorongʻi pardasi bilan ustma-ust tushib qolardi; bu yerlarda yumshoq oʻtishga almashtirildi (impact SFX qoldi).
5. **Musiqa:** film uzaygani uchun trek ortiqcha sekinlashtirilmaydi. Tezlik koʻpi bilan ×0,95; qolgan qism trek tanasini 3 soniyalik crossfade bilan takrorlash orqali toʻldiriladi.
6. **Tunnel kamerasi:** v1 dagi 17,9 s dagi bir kadrlik sakrash (kalitlar tartibi xatosi) toʻliq tuzatildi.
7. **SKD jumlasi** ("dastlab aynan shu SKD sexida 250 nafar xodim bilan boshlagan") saqlandi.

## v3 da tuzatilganlar
1. **Logo:** "GLOBAL" oʻrniga "JIZZAKH" (vektor va jonli matn, aniq tasvir). Ochilish, yakun va oq logo kartasida.
2. **Yozuv:** ekrandagi barcha "JIZZAX" yozuvlari endi "JIZZAKH".
3. **Musiqa:** ElevenLabs treki oʻrniga foydalanuvchining treki. Takt chiziqlarida aranjirovka qilingan, tempo oʻzgartirilmagan, ovoz ostida ducking bor.
4. **Montaj musiqaga moslandi:** sahnalar taktga tushadi, klaster choʻqqiga, chaqnash yakuniy urgʻuga.
5. **Oʻrinbosar qiymatlar:** hech qayerda notoʻgʻri oraliq qiymat koʻrinmaydi. Raqam aytilguncha joyi boʻsh turadi va aytilgan soʻzda 0,6–0,7 s ichida sanab yakuniy qiymatda toʻxtaydi. Bu klaster panellariga (investitsiya, ish oʻrni, 250 nishoni), $1 024 mln, 33 / 5 900 va maqsadlar jadvalining +400 / +5 000 qatorlariga tegishli.

## Musiqa va SFX
- **Musiqa (v3):** foydalanuvchining treki: **AShamaluev Music — "Epic Motivational Music"** (`src/music_user.m4a`, 200 s). Fayl repoga kiritilmaydi; litsenziya va ishlatish huquqi foydalanuvchida.
  - **Tahlil** (`build/music_analyze.py`, librosa): 99,4 BPM, takt (bar) 2,40 s, 80 ta takt.
  - **Energiya xaritasi:** kirish 0–21 s, A boʻlimi 40–76 s, pasayish 81–97 s, choʻqqi 97,8–155 s, yakuniy urgʻu 174,6 s.
  - **Aranjirovka** (`timeline.json` → `music`), tempo oʻzgartirilmagan:
    1. trek boshidan 71-taktgacha uzluksiz. Klaster fly-over aynan choʻqqining kirish taktida (40-takt) boshlanadi;
    2. keyin A boʻlimidan (16-takt) takrorlanadi, pasayish orqali yana choʻqqiga chiqib, maqsadlar, ekotizim va yakun ostida yangraydi;
    3. trekning yakuniy urgʻusi (72-takt) oq chaqnashga toʻgʻri keladi.
    - Ulanishlar takt chizigʻida, 0,3 s equal-power crossfade bilan.
  - **Montaj musiqaga mos:** sahna boshlanishlari takt chiziqlariga (bar downbeat) suriladi, jumlalar yaqin boʻlsa keyingi beat dan keyin boshlanadi, oq chaqnash yakuniy urgʻuda. Ovozlar qayta yozilmadi, faqat pauzalar surildi.
  - **Ducking:** diktor gapirayotganda musiqa −11 dB ga tushadi (attack 0,15 s, release 0,3 s). Pauzalar, kirish va yakunda toʻliq balandlikda.
- **SFX:** `audio/sfx/*.mp3`, ElevenLabs Sound Effects API: whoosh, impact, tick, pop, rise, chime, car. Har biri kadrdagi hodisaga oʻz choʻqqisi boʻyicha joylanadi:
  - whip va boshqa oʻtishlar;
  - klasterga kirishdagi impact;
  - har sexga uchish va panel chiqishi;
  - jadval qatorlari;
  - furgonlarning kirib kelishi;
  - logo kartasidagi chime.
- **Mix:** `audio.py`, ikki bosqichli loudnorm. Mixkit, Freesound va Pixabay bu muhitning tarmogʻidan ochilmadi, shuning uchun musiqa va SFX ElevenLabs orqali olindi. Oldin `video/hrm-edolus` da ham shunday qilingan.

## Fakt-tekshiruv (har raqam va daʼvo → slayd)

| Raqam / daʼvo | Slayd |
|---|---|
| MULTI BREND AVTOMOBIL ISHLAB CHIQARUVCHI | 1 |
| 2014 asos solindi; 2020 ADM JIZZAKH avtozavodi qurilishi (1-bosqich — SKD); Mart 2021 ilk avtomobillar; Oktabr 2022 Chery SKD (yirik uzellardan); Mart 2024 CKD (Kia Sonet); Aprel 2026 yangi CKD ishlab chiqarish liniyasi (Kia K3). Barchasi narratsiyada ham aytiladi | 2 |
| 33 kompaniya, 5 900 xodim; ADM Jizzakh, Fincom, Diler tarmogʻi (3S, 2S), 124 ta dilerlik markazi, United Auto Alliance va ularning izohlari | 2 |
| Bozor ulushi va sotuv: 2017 0,5% / 650; 2020 1,6% / 4 604; 2022 2,8% / 8 198; 2024 7,5% / 30 349; 2025 11% / 46 439; 2030 prog. 30% / 130 000; 2035 prog. 35% / 210 000 | 2 |
| $1 024 mln (2025-yildagi yillik aylanma); №2 sotuv hajmi; TOP-10 soliq toʻlovchilar; BIRINCHI xususiy koʻp brendli; YETAKCHI ×2 | 3 |
| Joriy brendlar KIA, CHERY, GWM, HYUNDAI TRUCK & BUS, CHANGAN (logolar matn bilan); DOST — Markaziy Osiyodagi birinchi milliy avtomobil brendi | 3 |
| KIA CKD 2021-2026, 242 mln $, 2700; SKD 2020-2021, 12,6 mln $, 450; Lokalizatsiya klasteri 2022-2027, 150 mln $, 350; Shtamplash sexi 2024-2026, 55 mln $, 150; CKD NEV 2026-2028, 100 mln $, 1200; R&D 2026-2030, 100 mln $, 500 muhandis; DOST CKD 2026-2030, Tijorat avtomobillari, 30 mln $, 1200; CKD loyihalari 100 000 avtomobil (yiliga) (ICE + NEV); modellar Sonet 2024 … Sonet 2 2030 | 5 |
| "250 nafar xodim bilan SKD sexida boshlagan" | **foydalanuvchi bergan fakt** (slaydda yoʻq). Slayddagi 450 ish oʻrni ham saqlangan |
| Lokalizatsiya geografiyasi: Jizzax, Toshkent, Fargʻona, Andijon, Nukus, Xorazm, Qozogʻiston; JAMI ISH OʻRINLARI: 5900 | 6 |
| Markazlashgan logistika, 14 ta hudud nomi, ikki izoh | 7 |
| Ishtirok segmentlari va model nomlari | 8 |
| DOST: 30 mln $, yiliga 30 ming, 30 %, 1200, I chorak 2027 SKD, III chorak 2028 CKD; 3 tur | 9 |
| R&D bosqichlari (2026-2027, 2028, 2030, 2032 · 2035), maqsadlar, shior | 10 |
| R&D yutuqlari: ESKIZ → RENDER → CAD-CHIZMA → PROTOTIP (DOST) | 11 |
| 2026-2035 maqsadlari: jadvalning 7 qatori × 2 ustuni | 4 |
| Ekotizim: 4 yoʻnalish, xizmatlar | 12 |

## Qarama-qarshi yoki noaniq joylar (taxmin qilinmadi)
1. **Lokalizatsiya klasteri:** slayd 5 da 150 mln $, slayd 6 da $112 mln. Ish oʻrni ikkalasida 350. Filmda slayd 5 raqami ishlatildi.
2. **Shtamplash sexi / ADM Stamping:** slayd 5 da 55 mln $, slayd 6 da $59 mln. Ish oʻrni ikkalasida 150. Filmda slayd 5 raqami.
3. **DOST:** slayd 5 va 9 da 30 mln $ va 1200 ish oʻrni, slayd 6 da $62 mln va 1 000 ish oʻrni. Filmda slayd 5 va 9 raqamlari.
4. **R&D investitsiyasi:** slayd 5 da 100 mln $ (2026-2030), slayd 10 da "USD 250M" (rasm ichida). Filmda faqat slayd 5 raqami bor.
5. **Nukus Component va Adm Cable:** ikkalasida bir xil "$85,9 mln, 209 ish oʻrni" turibdi. Nusxa koʻchirishdagi xato boʻlishi mumkin. Filmda koʻrsatilmadi.
6. **Distribyutor brendlari:**
   - slayd 2: Kia, Chery, Haval, Hyundai Truck, Changan, Tank;
   - slayd 3: KIA, CHERY, GWM, HYUNDAI, CHANGAN.
   - Narratsiyada brendlar sanab oʻtilmaydi. Ekranda faqat koʻrsatilayotgan slayd 3 roʻyxati turibdi.
7. **6-slayddagi pinlar:** Andijon va Fargʻona pinlari slayddagi chiziqlar boʻyicha joylashtirildi. Geografik jihatdan ular teskari koʻrinadi. Filmda slayddagidek qoldirildi.
8. **Sarlavha:** foydalanuvchi talabi bilan ekrandagi barcha "JIZZAX" yozuvlari "JIZZAKH" qilindi: sarlavha, yakun kartasi, "JIZZAKH COMMERCIAL VEHICLE", pin va hudud yorligʻi. Slayd 1 da "ADM GLOBAL", slayd 6/7 da "JIZZAX" yozilgan. Narratsiya matnida "Jizzax" qoldi, ovozda baribir "Jizzakh" eshitiladi.
   - Slayd 2 dagi tuzilma sarlavhasi ("ADM Global") va slayd 6 nomi ("ADM GLOBAL LOKALIZATSIYA …") slayd iqtibosi sifatida oʻzgarmagan.
   - Logotip: ADM belgisi va harflari pptx dagi vektor SVG dan olindi. Ostidagi kichik "GLOBAL" soʻzi oʻsha joy, eni, rangi va harf balandligida jonli matn "JIZZAKH" bilan almashtirildi (`assets/adm_logo_jizzakh.svg`, sahifaga inline, Montserrat).
9. **Ochilgan qisqartmalar:** ICE + NEV ekranda slayddagidek. KIA CKD 2021-2026 investitsiya davri, CKD yigʻish esa slayd 2 boʻyicha 2024-yil martda boshlangan; bu ikki xil sana maʼnosi boʻlishi mumkin.

## Build
```sh
cd video/adm-profile
python3 -I build/prep_assets.py src/ADM_Global_Company_Profile_UZB.pptx assets   # rasmlar (pptx faqat oʻqiladi)
python3 -I build/cut_vans.py assets                                               # furgonlar kesmasi + toza fon (GrabCut)
(cd ../../studio && ELEVENLABS_API_KEY=... ATTEMPTS=3 npx tsx ../video/adm-profile/narrate.mts)   # ONLY=id1,id2 — faqat shular
python3 timeline.py && python3 audio.py
python3 build/render.py out/v2_master.mp4 --fps 30 --sub 1 --chunks 4                # 4 ta parallel boʻlak (JPEG skrinshot, render_short.py bilan bir xil seek(t) shartnomasi)
ffmpeg -i out/final_v.mp4 -i out/audio.wav -c:v libx264 -b:v 2700k -pass 1/2 … ADM_Global_Profile_v2.mp4
python3 build/still.py out/st 80 120 …                                            # QA kadrlari
```
