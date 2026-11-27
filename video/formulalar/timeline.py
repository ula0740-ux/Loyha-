"""Scene timeline from the narration: every scene starts when the previous one ends and lasts
lead + voice + tail. Word times become absolute. Writes audio/timeline.json (read by film.html and audio.py)."""
import json
from pathlib import Path

HERE = Path(__file__).parent
timing = json.loads((HERE / "audio/timing.json").read_text())
ORDER = ["hook", "intro", "tt1", "tt2", "tt3", "up", "att1", "att2", "jph1", "jph2", "jph3", "over1", "over2", "ct", "rwt", "outro"]
LEAD = {"hook": 1.0}
TAIL = {"outro": 3.2}

cur, scenes = 0.0, {}
for sid in ORDER:
    t = timing[sid]
    lead, tail = LEAD.get(sid, 1.0), TAIL.get(sid, 0.3)
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
