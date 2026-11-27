# Loyha shriftlari

Barcha shriftlar Google Fonts'dan (rasmiy `google/fonts` ombori). Litsenziya: SIL Open Font License 1.1 (har papkada `OFL.txt`). Tijorat videolarida ham bepul ishlatiladi.

| Shrift | Vazifasi | Oʻzbek lotin (ʻ ʼ) | Oʻzbek kirill (ў қ ғ ҳ) |
|---|---|---|---|
| **Inter** | Subtitr va interfeys, eng toza | ✓ | ✓ |
| **Montserrat** | Sarlavhalar | ✓ | ✓ |
| **Onest** | Oʻqilishi oson, toza matn | ✓ | ✓ |
| **Oswald** | Tor va kuchli sarlavha, raqamlar | ✓ | ✓ |
| Unbounded | Katta, keng hook-sarlavhalar | ✓ | ✗ қ ғ ҳ yoʻq |
| Playfair Display | Nafis serif, premium | ✓ | ✗ ҳ yoʻq |
| Rubik | Doʻstona, yumaloq | ✗ ʻ yoʻq | ✗ ҳ yoʻq |
| Manrope | Zamonaviy, yumshoq matn | ✗ ʻ ʼ yoʻq | ✗ қ ғ ҳ yoʻq |
| Space Grotesk | Texno uslub | ✓ | ✗ kirill yoʻq |
| JetBrains Mono | Kod koʻrsatish | ✗ ʻ yoʻq | ✗ қ ғ ҳ yoʻq |

**Qoida:** oʻzbekcha matn uchun avval Inter, Montserrat, Onest yoki Oswald.
- Lotin matnda ʻ belgisi yoʻq shriftda (Rubik, Manrope, JetBrains Mono) ekranda koʻrsatish uchun ʻ oʻrniga ‘ (U+2018) qoʻyiladi. Koʻrinishi bir xil, imlo matnining oʻzi oʻzgarmaydi.
- Kirill matnda harfi yetishmaydigan shriftlarni (Unbounded, Playfair, Rubik, Manrope, Space Grotesk) ishlatmang. Ishlatsangiz, `font-family: 'Unbounded', 'Montserrat'` kabi zaxira shrift bering.

**Ishlatish:**
- HTML video yoki sahifa: `<link rel="stylesheet" href="…/assets/fonts/fonts.css">`, keyin `font-family: 'Inter'`.
- Tizimga oʻrnatish (PIL, PowerPoint/LibreOffice render, ffmpeg): `sh assets/fonts/install.sh`.
- PIL: `ImageFont.truetype('assets/fonts/inter/Inter[opsz,wght].ttf', 64)`, keyin `font.set_variation_by_axes([...])` bilan qalinlik.
