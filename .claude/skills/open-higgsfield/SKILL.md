---
name: open-higgsfield
description: Open Higgsfield AI (Clabstream AI Studio) — local Higgsfield-style studio in tools/open-higgsfield (Image, Video, Cinema, LipSync) running through the paid muapi.ai API. Use when the user asks for AI image/video generation through "Open Higgsfield", muapi.ai models (Flux, Midjourney v7, Seedream, nano-banana, Kling, Wan…), or cinematic camera/lens prompt presets.
---

# Open Higgsfield AI (tools/open-higgsfield)

The user installed this on 2026-10-18 ("keyinchalik shu skillardan foydalanamiz").
Source: github.com/ClabstreamTeam/Open-Higgsfield-AI (the user's zip was identical).
**There is no LICENSE file** — use it internally only; do not redistribute or copy its code into other projects.

## What it is
- A Next.js 14 app (+ Vite/Electron variants). UI: `packages/studio` (Image/Video/Cinema/LipSync studios), pages in `app/`.
- It does NOT generate anything itself. All generation goes through **api.muapi.ai** (paid credits).
  - `app/api/generate/route.js` → POST `https://api.muapi.ai/api/v1/<endpoint>` with header `x-api-key`.
  - `app/api/jobs/[id]` polls the result; `app/api/upload` uploads reference files.
  - `app/api/generate/image` can use `HUGGINGFACE_API_KEY`.
- Model list: `models_dump.json`, `src/lib/models.js` (49 image models + video models).
- Prompt presets (camera bodies, lenses, focal lengths, apertures, lighting/mood/style tags): `src/lib/promptUtils.js`, preview images in `public/assets/cinema/`.

## Run
```sh
cd tools/open-higgsfield
npm install --ignore-scripts      # node_modules is not committed
npm run build:studio              # builds packages/studio
MUAPI_API_KEY=... npx next dev -p 3000   # → http://localhost:3000/studio/
```
- Keys come only from the environment or `tools/open-higgsfield/.env.local` (git-ignored). Never write a key in code, print it, or commit it.
- Without `MUAPI_API_KEY` the UI opens, but generation returns `Missing MUAPI_API_KEY`.
- Electron builds (`electron:build*`, `afterPack.js` ad-hoc codesign) are for the user's own Mac/Windows PC, not this container.

## Rules
- Before any paid generation, tell the user it spends muapi.ai credits and confirm.
- For our own motion-design videos the code pipeline (`motion-design`, `motion-reel`, `hyperframes`) stays the free default; use this studio only when AI-generated footage/images are really needed.
- Uzbek narration still always goes through `uzbek-tts` (ElevenLabs), never through this app.
