# Loyha — motion-design videos with Uzbek narration

- Talk to the user in **Uzbek**.
- Uzbek voice-over: always follow `.claude/skills/uzbek-tts/SKILL.md`. In short:
  - x and h are never swapped or dropped;
  - fix mispronunciations in `studio/lexicon/uz-lexicon.json`, never by misspelling the text;
  - send text through `prepareUzbek`;
  - send only the API parameters the model supports;
  - check each line with STT before the final render.
- Secrets: `ELEVENLABS_API_KEY` comes only from the environment or `studio/.env`. Never write it in code, print it, or commit it.
- Do not break existing features: run `cd studio && npx tsc --noEmit && npm test` before committing.
