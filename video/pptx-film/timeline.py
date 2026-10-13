"""Scene timeline from the narration: every scene starts when the previous one ends and lasts
lead + voice + tail. Word times become absolute. Writes audio/timeline.json (read by film.html and audio.py)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
timing = json.loads((HERE / "audio/timing.json").read_text())
ORDER = ["intro", "hire", "adapt", "reserve", "leave", "standards", "outro"]
LEAD = {"intro": 1.25}
TAIL = {"outro": 2.4}

cur, scenes = 0.0, {}
for sid in ORDER:
    t = timing[sid]
    lead, tail = LEAD.get(sid, 0.55), TAIL.get(sid, 0.8)
    vo = cur + lead
    end = vo + t["duration"] + tail
    scenes[sid] = {
        "start": round(cur, 3), "vo": round(vo, 3), "voEnd": round(vo + t["duration"], 3), "end": round(end, 3),
        "words": [{"text": w["text"], "t": round(vo + w["start"], 3), "e": round(vo + w["end"], 3)} for w in t["words"]],
    }
    cur = end
out = {"total": round(cur, 3), "order": ORDER, "scenes": scenes}
(HERE / "audio/timeline.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"total {cur:.2f}s")
for sid in ORDER:
    s = scenes[sid]
    print(f"  {sid:10s} {s['start']:6.2f} -> {s['end']:6.2f}  (ovoz {s['vo']:.2f}-{s['voEnd']:.2f})")
