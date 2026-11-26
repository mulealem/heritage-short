"""Stage: narration — one WAV per shot via Gemini TTS. Real only.

Needs GEMINI_API_KEY in .env. A failed call (after net.py's retries) stops
the stage — no placeholder audio is ever written.

Output: outputs/narration/<shot_id>.wav + outputs/narration/durations.json
"""
import base64
import json
import math
import sys
import time
import wave
from array import array

from pipeline import common, net

SAMPLE_RATE = 24000


def gemini_tts(text, style, voice):
    """Call Gemini TTS; returns raw PCM bytes (L16, 24 kHz mono)."""
    key = common.env_key("GEMINI_API_KEY")
    model = common.env_key("GEMINI_TTS_MODEL") or "gemini-3.8-flash-tts"
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "%s:generateContent?key=%s" % (model, key))
    # Never send the style as bare prose: Gemini TTS reads a descriptive
    # phrase aloud ("a warm Amharic folk storyteller ...") instead of
    # interpreting it (FAILURES.md F11). Tone comes from the voice choice.
    prefix = common.env_key("TTS_STYLE_PREFIX")
    prompt = (prefix + "\n\n" + text) if prefix else text
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
    return base64.b64decode(inline["data"]), model


def pcm_to_wav(pcm, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)


def trim_terminal_burst(path):
    """Remove the fixed noise burst Gemini TTS appends to every clip.

    Observed Nov 2026: after the last word and a short pause, every response
    ends with ~100 ms of near-full-scale noise (peak 0 dBFS) after a block of
    digital silence. It is not speech; left in, it is audible as a click/static
    at the end of every line. Detect the terminal loud run, require a quiet gap
    before it, cut at the burst start minus 10 ms and apply a 10 ms fade.
    Returns (old_seconds, new_seconds) when trimmed, else None.
    """
    with wave.open(str(path), "rb") as w:
        n, sr = w.getnframes(), w.getframerate()
        data = array("h")
        data.frombytes(w.readframes(n))
    if n < sr:  # too short to judge
        return None
    block = max(1, int(sr * 0.01))
    scan = max(0, n - int(sr * 0.6))
    rms = []
    for i in range(scan, n, block):
        chunk = data[i:i + block]
        if not chunk:
            break
        acc = sum(float(x) * x for x in chunk) / len(chunk)
        rms.append(10 * math.log10(acc / (32768.0 * 32768.0) + 1e-12))
    loud = [j for j, v in enumerate(rms) if v > -20]
    if not loud:
        return None
    j = loud[-1]
    while j > 0 and rms[j - 1] > -45:
        j -= 1
    burst_start = scan + j * block
    burst_len = n - burst_start
    if not (int(0.04 * sr) <= burst_len <= int(0.30 * sr)):
        return None
    # require the burst to be preceded by actual quiet (not a loud word ending)
    if j < 2 or any(v > -40 for v in rms[max(0, j - 2):j]):
        return None
    cut = burst_start - int(0.01 * sr)
    if cut < int(0.5 * sr):
        return None
    kept = data[:cut]
    fade = min(len(kept), max(1, int(0.01 * sr)))
    for i in range(fade):
        kept[len(kept) - 1 - i] = int(kept[len(kept) - 1 - i] * (1.0 - i / fade))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(kept.tobytes())
    return n / sr, cut / sr


def cache_get(path, key):
    meta = path.with_suffix(".json")
    if path.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key:
        return True
    return False


# --- edit to time -------------------------------------------------------------
# The storyboard's `meta.timing` says how the recorded lines are fitted to the
# cut without re-recording: hold every long internal pause to `pause_cap_seconds`
# and apply a small pitch-preserving `narration_tempo`. Gemini TTS breathes for
# 0.5–0.9 s between phrases; capping those pauses recovers several seconds
# while leaving the speech rate itself almost alone.

FIT_DIR = common.OUT / "narration_fit"


def _read_wav(path):
    with wave.open(str(path), "rb") as w:
        sr, n = w.getframerate(), w.getnframes()
        pcm = array("h")
        pcm.frombytes(w.readframes(n))
    return pcm, sr


def _write_wav(path, pcm, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def cap_pauses(pcm, sr, pause_cap, floor_db=-42.0):
    """Hold every internal pause longer than `pause_cap` down to `pause_cap`.

    A pause is a run of 10 ms blocks all below `floor_db`. The cut runs from
    `pause_cap` into that run to 50 ms before the next speech onset, so both
    joined edges are inside silence (each gets a 2 ms fade as well). Pauses at
    the very start or end of a line are left alone. Returns (samples, seconds
    removed, number of pauses capped).
    """
    n = len(pcm)
    block = max(1, int(sr * 0.01))
    quiet = []
    for i in range(0, n, block):
        chunk = pcm[i:i + block]
        acc = sum(float(x) * x for x in chunk) / max(1, len(chunk))
        quiet.append(10 * math.log10(acc / (32768.0 * 32768.0) + 1e-12) < floor_db)
    runs, start = [], None
    for j, q in enumerate(quiet):
        if q and start is None:
            start = j
        elif not q and start is not None:
            runs.append((start, j))
            start = None
    if start is not None:
        runs.append((start, len(quiet)))
    edge = 30                      # never touch the first/last 300 ms
    lead_out = int(0.05 * sr)      # silence kept before the next word
    fade = max(1, int(0.002 * sr))
    cuts = []
    for a, b in runs:
        if a < edge or b > len(quiet) - edge:
            continue
        cut_from = a * block + int(pause_cap * sr)
        cut_to = b * block - lead_out
        if cut_to - cut_from > int(0.05 * sr):
            cuts.append((cut_from, cut_to))
    if not cuts:
        return pcm, 0.0, 0
    out = array("h")
    pos = 0
    for cut_from, cut_to in cuts:
        piece = pcm[pos:cut_from]
        for i in range(fade):       # fade the silence down into the join
            piece[len(piece) - 1 - i] = int(piece[len(piece) - 1 - i] * (1.0 - i / fade))
        out.extend(piece)
        pos = cut_to
    out.extend(pcm[pos:])
    removed = sum(b - a for a, b in cuts) / float(sr)
    return out, removed, len(cuts)


def fit_line(src, dst, pause_cap, tempo):
    """One recorded line -> the edited line used in the cut. Returns a dict."""
    pcm, sr = _read_wav(src)
    raw_s = len(pcm) / float(sr)
    removed, capped = 0.0, 0
    if pause_cap > 0:
        pcm, removed, capped = cap_pauses(pcm, sr, pause_cap)
        tmp = dst.with_suffix(".cap.wav")
        _write_wav(tmp, pcm, sr)
    else:
        tmp = src
    if abs(tempo - 1.0) > 1e-3:
        common.run_ffmpeg(["-i", str(tmp), "-filter:a", "atempo=%.4f" % tempo,
                           "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
                          stage="narration-fit", note="atempo %.3f" % tempo)
    else:
        _write_wav(dst, pcm, sr)
    if tmp != src and tmp.exists():
        tmp.unlink()
    return {"raw_s": round(raw_s, 3), "fit_s": round(common.probe_duration(dst), 3),
            "pause_s_removed": round(removed, 3), "pauses_capped": capped}


def ensure_fit(sb, force=False):
    """Write outputs/narration_fit/<id>.wav (+ durations.json) per meta.timing.

    Returns (durations, directory): what the timeline and the mix should use.
    With no timing block, or a pass-through one, the raw recordings are the
    edit and nothing is written. Deterministic and credential-free: a clone
    rebuilds the fitted lines from the committed raw ones.
    """
    timing = sb["meta"].get("timing") or {}
    pause_cap = float(timing.get("pause_cap_seconds") or 0)
    tempo = float(timing.get("narration_tempo") or 1.0)
    raw_dir = common.OUT / "narration"
    raw_file = raw_dir / "durations.json"
    if not raw_file.exists():
        sys.exit("no outputs/narration/durations.json — run: make narration")
    raw = json.loads(raw_file.read_text())
    if pause_cap <= 0 and abs(tempo - 1.0) < 1e-3:
        return raw, raw_dir

    out_dir = FIT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = [s["id"] for s in sb["shots"]]
    sources = {sid: int((raw_dir / (sid + ".wav")).stat().st_mtime * 1000) for sid in ids}
    want = {"pause_cap": pause_cap, "tempo": tempo, "sources": sources}
    state = out_dir / "fit.json"
    durations = {}
    cached = False
    if not force and state.exists():
        have = json.loads(state.read_text())
        cached = (have.get("pause_cap") == pause_cap and have.get("tempo") == tempo
                  and have.get("sources") == sources
                  and all((out_dir / (sid + ".wav")).exists() for sid in ids))
    if cached:
        for sid in ids:
            durations[sid] = common.probe_duration(out_dir / (sid + ".wav"))
        common.log_call(stage="narration-fit", model="ffmpeg-atempo", status="cache",
                        params={"pause_cap": pause_cap, "tempo": tempo},
                        output=str(out_dir), note="cache hit (%d lines)" % len(ids))
    else:
        for sid in ids:
            t0 = time.time()
            info = fit_line(raw_dir / (sid + ".wav"), out_dir / (sid + ".wav"),
                            pause_cap, tempo)
            durations[sid] = info["fit_s"]
            common.log_call(stage="narration-fit", model="ffmpeg-atempo",
                            latency_ms=int((time.time() - t0) * 1000), status="ok",
                            params=dict(info, shot=sid, pause_cap=pause_cap, tempo=tempo),
                            output=str(out_dir / (sid + ".wav")),
                            note="%.2fs -> %.2fs (%d pauses held, tempo %.3f)"
                                 % (info["raw_s"], info["fit_s"], info["pauses_capped"], tempo))
        state.write_text(json.dumps(want, indent=1, sort_keys=True))
    (out_dir / "durations.json").write_text(
        json.dumps(durations, indent=1, sort_keys=True))
    print("narration fit: pause cap %.2fs, tempo %.3f -> %.1fs of speech (%s)"
          % (pause_cap, tempo, sum(durations.values()), out_dir))
    return durations, out_dir


def cache_put(path, key, extra=None):
    meta = {"key": key, "extra": extra or {}}
    path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))


def main():
    sb = common.load_storyboard()
    out_dir = common.stage_dir("narration")
    style = sb["meta"].get("narrator_style", "calm, warm, unhurried")
    voice = common.env_key("TTS_VOICE") or "Kore"

    durations = {}
    for shot in sb["shots"]:
        text = shot["narration"]["text"]
        lang = shot["narration"]["lang"]
        out_path = out_dir / ("%s.wav" % shot["id"])
        # TTS_CACHE_VERSION lets a prompt/engine change force a re-record
        # (bump it instead of hand-deleting sidecars).
        key = common.hash_key(text, lang, style, voice,
                              common.env_key("TTS_CACHE_VERSION") or "tts-v2")

        if cache_get(out_path, key):
            d = common.probe_duration(out_path)
            durations[shot["id"]] = d
            common.log_call(stage="narration", model="gemini-tts", seed=None,
                            params={"shot": shot["id"], "chars": len(text)},
                            status="cache", output=str(out_path), note="cache hit")
            continue

        # The key is only needed when a line is actually (re)recorded, so a
        # clone that carries the cached narration needs no credential at all.
        common.require_key("GEMINI_API_KEY",
                           "get one at https://aistudio.google.com/apikey (free tier)")
        model = common.env_key("GEMINI_TTS_MODEL") or "gemini-3.8-flash-tts"
        t0 = time.time()
        try:
            pcm, model = gemini_tts(text, style, voice)
        except RuntimeError as e:
            common.log_call(stage="narration", model=model, status="error",
                            params={"shot": shot["id"]}, note=str(e))
            sys.exit("TTS failed for %s: %s\nfix the key/quota in .env and rerun "
                     "(done shots are cache hits, you will not pay twice)"
                     % (shot["id"], e))
        pcm_to_wav(pcm, out_path)
        trimmed = trim_terminal_burst(out_path)
        if trimmed:
            print("  %s: trimmed TTS tail burst %.2fs -> %.2fs"
                  % (shot["id"], trimmed[0], trimmed[1]))
        ms = int((time.time() - t0) * 1000)
        cost = common.est_cost("gemini-tts-per-1k-chars", len(text) / 1000.0)
        common.log_call(stage="narration", model=model, seed=voice,
                        params={"shot": shot["id"], "chars": len(text), "lang": lang},
                        latency_ms=ms, status="ok", output=str(out_path),
                        cost_usd_est=cost,
                        note="tail burst trimmed" if trimmed else None)

        d = common.probe_duration(out_path)
        durations[shot["id"]] = d
        cache_put(out_path, key, {"seconds": d})
        print("  %s: %.2fs (planned %.2fs)" % (shot["id"], d, shot["duration_s"]))
        if shot is not sb["shots"][-1]:
            # Free TTS tier allows 3 requests/minute; pace real calls.
            pace = float(common.env_key("TTS_SECONDS_BETWEEN_CALLS") or 21)
            if pace > 0:
                print("  ... pacing %.0fs (free-tier 3 req/min)" % pace)
                time.sleep(pace)

    (out_dir / "durations.json").write_text(
        json.dumps(durations, indent=1, sort_keys=True))
    total = sum(durations.values())
    print("narration done: %d lines, %.1fs of speech -> %s"
          % (len(durations), total, out_dir / "durations.json"))
    if total > 90:
        print("  ! narration is %.0fs — trim text in storyboard.json (target 60–90s total)" % total)


if __name__ == "__main__":
    main()
