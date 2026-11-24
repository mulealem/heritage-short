"""Stage: narration — one WAV per shot via Gemini TTS; offline mock fallback.

Real mode needs GEMINI_API_KEY in .env. Mock mode synthesises a soft tone with
the exact planned duration so the edit timing is testable without any key.

Output: outputs/narration/<shot_id>.wav + outputs/narration/durations.json
"""
import io
import json
import math
import struct
import sys
import time
import wave
from pathlib import Path

from pipeline import common, net

SAMPLE_RATE = 24000


def gemini_tts(text, style, voice):
    """Call Gemini TTS; returns raw PCM bytes (L16, 24 kHz mono)."""
    key = common.env_key("GEMINI_API_KEY")
    model = common.env_key("GEMINI_TTS_MODEL") or "gemini-2.5-flash-preview-tts"
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "%s:generateContent?key=%s" % (model, key))
    prompt = (style + ":\n\n" + text) if style else text
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    body, _, _ = net.http_json(url, payload,
                               headers={"x-goog-api-key": key})
    parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    inline = parts[0].get("inlineData", {}) if parts else {}
    if not inline.get("data"):
        raise RuntimeError("no audio in TTS response: %s" % json.dumps(body)[:300])
    import base64
    return base64.b64decode(inline["data"]), model


def pcm_to_wav(pcm, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)


def mock_wav(path, seconds, pitch_hz):
    """A gentle tone with a slow fade in/out — clearly a placeholder voice."""
    n = int(seconds * SAMPLE_RATE)
    frames = bytearray()
    for i in range(n):
        t = i / SAMPLE_RATE
        env = min(1.0, t / 0.3, (seconds - t) / 0.3)
        wob = 0.6 + 0.4 * math.sin(2 * math.pi * 0.8 * t)  # speech-ish wobble
        v = int(9000 * env * wob * math.sin(2 * math.pi * pitch_hz * t))
        frames += struct.pack("<h", v)
    pcm_to_wav(bytes(frames), path)


def cache_get(path, key):
    meta = path.with_suffix(".json")
    if path.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key:
        return True
    return False


def cache_put(path, key, extra=None):
    meta = {"key": key, "extra": extra or {}}
    path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))


def main():
    sb = common.load_storyboard()
    out_dir = common.stage_dir("narration")
    style = sb["meta"].get("narrator_style", "calm, warm, unhurried")
    voice = common.env_key("TTS_VOICE") or "Kore"
    use_real = common.has_key("GEMINI_API_KEY") and not common.force_mock()

    if not use_real:
        why = "FORCE_MOCK=1" if common.force_mock() else "GEMINI_API_KEY missing"
        print("narration: MOCK mode (%s) — placeholder tones, real timing" % why)

    durations = {}
    for i, shot in enumerate(sb["shots"]):
        text = shot["narration"]["text"]
        lang = shot["narration"]["lang"]
        out_path = out_dir / ("%s.wav" % shot["id"])
        key = common.hash_key(text, lang, style, voice, "tts-v1")

        if cache_get(out_path, key):
            d = common.probe_duration(out_path)
            durations[shot["id"]] = d
            common.log_call(stage="narration", model="gemini-tts", seed=None,
                            params={"shot": shot["id"], "chars": len(text)},
                            status="cache", output=str(out_path), note="cache hit")
            continue

        if use_real:
            t0 = time.time()
            try:
                pcm, model = gemini_tts(text, style, voice)
            except RuntimeError as e:
                common.log_call(stage="narration", model=model, status="error",
                                params={"shot": shot["id"]}, note=str(e))
                print("  ! TTS failed for %s (%s); falling back to mock tone" % (shot["id"], e))
                mock_wav(out_path, shot["duration_s"], 180 + 12 * i)
            else:
                pcm_to_wav(pcm, out_path)
                ms = int((time.time() - t0) * 1000)
                cost = common.est_cost("gemini-tts-per-1k-chars", len(text) / 1000.0)
                common.log_call(stage="narration", model=model, seed=voice,
                                params={"shot": shot["id"], "chars": len(text), "lang": lang},
                                latency_ms=ms, status="ok", output=str(out_path),
                                cost_usd_est=cost)
        else:
            mock_wav(out_path, shot["duration_s"], 180 + 12 * i)
            common.log_call(stage="narration", model="mock-tone", seed=None,
                            params={"shot": shot["id"], "seconds": shot["duration_s"]},
                            status="mock", output=str(out_path))

        d = common.probe_duration(out_path)
        durations[shot["id"]] = d
        cache_put(out_path, key, {"seconds": d})
        print("  %s: %.2fs (planned %.2fs)" % (shot["id"], d, shot["duration_s"]))

    (out_dir / "durations.json").write_text(
        json.dumps(durations, indent=1, sort_keys=True))
    total = sum(durations.values())
    print("narration done: %d lines, %.1fs of speech -> %s"
          % (len(durations), total, out_dir / "durations.json"))
    if total > 90:
        print("  ! narration is %.0fs — trim text in storyboard.json (target 60–90s total)" % total)


if __name__ == "__main__":
    main()
