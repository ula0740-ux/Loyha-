"""Scene timeline from the real narration audio.
Each line is sped up by TEMPO (ffmpeg atempo, pitch kept) into audio/t/<id>.wav, then placed: lines of one scene follow
each other after GAP, scenes are contiguous (LEAD/TAIL pad them); the segments bridge (slide 8) has no voice and lasts BRIDGE seconds.
v3: the cut follows the user's music (audio/music_grid.json, from build/music_analyze.py). Scene starts snap to bar lines
(P = mean bar length), sentences start on the next beat when that is close, the cluster fly-over starts exactly on the
track's climax entry (bar 40) and the outro white flash lands on the track's final accent (bar 72). The music plan
(which track bars play where) is written into timeline.json for audio.py.
Writes audio/timeline.json (read by film.html and audio.py)."""
import math
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
LEAD = {"title": 6.5, "cluster": 1.4}   # v4: title = 5.9 s logo reveal (user's reference opening) + white bloom, then the voice   # picture before the first voice line of a scene
TAIL = {"outro": 3.2, "cluster": 2.6, "rnd": 3.6}   # picture after the last line
GAP, BRIDGE = 0.7, 3.8
PAD = 0.06   # v4: silence before each take + 5 ms fade-in, so a take that starts mid-fricative ("Shtamplash") is not clicked/clipped

timing = json.loads((HERE / "audio/timing.json").read_text())
(HERE / "audio/t").mkdir(exist_ok=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)

G = json.loads((HERE / "audio/music_grid.json").read_text())
TB = G["bars"]; P = (TB[-1] - TB[0]) / (len(TB) - 1); BEAT = P / 4
CLIMAX_BAR, ACCENT_BAR, REPEAT_FROM = 40, 72, 16      # track bars: climax entry, final accent, section repeated after the cluster
def snap_bar(t, floor_t):                            # nearest usable bar line: earlier by <= .5 s if no voice is cut, else the next one
    prev, nxt = math.floor(t / P) * P, math.ceil(t / P) * P
    return prev if t - prev <= .5 and prev >= floor_t else nxt

cur, scenes, lines, last_voice = 0.0, [], {}, 0.0
for sid, ids in SCENES:
    if scenes:
        cur = snap_bar(cur, last_voice + .3); scenes[-1]["end"] = round(cur, 3)
    start = cur
    if not ids:
        cur += BRIDGE; scenes.append({"id": sid, "start": round(start, 3), "end": round(cur, 3), "lines": []}); continue
    cur += LEAD.get(sid, 0.55)
    for i, lid in enumerate(ids):
        src, out = HERE / f"audio/{lid}.mp3", HERE / f"audio/t/{lid}.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"afade=t=in:d=0.005,adelay={int(PAD*1000)}", "-ar", "48000", "-ac", "1", str(out)], check=True)
        d = dur(out)
        nb = math.ceil((cur - .02) / BEAT) * BEAT + .05            # start just after the next beat when it is close
        if 0 <= nb - cur < .35: cur = nb
        lines[lid] = {"vo": round(cur, 3), "end": round(cur + d, 3), "scene": sid,
                      "words": [{"text": w["text"], "t": round(cur + PAD + w["start"] / TEMPO, 3), "e": round(cur + PAD + w["end"] / TEMPO, 3)} for w in timing[lid]["words"]]}
        cur += d + (GAP if i < len(ids) - 1 else 0); last_voice = lines[lid]["end"]
    cur += TAIL.get(sid, 0.4)
    scenes.append({"id": sid, "start": round(start, 3), "end": round(cur, 3), "lines": ids})
# outro: the white flash on the first bar line after the last word, then 4.2 s of logo card
flash = math.ceil((lines["outro"]["end"] + .35) / P) * P
total = round(flash + 4.2, 3); scenes[-1]["end"] = total
# music plan: film bar k <-> track bar k + off, so that the cluster starts on the climax entry. v4: the film before the
# cluster is now longer than the track before its climax, so `pad` bars (a multiple of 4, one phrase) of section A are
# repeated early on (bar line join) instead of leaving silence at the start.
kc = round(next(x["start"] for x in scenes if x["id"] == "cluster") / P)
pad = 0 if kc <= CLIMAX_BAR else math.ceil((kc - CLIMAX_BAR) / 4) * 4
sb = CLIMAX_BAR + pad - kc                                  # track bar under film bar 0 (negative: silence first)
s0 = TB[sb] if sb >= 0 else TB[0] + sb * P
segs = []
if pad:
    F1 = REPEAT_FROM + pad - sb                             # film bar where the track jumps back to bar 16
    segs.append({"film": 0.0, "track": round(s0, 3), "dur": round(F1 * P, 3)})
    f72 = ACCENT_BAR - REPEAT_FROM + F1
    segs.append({"film": round(F1 * P, 3), "track": TB[REPEAT_FROM], "dur": round((f72 - F1) * P, 3)})
else:
    f72 = ACCENT_BAR - sb
    segs.append({"film": 0.0, "track": round(s0, 3), "dur": round(f72 * P, 3)})
seg1_end = f72 * P
segs.append({"film": round(seg1_end, 3), "track": TB[REPEAT_FROM], "dur": round(flash - seg1_end, 3)})   # section A again, through the breakdown into the climax
segs.append({"film": round(flash, 3), "track": TB[ACCENT_BAR], "dur": round(total - flash + .3, 3)})     # final accent on the flash
music = {"bar": P, "s0": round(s0, 3), "pad": pad, "segments": segs}
(HERE / "audio/timeline.json").write_text(json.dumps({"total": total, "tempo": TEMPO, "flash": round(flash, 3), "music": music, "scenes": scenes, "lines": lines}, ensure_ascii=False, indent=1))
print("music", music)
print(f"total {total:.2f}s")
for s in scenes: print(f"  {s['id']:8s} {s['start']:7.2f} -> {s['end']:7.2f}  {' '.join(s['lines'])}")
