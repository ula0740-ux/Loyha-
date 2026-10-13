---
name: uzbek-tts
description: Natural literary Uzbek voice-over (Latin or Cyrillic) for motion-design videos via ElevenLabs. Use whenever a video, reel or studio scene needs Uzbek narration, when Uzbek words are mispronounced (e.g. "Jizzax" read as "jizzaks"), or when preparing Uzbek text with numbers/abbreviations for TTS.
---

# Uzbek TTS (ElevenLabs)

Talk to the user in Uzbek. Code lives in `studio/server/uz/`, the lexicon in `studio/lexicon/uz-lexicon.json`, the CLI in `studio/scripts/uz.ts` (`npm run uz -- …` from `studio/`).

## Hard rules
1. Write the narration in correct literary spelling. **x (х, deep) and h (ҳ, soft) are never swapped or dropped**, not even as a pronunciation hack ("Jizzah", "hodim" are wrong).
2. Letters map one-to-one: oʻ=ў, gʻ=ғ, q=қ, sh=ш, ch=ч, ng=нг, sʼh=сҳ. Cyrillic ҳ х қ ғ ў are kept.
3. When a word is mis-read, fix it in the **lexicon**, never in the script text. Run `npm run uz -- word <Soʻz>` (it tests the Latin, Cyrillic and extra forms through STT and saves the best one as a `candidate`). A Cyrillic spoken form inside Latin text is fine, e.g. Jizzax → `Жиззах`.
4. Always send text through `prepareUzbek(text, script)`. It handles the lexicon, script normalization for mixed text, numbers → words, and abbreviations. The original text stays separate (captions show the original words).
5. Only send parameters the model is known to accept (`MODEL_CAPS` in `eleven.ts`). `language_code: "uz"` → only `eleven_v4`. Default model: `eleven_v3`. If a new parameter is untested, probe it first and record the result in `MODEL_CAPS`.
6. Before the final render, check every line: `npm run uz -- test "…"` for Latin vs Cyrillic, or the STT check built into the narration script. Retake lines below about 97%. Then ask the user to listen and approve the candidate lexicon entries.
7. Never print or commit `ELEVENLABS_API_KEY`. It comes from the environment or from `studio/.env` (gitignored).

## Known results (2026-10-13, voice Sarah `EXAVITQu4vr4xnSDxMaL`)
- eleven_v3: Latin 98.8%, Cyrillic 98.8% (mixed sentence). eleven_v4 with `uz`: 97.6% / 95.2%.
- Jizzax: Cyrillic `Жиззах` 100%, Latin → "jizax". STT writes the Uzbek rounded a as "o" (bazasida → "bozasida") and final f as "v". These are artifacts of the ear, not errors.

## Workflow for a film
1. Write `narration.json` lines in literary Uzbek.
2. Record with `prepareUzbek` + `synth` (see `video/pptx-film/narrate.mts`, `ONLY=id` re-takes single lines; it prints the STT score per line).
3. Run `npm run uz -- word X` for every word that is flagged as a problem, then re-record.
4. Build the timeline, mix, render.
