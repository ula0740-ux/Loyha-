---
name: motion-reel
description: Make a product or showreel motion video rendered from code (seek(t) HTML/canvas engine, closed-form springs, beat grid, synthesized sound, critique loop). Use when the user asks for a launch video, showreel, product reel, animated explainer, UI-morph loop, motion ad, or an overnight "director's brief" film. Distilled from Movez's course "How to build motion design studio with Opus 5.5" (27 Sep 2026). Pairs with the motion-design skill (render/audio templates, QA scripts).
---

# Motion reel studio

"The prompt is 10 % of the video. The other 90 % is the harness." A model writes a **program**, not a video: one function `seek(t)` paints the exact frame for any time; a headless browser walks time, screenshots each frame, ffmpeg stitches. Nothing depends on a timer, so every render is identical and a change is a one-line edit plus a re-render.

## Inputs to collect first
Product + URL, duration, formats (9:16 / 1:1 / 16:9), brand colors + fonts, a reference (frame, video or image folder), music (file or "synthesize"). If the user gives none, pick defaults and say so.

## Pipeline
1. Gather assets from the URL with Playwright into `./assets`. List them. Never redraw the product UI from imagination: crop and animate the real thing.
2. If a reference exists, extract a frame every 0.5 s with ffmpeg and write `docs/style_guide.md` (palette hex, type family/weight/tracking, shot lengths, transitions, camera, texture/grain, how text enters and exits). Take the grammar, never the content, logos or characters.
3. Measure or synthesize music: `python scripts/beats.py song.wav > beats.json` (state changes on beats, big moments on downbeats, SFX on hits).
4. Write `docs/shotlist.md` on the beat grid. Show it and wait for OK (unless told to run autonomously).
5. Build `index.html` with `window.seek(t)` using `lib/motion.js` springs. Follow the house rules below.
6. Contact sheet → critique pass (`prompts/critique-pass.txt`) → fix. 3 rounds minimum, until every score is 8+.
7. `node scripts/render.mjs` → `node scripts/sfx.mjs cues.json out/sfx.wav` → mix to -14 LUFS → `out/final.mp4`, all formats.
8. Deliver `final.mp4`, `contact.png`, `poster.png`. Say what you'd improve next.

## House rules (render contract)
- Every film is a pure function of time: `window.seek(t)` paints frame t.
- No CSS transitions, no setTimeout, no requestAnimationFrame in render mode, no state carried between frames. Seeded noise only (mulberry32 `rng` in lib/motion.js), never `Math.random`.
- Encode H.264 yuv420p, CRF 16. Live preview loop only when `!navigator.webdriver`.
- Setup per film folder: `npm i -D playwright` (render.mjs resolves it from the film folder). In this container Chromium is at `/opt/pw-browsers/chromium` (render.mjs picks it up; never `playwright install`).
- Pages with `<script type="module">` (importing lib/motion.js) must be served: `python3 -m http.server 8000 &` then `node render.mjs --url http://localhost:8000/index.html`. Browsers block ES modules on file://.
- beats.py uses librosa if installed, else a numpy fallback (smoothed onset autocorrelation with a 120 BPM prior; verified on a 120 BPM click track).

## Look
- Banned defaults: centered title on gradient, everything fading in, corner labels and frame borders, glow on UI chrome, generic particle bursts, bouncy easing, dead time.
- One display face, one UI face. One accent color unless the brief says otherwise.
- Every 2 to 4 seconds something new must happen on screen. Hook in the first 2 s.
- Without a reference the model falls back to its default look. Naming a style ("Linear launch", "Apple bumper") beats describing one; a frame or video beats both.

## Springs (lib/motion.js)
Cheap motion eases A→B on a fixed curve; expensive motion has mass. Use closed-form springs so `seek(t)` stays a pure function.
- When a value changes target several times, never restart the spring: `track(t, keys)` sums one spring per change, so frame 812 renders without simulating 0..811.
- Presets (k stiffness, d damping): snappy UI 320/30 (buttons, toggles, leading edges) · default 170/26 (cards, containers, camera) · heavy 120/24 (big type, 3D, logo lockups) · playful 180/12 (mascots, stickers, visible overshoot).
- Tab indicator: leading edge stiffer than trailing edge (`indicator`) so it stretches.
- Text inside a morphing box enters after the morph starts and leaves before the next one (`swapAlpha`).
- Refactor prompt: "Replace every easing curve with closed-form springs from lib/motion.js. Tiny overshoot on UI, none on type. Any value with more than one target uses track()."

## Sound
If a track is supplied, measure it (beats.py). If not, synthesize on the same timeline as the picture (sfx.mjs voices: click, pop, thump, whoosh; extend with kick/hat/pad as needed). Hits on the measured beat grid, loudness -14 LUFS.

## Effort
Medium for small fixes and re-renders, xhigh for new films, max when the first 3 seconds have to carry a launch. "go all out" works as an effort multiplier.

## Prompt library
Templates in `prompts/`:
- `one-liner.txt`: the viral showreel sentence + variants (longer with piano score, anti-slop guardrail, story/history, agency persona). Tests the engine, never the idea ("brief contagion": everyone's reel rhymes). Use once, then move on.
- `brand.txt`: point the reel at a product URL (real screenshots, 5-beat story, 120 BPM synth, 9:16 first).
- `reference.txt`: style_guide + shotlist from a reference before any code.
- `ui-morph-spec.txt`: XML spec, one shape never cuts, 8-12 UI states, cursor drives every change, exact loop.
- `director-brief.txt`: overnight multi-session film (logline, refs, tools/keys, character bible, beat sheet, gated workflow, subagents with ANIMATION_GUIDE.md, critique loop, deliverables).
- `critique-pass.txt`: make the model watch its own frames.

## Critique loop (the habit that separates viral clips from "mid")
```
ffmpeg -i out/final.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 out/contact.png        # overview
ffmpeg -ss 4.1 -i out/final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 out/strip.png        # 12 frames around a fast action
ffmpeg -i out/final.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 out/phone.png           # phone readability
ffmpeg -stream_loop 1 -i out/final.mp4 -c copy out/loop_check.mp4                              # loop seam
```
Determinism check: render the same seconds twice, hashes must match. Iteration is the method, not a failure (the honest "one prompt" films took 3-163 model calls).

## Formats and shipping
Write scenes against a layout function, not fixed pixels; render 9:16, 1:1 and 16:9 from one timeline, reframing type and UI per format (never crop). API keys live in `.env` (e.g. `ELEVENLABS_API_KEY`), never in a prompt or screenshot.

## Route B (only if asked)
Remotion (React; series, templates, data-driven): `npx create-video@latest`, `npx skills add remotion-dev/skills`. HyperFrames (HTML + GSAP): `npx hyperframes init`, `npx skills add heygen-com/hyperframes`. Hand-drawn Node canvas rigs: `buildwithhanif/claude-animation-skill`.

## Reference repos
JohnHeibel/PDoomVideo (subagents + ANIMATION_GUIDE.md/STORYBOARD.md, chapters in src/ch/), JohnHeibel/ClaudeAnimationBase (starter), buildwithhanif/claude-animation-skill, heygen-com/hyperframes, remotion.dev/docs/ai/skills, WinterArc21/Battle-of-Austerlitz-Film (long form), guanmo-ai/awesome-ai-motion (prompts), athemeroy/awesome-opus-5-5-videos (dataset).
