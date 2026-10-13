---
name: uzbek-tts
description: Natural literary Uzbek voice-over (Uzbek Latin script) for motion-design videos via ElevenLabs. Use whenever a video, reel or studio scene needs Uzbek narration, when Uzbek words are mispronounced (e.g. "Jizzax" read as "jizzaks", "Axborot" as "aksborot"), or when preparing Uzbek text with numbers, abbreviations or English terms for TTS.
---

# Uzbek TTS (ElevenLabs)

**Goal:** fluent, natural and accurate narration in Uzbekistan's literary Uzbek.

Talk to the user in Uzbek. Code is in `studio/server/uz/`, the lexicon is `studio/lexicon/uz-lexicon.json`, and the CLI is `studio/scripts/uz.ts` (`npm run uz -- …` from `studio/`). Before changing anything, read the existing integration (`server/uz/eleven.ts`, `server/tts/elevenlabs*.ts`) and improve it without breaking it. Run `npx tsc --noEmit && npm test` before committing.

## 1. Language and pronunciation
- Text sent to TTS is **Uzbek Latin only**. Cyrillic input is converted to Latin. Never send Cyrillic, and never respell words to imitate English or Russian pronunciation.
- Do not let the model read Uzbek words as English letter names. Abbreviations use Uzbek letter names (x = "xa", q = "qa"), or better, their lexicon expansion.
- **x** is the deep Uzbek x and must never come out as "eks". **h** is the soft h and must never be dropped. **x and h are never swapped** ("Jizzah", "hodim" are wrong spellings).
- Keep oʻ, gʻ, sh, ch and ng exactly as written. Syllable breaks never split a digraph.

## 2. Preparing the text (`prepareUzbek`, always)
- Spelling is normalised (apostrophes go to ʻ/ʼ, Cyrillic goes to Latin).
- Numbers, percentages, dates and ranges become words.
- Abbreviations and English terms become Uzbek equivalents from the lexicon (`kind: term|abbr`, e.g. IT → "axborot texnologiyalari", online → "onlayn"). ALL-CAPS entries only match ALL-CAPS text, so the Uzbek word "it" stays "it".
- Pauses come from punctuation: every line and every sentence ends with a mark (`addPauses`).
- Never change or remove a word's letters on your own. A lexicon `word` entry may only add a syllable hyphen (`sameLetters` enforces this). For example, "Jiz-zax" and "Ax-borot" were tested and are read correctly.

## 3. ElevenLabs
- Model `eleven_v3`, the default, gave the best Uzbek in our STT tests. `eleven_v4` accepts `language_code: "uz"` but scored worse (ADM → "adiyam", Axborot → "aksborot").
- Only send parameters the model accepts. `ttsBody()` and `MODEL_CAPS` encode the tested facts:
  - `language_code` → v4 only;
  - `previous_text`/`next_text` → v4 and multilingual_v2, not v3;
  - `seed` → v3, v4 and multilingual_v2.
  Probe any new parameter first and record the result.
- Voice: Sarah `EXAVITQu4vr4xnSDxMaL` (female). Rachel, Matilda, Alice, Lily and Jessica scored ~100% on the same test.
- Pronunciation dictionaries: the current key lacks `pronunciation_dictionaries_write` (401). The local lexicon does the same job as alias rules and works on every model. Phoneme rules do not work on v3 anyway.

## 4. Quality control
- `npm run uz -- make "matn" out/a.mp3` (or `--file matn.txt`) works sentence by sentence:
  - it caches each sentence and checks it with Speech-to-Text (scribe_v1, uzb);
  - it retries a sentence until it reaches ≥97% and keeps the best take;
  - it writes `out/a.json` with each sentence's score and problems.
- `npm run uz -- redo out/a.json 2,4` regenerates only those sentences. After a lexicon fix, `make` also regenerates only the sentences whose prepared text changed.
- `npm run uz -- word Soʻz [--takes 3]` tests the plain word plus syllable forms in a carrier sentence and saves the best as a `candidate`. The user listens, then `lexicon approve`.
- Known artefacts of the STT ear, which are not errors: the rounded a (bazasida → "bozasida") and a final f heard as "v".
- Films: `video/pptx-film/narrate.mts` follows the same pattern (prepareUzbek; up to 4 takes per line with an STT check; `ONLY=id` re-records single lines).

## Secrets
Never print or commit `ELEVENLABS_API_KEY`. It comes only from the environment or `studio/.env` (gitignored).
