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
