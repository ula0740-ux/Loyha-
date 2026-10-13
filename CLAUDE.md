# Loyha — motion-design videos with Uzbek narration

- Talk to the user in **Uzbek**.
- Uzbek voice-over (ElevenLabs): always follow `.claude/skills/uzbek-tts/SKILL.md`. The goal is fluent, natural and accurate literary Uzbek. In short:
  - **Uzbek Latin script only.** No English or Russian respelling, and no English letter names.
  - x = deep x (never "eks"), h = soft h (never dropped). **x and h are never swapped.** oʻ, gʻ, sh, ch and ng are kept.
  - Always send text through `prepareUzbek`. It turns numbers and abbreviations into words, replaces English terms with Uzbek equivalents from the lexicon, and adds punctuation for pauses.
  - Never change or drop a word's letters. Fix mispronunciations in `studio/lexicon/uz-lexicon.json`; only syllable hyphens are allowed, checked with `sameLetters`.
  - Model `eleven_v3`. Send only the parameters the model supports (`ttsBody`/`MODEL_CAPS`).
  - Check every sentence with STT (`npm run uz -- make`). Regenerate only the bad sentences (`npm run uz -- redo`), and test problem words with `npm run uz -- word`.
- Before changing the ElevenLabs integration, read the existing code and improve it without breaking it.
- Secrets: `ELEVENLABS_API_KEY` comes only from the environment or `studio/.env`. Never write it in code, print it, or commit it.
- Do not break existing features: run `cd studio && npx tsc --noEmit && npm test` before committing.
