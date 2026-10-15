---
name: uzbek-tts
description: Natural literary Uzbek voice-over (Uzbek Latin script) for motion-design videos via ElevenLabs. Use whenever a video, reel or studio scene needs Uzbek narration, when Uzbek words are mispronounced (e.g. "Jizzax" read as "jizzaks", "Axborot" as "aksborot"), or when preparing Uzbek text with numbers, abbreviations or English terms for TTS.
---

# Uzbek TTS (ElevenLabs)

**Goal:** fluent, natural and accurate narration in Uzbekistan's literary Uzbek.

Talk to the user in Uzbek. Code is in `studio/server/uz/`, the lexicon is `studio/lexicon/uz-lexicon.json`, and the CLI is `studio/scripts/uz.ts` (`npm run uz -- …` from `studio/`). Before changing anything, read the existing integration (`server/uz/eleven.ts`, `server/tts/elevenlabs*.ts`) and improve it without breaking it. Run `npx tsc --noEmit && npm test` before committing.

## Approved baseline
On 2026-10-13 the user approved `video/pptx-film/ADM_HR_2026_v5.mp4`: "precise and genuine Uzbek on all counts, speak like this from now on".

Its settings are the default for every future Uzbek voice-over, so do not change them without the user's approval:
- `eleven_v4` with `language_code: "uz"` and voice Sarah;
- x → kh;
- variant F ("A-de-em, Jizzakh!");
- context sentences on every call;
- the STT check;
- the lexicon.

## 1. Language and pronunciation
- Text sent to TTS is **Uzbek Latin only**. Cyrillic input is converted to Latin. Never send Cyrillic, and never respell words to imitate English or Russian pronunciation.
- Do not let the model read Uzbek words as English letter names. Abbreviations use Uzbek letter names (x = "xa", q = "qa"), or better, their lexicon expansion.
- **x** is the deep Uzbek (throat) x and must never come out as "eks". **h** is the soft h and must never be dropped. **x and h are never swapped** ("Jizzah", "hodim" are wrong spellings).
- **The user's choice by ear (2026-10-13): in the spoken form, x becomes "kh"** ("Jizzax xodimlariga xayr" → "Jizzakh khodimlariga khayr") on `eleven_v4` with `language_code: "uz"`. `prepareUzbek` does this automatically (`xToKh`; `UZ_X_KH=0` turns it off). The written text and captions keep x. Never send a plain "h" for x.
- Keep oʻ, gʻ, sh, ch and ng exactly as written. Syllable breaks never split a digraph.

- **Variant F (the user's choice by ear, 2026-10-13): "A-de-em, Jizzakh!"**
  - A word whose spoken form ends in the deep x ("…kh") gets "!" instead of "." at the end of a sentence. With a full stop, the model swallowed the final kh ("jizzaq", "ji zzkh").
  - An abbreviation marked `pauseAfter` in the lexicon (ADM) gets a comma, i.e. a short pause, when no punctuation follows it.
  - `prepareUzbek` does both automatically; the written text and captions are unchanged.
- **The user's choices by ear (2026-10-14/15):**
  - 100–199 is read as plain "yuz" ("yuz yetmish ikki"), never "bir yuz" (`numbers.ts`).
  - "Formula" is read the Uzbek way, via the lexicon form "For-mu-la".
  - English terms the user wants read in English go in `{braces}` in the narration (`video/formulalar/narrate.mts`); they skip `prepareUzbek`. Neighbouring-sentence context is always sent through `prepareUzbek`, because English context pulled "ADM" towards an English reading.
- **Never cut a word out of one take and splice it into another.** It was tried: the user heard "ji zzkh" (the vowel lost, the fricative cut). Fix pronunciation with the text form and by regenerating, not with audio surgery.

## 2. Preparing the text (`prepareUzbek`, always)
- Spelling is normalised (apostrophes go to ʻ/ʼ, Cyrillic goes to Latin).
- Numbers, percentages, dates and ranges become words.
- Abbreviations and English terms become Uzbek equivalents from the lexicon (`kind: term|abbr`, e.g. IT → "axborot texnologiyalari", online → "onlayn"). ALL-CAPS entries only match ALL-CAPS text, so the Uzbek word "it" stays "it".
- Pauses come from punctuation: every line and every sentence ends with a mark (`addPauses`).
- Never change or remove a word's letters on your own. A lexicon `word` entry may only add a syllable hyphen (`sameLetters` enforces this). For example, "Jiz-zax" and "Ax-borot" were tested and are read correctly.

## 3. ElevenLabs
- Default model: **`eleven_v4`** with `language_code: "uz"` plus x → kh. The user picked this by ear from 6 variants (v3/v4/multilingual_v2 × x/kh/Cyrillic). STT had rated plain-x v3 as "correct", but the user heard "eks". **The user's ear decides; STT is only a helper.**
- On v4, always send the neighbouring sentences as `previous_text`/`next_text`. Without them, short lines ("Shaffof jarayon. Barqaror jamoa.") can come out with a Persian accent; STT then writes Arabic script. `segments.ts` and `narrate.mts` already do this.
- ADM on v4: "ADM" is read as "adiyam". The lexicon form "A-de-em" is heard as "ADM".
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
- The STT reference is `spokenReference(text)`: the plain written words, numbers in words, x as x. Lexicon spellings ("A-de-em", "Jizzakh") therefore do not count as errors.
- Known artefacts of the STT ear, which are not errors: the rounded a (bazasida → "bozasida"), a final f heard as "v", Zaxira → "zahira", and a final kh sometimes written as "q".
- Films: `video/pptx-film/narrate.mts` follows the same pattern (prepareUzbek with x→kh; context sentences; up to 4 takes per line with an STT check; `ONLY=id` re-records single lines).
- When the user says a sound is still wrong, do not trust STT. Generate a few clearly labelled variants (model × spelling) of their exact sentence, send them, and let the user choose. Then make that choice the default and record it here.

## Secrets
Never print or commit `ELEVENLABS_API_KEY`. It comes only from the environment or `studio/.env` (gitignored).

## Document → MP3 (no video)
Done for `audio/IMTQ/` on 2026-10-13: the user sent a Word file and asked for a 5-minute summary. They liked the result ("zoʻr chiqibdi").

1. Extract the text in document order (paragraphs and tables) with python-docx; run Python with `-I` on uploaded files.
2. Before spending ElevenLabs credits on a long document, give the user the size (words, characters, ≈ minutes at about 115 words per minute). If they want a time limit, write a summary instead of reading everything.
3. Write the summary in literary Uzbek Latin, keeping x as x:
   - about 600 words ≈ 5 min 50 s;
   - use only facts from the document: numbers, deadlines, rules;
   - leave out signatures, blanks, staff tables and Russian approval sheets;
   - start numbered section headings with a word ("Birinchi."). The text stays Latin even when the source is Cyrillic.
4. Run `npm run uz -- make --file text.txt out.mp3`. It uses the baseline settings, an STT check on every sentence, and retries.
5. Very short standalone sentences ("Qisqacha bayon.") come out badly. Join them to the previous sentence with a colon instead of regenerating them again and again. Then re-run `make`; only the changed sentence is regenerated.
6. Send the MP3 and the text that was read. Copy both into the repo (e.g. `audio/<name>/`) so they outlive the cloud session.
