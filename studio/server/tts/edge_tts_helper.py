"""Microsoft Edge read-aloud voices (free, no key, not open source).
usage: python3 edge_tts_helper.py <voice> <text-file> <out.mp3> <words.json>
Writes MP3 audio and exact word boundaries [{"text","start","end"}] in seconds."""
import asyncio, json, os, sys
import edge_tts


async def main(voice, text_file, out_mp3, out_json):
    text = open(text_file, encoding="utf8").read()
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    com = edge_tts.Communicate(text, voice, boundary="WordBoundary", proxy=proxy)
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                s = chunk["offset"] / 1e7
                words.append({"text": chunk["text"], "start": s, "end": s + chunk["duration"] / 1e7})
    json.dump(words, open(out_json, "w", encoding="utf8"), ensure_ascii=False)


asyncio.run(main(*sys.argv[1:5]))
