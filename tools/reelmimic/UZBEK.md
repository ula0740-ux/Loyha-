## O‘zbekcha ovoz (ElevenLabs) — Loyha qoidasi

Video tili oʻzbekcha boʻlsa (oʻzbekcha matn yoki narration), Yating yoki media-use TTS EMAS, shu skriptni ishlat:

    python .claude/skills/video-clone/scripts/uz_tts.py --lines lines.json --outdir <loyiha>/build/vo
    python .claude/skills/video-clone/scripts/uz_tts.py "Matn." --out <fayl>.wav

- Matn oʻzbek LOTIN yozuvida, toʻgʻri adabiy imloda yoziladi (x va h almashtirilmaydi). Ovozga tayyorlash (x→kh, sonlar, ADM → "A-de-em,", gap oxiridagi x → "!") avtomatik bajariladi; matnni qoʻlda oʻzgartirma.
- Har bir faylning yonida `.json` hisobot bor: `stt_min` < 0.97 yoki `problems` boʻlsa — oʻsha qatorni qayta yarat yoki soʻzni Loyha lugʻatiga qoʻsh (`npm run uz -- word <Soʻz>`, Loyha/studio ichida).
- Subtitr va ekrandagi yozuvlar uchun oʻzbek harflari toʻliq boʻlgan shrift: Inter, Montserrat, Onest yoki Oswald (Loyha/assets/fonts).
- Kalit: ELEVENLABS_API_KEY (muhit yoki Loyha/studio/.env). Hech qachon loyiha fayliga yozilmaydi.
