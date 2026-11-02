#!/usr/bin/env python3
"""Uzbek narration for ReelMimic through the Loyha ElevenLabs pipeline (same interface as yating_tts.py).

Uses the approved Loyha settings: eleven_v4 + language_code uz, Uzbek Latin text through prepareUzbek
(x -> kh, variant F "A-de-em, Jizzakh!", numbers in words, lexicon), neighbouring lines as context,
and a Speech-to-Text check with retakes for every sentence.

Key: ELEVENLABS_API_KEY from the environment or Loyha's studio/.env (never stored in a project or printed).
Needs the Loyha repo (env LOYHA_DIR, default ~/Loyha- or /home/user/Loyha-).

  python uz_tts.py "Assalomu alaykum, bu ADM Jizzax." --out l1.wav
  python uz_tts.py --lines lines.json --outdir vo/        # [{"id":"L1","text":"..."}, ...] -> vo/L1.wav (+ vo/L1.json report)
"""
import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path


def loyha_dir() -> Path:
    for p in (os.environ.get("LOYHA_DIR"), "~/Loyha-", "/home/user/Loyha-"):
        if p and (Path(p).expanduser() / "studio/scripts/uz.ts").exists():
            return Path(p).expanduser()
    sys.exit("Loyha repo not found: set LOYHA_DIR to the folder that contains studio/scripts/uz.ts")


def synth(text: str, out: str) -> dict:
    studio = loyha_dir() / "studio"
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        mp3 = os.path.join(td, "line.mp3")
        r = subprocess.run(["npx", "tsx", "scripts/uz.ts", "make", text, mp3], cwd=studio, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(mp3):
            sys.exit(f"uz_tts failed: {(r.stderr or r.stdout)[-500:]}")
        rep = json.load(open(mp3[:-4] + ".json", encoding="utf-8"))
        if out.endswith(".mp3"):
            shutil.copy(mp3, out)
        else:  # ReelMimic engines expect wav
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ar", "44100", "-ac", "1", out], check=True)
    seg = rep.get("segments", [])
    report = {"text": text, "out": out, "model": rep.get("model"),
              "stt_min": min((s.get("similarity", 1) for s in seg), default=None),
              "problems": [p for s in seg for p in (s.get("problems") or [])]}
    json.dump(report, open(os.path.splitext(out)[0] + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?"); ap.add_argument("--out"); ap.add_argument("--lines"); ap.add_argument("--outdir")
    a = ap.parse_args()
    if a.lines:
        for x in json.load(open(a.lines, encoding="utf-8")):
            r = synth(x["text"], os.path.join(a.outdir, f"{x['id']}.wav"))
            print(r["out"], f"STT {r['stt_min']:.3f}" if r["stt_min"] is not None else "")
        return
    if not (a.text and a.out): sys.exit("give TEXT --out FILE, or --lines FILE --outdir DIR")
    r = synth(a.text, a.out)
    print(r["out"], f"STT {r['stt_min']:.3f}" if r["stt_min"] is not None else "", r["problems"] or "")


if __name__ == "__main__":
    main()
