"""Scene timeline from the real narration audio.
Each line is sped up by TEMPO (ffmpeg atempo, pitch kept) into audio/t/<id>.wav, then placed: lines of one scene follow
each other after GAP, scenes are contiguous (LEAD/TAIL pad them); the segments bridge (slide 8) has no voice and lasts BRIDGE seconds.
Writes audio/timeline.json (read by film.html and audio.py)."""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).parent
TEMPO = 1.0   # no speed-up: the user asked for an unhurried, word-by-word delivery
SCENES = [  # narrative order (not slide order): identity -> origins -> scale -> standing -> the plant -> national brand ->
            # innovation -> portfolio -> reach (localization, logistics) -> 2035 goals -> ecosystem -> close
    ("title", ["title"]), ("hist", ["hist1", "h2020", "h2021", "h2022", "h2024", "h2026"]), ("struct", ["struct", "sales"]), ("kpi", ["kpi", "brands"]),
    ("cluster", ["cl0", "c_kia", "c_skd", "c_lok", "c_sht", "c_nev", "c_rd", "c_dost", "cl4"]),
    ("dost", ["dost1", "dost2"]), ("rnd", ["rnd"]), ("seg", []), ("geo", ["geo"]), ("logi", ["logi"]),
    ("goals", ["goals"]), ("eco", ["eco"]), ("outro", ["outro"]),
]
LEAD = {"title": 1.8, "cluster": 1.4}   # picture before the first voice line of a scene
TAIL = {"outro": 3.2, "cluster": 2.6, "rnd": 3.6}   # picture after the last line
GAP, BRIDGE = 0.7, 3.8

timing = json.loads((HERE / "audio/timing.json").read_text())
(HERE / "audio/t").mkdir(exist_ok=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)

cur, scenes, lines = 0.0, [], {}
for sid, ids in SCENES:
    start = cur
    if not ids:
        cur += BRIDGE; scenes.append({"id": sid, "start": round(start, 3), "end": round(cur, 3), "lines": []}); continue
    cur += LEAD.get(sid, 0.55)
    for i, lid in enumerate(ids):
        src, out = HERE / f"audio/{lid}.mp3", HERE / f"audio/t/{lid}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-ar", "48000", "-ac", "1", str(out)], check=True)
        d = dur(out)
        lines[lid] = {"vo": round(cur, 3), "end": round(cur + d, 3), "scene": sid,
                      "words": [{"text": w["text"], "t": round(cur + w["start"] / TEMPO, 3), "e": round(cur + w["end"] / TEMPO, 3)} for w in timing[lid]["words"]]}
        cur += d + (GAP if i < len(ids) - 1 else 0)
    cur += TAIL.get(sid, 0.4)
    scenes.append({"id": sid, "start": round(start, 3), "end": round(cur, 3), "lines": ids})
total = round(cur, 3)
(HERE / "audio/timeline.json").write_text(json.dumps({"total": total, "tempo": TEMPO, "scenes": scenes, "lines": lines}, ensure_ascii=False, indent=1))
print(f"total {total:.2f}s")
for s in scenes: print(f"  {s['id']:8s} {s['start']:7.2f} -> {s['end']:7.2f}  {' '.join(s['lines'])}")
