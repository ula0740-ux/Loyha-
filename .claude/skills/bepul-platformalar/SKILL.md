---
name: bepul-platformalar
description: Free, open-source alternatives to three paid platforms (Zehn Blog pack, added 2026-11-25 at the user's request) — Open Generative AI instead of Higgsfield (image/video generation), AppFlowy instead of Notion (notes, docs, tasks), VoiceStudio instead of ElevenLabs (TTS, voice cloning, dubbing). Use when the user asks about free/open-source replacements for Higgsfield, Notion or ElevenLabs, wants to install or try Open Generative AI, AppFlowy or VoiceStudio (OmniVoice Studio), or asks how to set them up on Mac, Windows, Linux or phone.
---

# Bepul platformalar (Zehn Blog paketi)

The user added this pack on 2026-11-25 ("Shuni o'zingni skillaringga qo'shib ol"). Source: the Zehn Blog video "Hali ham bularga pul to'layapsizmi?". The original files are in `reference/`, unchanged.

| Paid platform | Free alternative | File |
|---|---|---|
| Higgsfield (image/video) | **Open Generative AI** (MIT) | `reference/01_Open-Generative-AI.md` |
| Notion (notes, docs, tasks) | **AppFlowy** (AGPL-3.0) | `reference/02_AppFlowy.md` |
| ElevenLabs (voice) | **VoiceStudio**, formerly OmniVoice Studio (AGPL-3.0) | `reference/03_VoiceStudio.md` |

All official links are in `reference/havolalar.txt`. The pack's own guidance for helping a non-programmer step by step is in `reference/paket-korsatmasi.md`. Use it when the user wants to install one of these on their own computer.

## Rules

- **Read the tool's file in full before you talk about it.** Take links, commands and requirements only from these files. Do not invent any. Prices date from November 2026; check the official site if it matters.
- **Official sources only:** the GitHub Releases pages, the official install scripts, Homebrew, App Store, Google Play, Flathub and Snap.
- **Talk in Uzbek, one step per message, in plain words.** Write button names exactly as shown on screen, with an Uzbek translation in brackets.
- **Say what costs money before you start.** Open Generative AI's cloud models (Kling, Veo, Sora…) need a paid Muapi key. Only its local models are free.
- **Check the computer first.** The main limits:
  - VoiceStudio does not generate voice on Intel Macs and needs macOS 13.3 or later.
  - Open Generative AI on an 8 GB Mac runs only SD 1.5 models (e.g. Dreamshaper 8).
  - Open Generative AI makes local video only with an NVIDIA or AMD GPU.
  - Each tool needs 10–15 GB of free disk space.
- **Never type passwords, API keys or card details yourself.** The user enters them in the app.
- **Ask before installing.** These are desktop apps for the user's own computer. This cloud container cannot run their GUI for the user. Use the user's machine through Remote Control if attached, or guide them in chat (mode B in `paket-korsatmasi.md`).

## How this relates to the project

- **Open Generative AI** (Anil-matcha) and the already installed **Open Higgsfield AI** (`tools/open-higgsfield`, skill `open-higgsfield`) both target muapi.ai. Both need a paid key for cloud models. Open Generative AI can also run free local models on a capable PC.
- **VoiceStudio vs ElevenLabs.** The approved Uzbek narration baseline remains ElevenLabs `eleven_v4` + `language_code: uz` (skill `uzbek-tts`, approved 2026-10-13). Do not switch a film's voice to VoiceStudio without the user's approval by ear. It is unverified for Uzbek ("O'zbek tilini o'zingiz sinab ko'ring"). Its default OmniVoice model is CC-BY-NC, so it is **non-commercial only**, which matters for company videos such as the ADM films. Never clone a person's voice without their consent.
- **AppFlowy** is a Notion replacement for notes and tasks. It is the lightest of the three and the only one with full phone apps. The free cloud tier is limited to 1 workspace and 100 MB.

## Installed in this repo (2026-11-25, cloud container check)

The user asked to install all three ("Hammasini o'rnat"). Result in this Linux x64 cloud container (4 CPU, 15 GB RAM, no GPU, no display):

| Tool | Path | Pinned commit | State here |
|---|---|---|---|
| Open Generative AI | `tools/open-generative-ai/` | `f1b8359baecab053d177b1b6df60704db6ea0fa4` (v2.0.0, 2026-11-24) + submodules Vibe-Workflow `c65ce89`, Open-Poe-AI `3e21ebc`, Open-AI-Design-Agent `ebc0ce7` | Installed and built; web UI verified |
| VoiceStudio | `tools/voicestudio/` | `202e2139814897a438541c707668e6ae90c159d2` (0.5.9-beta.9, 2026-11-24) | JS deps installed; Python backend blocked by the network |
| AppFlowy | — | — | Not installed here (desktop/phone app). Install on the user's own computer/phone from the links in `reference/02_AppFlowy.md` |

The sources are not committed (Open Generative AI ~34 MB, VoiceStudio ~100 MB without `.git`). Only `tools/<name>/setup.sh` is committed; everything else in those folders is in `.gitignore`. In a new session, rebuild with:

```bash
sh tools/open-generative-ai/setup.sh   # fetches the pinned commit + submodules, npm install, build:packages
sh tools/voicestudio/setup.sh          # fetches the pinned commit, bun install, bun run setup:api
```

### Open Generative AI — what works here

- **Web version (Next.js):** `cd tools/open-generative-ai && npm run dev` → http://localhost:3000 (redirects to `/studio`). Verified 2026-11-25: `/studio`, `/studio/image`, `/studio/video` return 200 and render the "Enter your Muapi.ai API key" screen with no page errors. The web version uses **cloud models only**, so every generation needs a paid Muapi key and spends credits: confirm the cost with the user first. The key is entered in the UI (stored in the browser's localStorage); never commit it.
- **Desktop renderer:** `npm run vite:build` builds. Electron itself needs a display (and refuses to run as root without disabling its sandbox, which we do not do), so `npm run electron:dev` is for the user's own computer.
- **Local models (free) do not work here:** local inference exists only in the Electron app; it downloads the sd.cpp engine from GitHub Releases/api.github.com and the weights from huggingface.co, and this environment's proxy blocks all three (HTTP 403). sd.cpp does run on CPU, so SD 1.5 (Dreamshaper 8, ~2 GB) would be feasible but slow (the README cites ~10 s/step for a CPU fallback on an M2; not measured here). Local video needs an NVIDIA/AMD GPU (Wan2GP).
- **For real image/video work in this project** use the installed cloud tools (`open-higgsfield`, the Higgsfield connector) with the user's approval for credits, or install the Open Generative AI desktop app on the user's PC (Releases page) for free local SD 1.5/Z-Image.

### VoiceStudio — what works here

- `bun install` succeeded (1089 packages). `bun run setup:api` (CPU PyTorch via `uv sync --locked`) **fails**: `download.pytorch.org`/`download-r2.pytorch.org` are blocked by the proxy, and the voice models come from `huggingface.co`, also blocked. So no voice can be generated in this container. The UI alone is useless without the backend.
- To run it headless where those hosts are open: `cd tools/voicestudio && bun run dev:web` (backend on 127.0.0.1:3900 + web UI). CPU works but is slow; pick a light engine (KittenTTS, Supertonic-3, PocketTTS).
- Simplest path: the user installs the desktop app on their own computer (`reference/03_VoiceStudio.md`).
- Uzbek is unverified and the default model is CC-BY-NC (non-commercial). The ElevenLabs baseline (`uzbek-tts`) stays unless the user approves a change by ear.

### To unblock in the cloud

Allowing `huggingface.co` (plus its CDN hosts) and `download.pytorch.org` / `download-r2.pytorch.org` in the environment's network settings would let VoiceStudio's backend install and download models, and Open Generative AI's local weights download (the Electron engine download would also need GitHub Releases/api.github.com). Ask the user before proposing that change.
