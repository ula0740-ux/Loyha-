# VoiceStudio — ElevenLabs o'rniga

**Nima qiladi:** matnni ovozga aylantiradi, ovozni klonlaydi (bir necha soniyalik yozuvdan), yangi ovoz yaratadi, videoni boshqa tilga dublyaj qiladi, gapni matnga aylantiradi.
**Asosiy farqi:** hammasi kompyuterning o'zida ishlaydi. Model yuklab olingach, internet kerak emas va ovozingiz hech qayerga yuborilmaydi.
**Litsenziya:** dastur — AGPL-3.0 (bepul, ochiq kod). Modellarning litsenziyasi alohida (pastda o'qing).
**Eslatma:** loyihaning eski nomi **OmniVoice Studio**. Ba'zi joylarda shu nom uchraydi — bu o'sha dastur.

## Rasmiy havolalar

| Nima | Havola |
|---|---|
| GitHub sahifasi | https://github.com/debpalash/VoiceStudio |
| Yuklab olish (eng yangi versiya) | https://github.com/debpalash/VoiceStudio/releases/latest |
| Rasmiy sayt | https://voicestudio.sh |
| O'rnatish qo'llanmalari | https://github.com/debpalash/VoiceStudio/tree/main/docs/install |
| Muammolar va yechimlar | https://github.com/debpalash/VoiceStudio/blob/main/docs/install/troubleshooting.md |

## Talablar — o'rnatishdan oldin albatta tekshiring

| Kompyuter | Holat |
|---|---|
| Mac, Apple Silicon (M1–M4), macOS 13.3 yoki yangi | ✅ To'liq ishlaydi |
| Mac, Intel protsessor | ⚠️ Faqat interfeys ochiladi, ovoz yaratilmaydi |
| Windows 10 / 11, 64-bit | ✅ Ishlaydi. NVIDIA videokarta bo'lsa tezroq |
| Linux, 64-bit | ✅ Ishlaydi |
| Videokarta yo'q | Ishlaydi, lekin sekinroq |
| Android 10+ / iPhone (iOS 17+) | 🧪 Sinov versiyasi (Preview) |

Modellar bir necha GB oladi. Kamida 10 GB bo'sh joy bo'lsin.

---

## O'rnatish — Mac (Apple Silicon)

**Eng oson yo'l — DMG fayl:**
1. https://github.com/debpalash/VoiceStudio/releases/latest sahifasini oching.
2. **Assets** qismidan `.dmg` faylni yuklab oling.
3. Uni oching va VoiceStudio belgisini **Applications** papkasiga torting.

**Bitta buyruq bilan** — Terminal'ni oching (Spotlight'da "Terminal" deb qidiring) va yozing:
```bash
curl -fsSL https://voicestudio.sh/install | sh
```

**Homebrew orqali** (Homebrew o'rnatilgan bo'lsa):
```bash
brew tap debpalash/tap
brew trust --cask debpalash/tap/voicestudio
brew install --cask debpalash/tap/voicestudio
```

## O'rnatish — Windows

**Eng oson yo'l — EXE fayl:**
1. https://github.com/debpalash/VoiceStudio/releases/latest sahifasini oching.
2. **Assets** qismidan `.exe` faylni yuklab oling va ishga tushiring.
3. "Windows protected your PC" chiqsa: **More info** → **Run anyway**.

**Bitta buyruq bilan** — **PowerShell**'ni oching (Start menyusida "PowerShell" deb qidiring) va yozing:
```powershell
irm https://voicestudio.sh/install.ps1 | iex
```

## O'rnatish — Linux

```bash
curl -fsSL https://voicestudio.sh/install | sh
```
Yoki tizimingizga mos yo'l:
- **Ubuntu / Debian / Mint:** Releases'dan `.deb` ni yuklab olib: `sudo apt install ./VoiceStudio-*-linux-x64.deb`
- **Snap:** `sudo snap install voicestudio`, so'ng mikrofon uchun: `sudo snap connect voicestudio:audio-record`
- **Arch / Manjaro:** `yay -S voicestudio-bin`
- **AppImage:** `chmod +x VoiceStudio-*-linux-x64.AppImage`, keyin `./VoiceStudio-*-linux-x64.AppImage`

---

## Birinchi marta ishlatish

1. VoiceStudio'ni oching.
2. **Voice cloning** ("Ovozni klonlash") bo'limiga kiring.
3. Tayyor ovozni tanlang yoki o'z ovozingizni qo'shing: shovqinsiz joyda yozilgan toza, qisqa yozuv bo'lsin.
4. Matnni yozing, tilni tanlang va **Generate** ("Yaratish") tugmasini bosing.
5. Dastur model yuklab olishdan oldin ruxsat so'raydi. Rozi bo'ling va yuklab olish tugashini kuting (bir necha GB).

## Halol ma'lumot

- Dastur 646 tilni qo'llab-quvvatlashini aytadi, lekin har bir til uchun sifat ro'yxati yo'q. **O'zbek tilini o'zingiz sinab ko'ring.**
- **Tijorat uchun diqqat:** standart OmniVoice modelining litsenziyasi — **CC-BY-NC**, ya'ni **faqat notijorat** foydalanish uchun. Ovozni pulli ishda (reklama, mijoz uchun) ishlatmoqchi bo'lsangiz, dastur ichidagi **Model Manager**'da boshqa model va uning litsenziyasini tekshiring.
- Birovning ovozini uning roziligisiz klonlamang.

## Muammo chiqsa

- **Intel Mac'da ovoz yaratilmayapti** → bu cheklov, xato emas. Apple Silicon Mac yoki Windows/Linux kompyuter kerak.
- **Juda sekin** → videokarta yo'q bo'lsa bu normal holat. Qisqaroq matndan boshlang.
- **Mikrofon ishlamayapti (Linux Snap)** → `sudo snap connect voicestudio:audio-record`
- **Boshqa xato** → https://github.com/debpalash/VoiceStudio/blob/main/docs/install/troubleshooting.md yoki https://github.com/debpalash/VoiceStudio/issues
