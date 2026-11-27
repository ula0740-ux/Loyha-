"""Real produced music and SFX from ElevenLabs (Music + Sound Effects APIs), not numpy synthesis.
The key is never printed; the network proxy injects it into the xi-api-key header.
Run: ELEVENLABS_API_KEY=proxy-injected python3 build/gen_audio_assets.py [music] [sfx]"""
import json, os, sys, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; API = 'https://api.elevenlabs.io'
def post(path, body, out):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(), method='POST',
                                 headers={'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'proxy-injected'), 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
    with urllib.request.urlopen(req, timeout=600) as r: Path(out).write_bytes(r.read())
    print('ok', out, Path(out).stat().st_size)
TL = json.loads((HERE / 'audio/timeline.json').read_text())
if 'music' in sys.argv:
    post('/v1/music', {
        'prompt': ('Premium cinematic corporate underscore for an automotive manufacturing company profile film. Instrumental only. '
                   'Warm modern orchestral-electronic hybrid: soft felt piano motif, warm strings pad, gentle pulsing synth bass, light '
                   'precise percussion entering after the intro, confident and optimistic, steady 100 BPM, builds gradually with a '
                   'restrained lift in the middle, no vocals, no dramatic drops, stays calm under a narrator, ends with a resolved final chord and soft tail.'),
        'music_length_ms': int((TL['total'] + 4) * 1000), 'force_instrumental': True}, HERE / 'audio/music.mp3')
SFX = {
    'whoosh': ('Soft cinematic air whoosh pass-by, smooth, clean, no impact', 1.2),
    'impact': ('Deep soft cinematic sub boom impact with short warm reverb tail, subtle', 2.0),
    'tick': ('Single soft modern UI tick, subtle click, clean', 0.5),
    'pop': ('Soft glassy interface pop, gentle, short', 0.5),
    'rise': ('Short smooth airy riser swell, soft, cinematic', 2.0),
    'chime': ('Elegant soft logo chime, warm bell with shimmer, single note, gentle tail', 3.0),
    'car': ('Modern van driving slowly on a smooth indoor showroom floor, approaching and stopping, quiet engine, soft tire roll', 4.0),
}
if 'sfx' in sys.argv:
    for k, (txt, d) in SFX.items():
        out = HERE / f'audio/sfx/{k}.mp3'
        if not out.exists(): post('/v1/sound-generation', {'text': txt, 'duration_seconds': d, 'prompt_influence': 0.5}, out)
