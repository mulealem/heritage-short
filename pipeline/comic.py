"""Comic renderer: storyboard + panels + narration → the motion-comic film.

This is a real, deterministic rendering path beside the video-clip assembler:
`comic/` is an fframes (Rust, CPU) scene that draws full-bleed comic panels
with camera moves, insert cuts, halftone screens, speech balloons, SFX bursts
and kinetic narration captions. This module writes the scene data, renders the
picture, mixes the audio master (reusing the assemble stage's narration
placement, ducking and loudness normaliser), and muxes the final MP4 with a
soft subtitle track.

Commands:
    python3 -m pipeline.comic build        # write comic/media/film.json + panels
    python3 -m pipeline.comic render       # 9:16: cargo render + audio mux
    python3 -m pipeline.comic render-wide  # 16:9: the landscape comic page
    python3 -m pipeline.comic remux [9x16|16x9]   # re-mix audio over an existing picture
    python3 -m pipeline.comic all          # build + render (9:16)

Both aspect ratios come from the same film.json and the same audio master; the
renderer is compiled once per layout (the `wide` cargo feature), so the 16:9
page is a layout of the same cuts, not a second edit.

Audio: a full mix when outputs/music/score_final.wav exists; otherwise the
radio cut — narration only, normalised. Both are real mixes, never placeholders.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from pipeline import assemble as asm
from pipeline import common
from pipeline import narration as narr

COMIC = common.ROOT / "comic"
MEDIA = COMIC / "media"
PANELS = common.ROOT / "comic" / "panels.json"
FILM_JSON = COMIC / "film.json"
OUT = common.OUT / "comic"
FPS = 24


def cargo_bin():
    for cand in (shutil.which("cargo"), str(Path.home() / ".cargo" / "bin" / "cargo")):
        if cand and Path(cand).exists():
            return cand
    sys.exit("cargo not found — install rustup (see comic/README.md)")


def split_words(text, start, dur):
    """Proportional word timings within one narration line (chars + 1 weight)."""
    tokens = [t for t in text.split() if t]
    if not tokens:
        return []
    weights = [len(t) + 1 for t in tokens]
    total = float(sum(weights))
    out, cursor = [], start
    for tok, wt in zip(tokens, weights):
        share = dur * wt / total
        out.append({"t0": round(cursor, 3), "t1": round(cursor + share, 3), "w": tok})
        cursor += share
    return out


def build():
    sb = common.load_storyboard()
    panels = json.loads(PANELS.read_text())
    # the recorded lines, edited to the storyboard's timing contract
    durations, fit_dir = narr.ensure_fit(sb)
    asm.NARR_DIR = fit_dir

    timed, total = asm.build_timeline(sb, durations)
    MEDIA.mkdir(parents=True, exist_ok=True)

    shots = []
    missing = []
    for i, item in enumerate(timed):
        shot = item["shot"]
        sid = shot["id"]
        keyframe = common.OUT / "keyframes" / ("%s.png" % sid)
        if not keyframe.exists():
            # allow .jpg from other providers
            alt = common.OUT / "keyframes" / ("%s.jpg" % sid)
            keyframe = alt if alt.exists() else keyframe
        if not keyframe.exists():
            missing.append(str(keyframe))
            continue
        panel_name = "panel_%s%s" % (sid, keyframe.suffix)
        shutil.copy(keyframe, MEDIA / panel_name)

        spec = panels["shots"].get(sid, {})
        cuts = [{"img": panel_name, "at": float(spec.get("base_at", 0.0))}]
        ins_src = common.OUT / "comic_panels" / ("%s.jpg" % sid)
        extras_available = [
            (i, ex) for i, ex in enumerate(spec.get("extras", []), 1)
            if (common.OUT / "comic_panels" / ("%s_x%d.jpg" % (sid, i))).exists()
        ]
        reuse_available = [
            (i, ru) for i, ru in enumerate(spec.get("reuse", []), 1)
            if (common.OUT / "comic_panels" / ru["img"]).exists()
        ]
        # Legacy insert only when no finer cuts are actually available; mixing
        # both produced duplicate cuts 30 ms apart.
        if ins_src.exists() and spec.get("insert") and not extras_available \
                and not reuse_available:
            insert_name = "ins_%s.jpg" % sid
            shutil.copy(ins_src, MEDIA / insert_name)
            cuts.append({"img": insert_name, "at": 0.55})
        for i, ru in reuse_available:
            ru_name = "re_%s_%d.jpg" % (sid, i)
            shutil.copy(common.OUT / "comic_panels" / ru["img"], MEDIA / ru_name)
            cuts.append({"img": ru_name, "at": float(ru.get("at", 0.0))})
        for i, ex in extras_available:
            ex_name = "ins_%s_x%d.jpg" % (sid, i)
            shutil.copy(common.OUT / "comic_panels" / ("%s_x%d.jpg" % (sid, i)),
                        MEDIA / ex_name)
            cuts.append({"img": ex_name, "at": float(ex.get("at", 0.5))})
        cuts.sort(key=lambda c: c["at"])

        balloon = None
        if spec.get("balloon"):
            b = spec["balloon"]
            balloon = {"text": b["text"], "start": float(b["start"]),
                       "end": float(b["end"]), "top": float(b.get("top", 0.16))}
        raw_sfx = spec.get("sfx") or []
        if isinstance(raw_sfx, dict):
            raw_sfx = [raw_sfx]
        sfx = [{"text": s["text"], "t": float(s["t"]),
                "x": float(s.get("x", 0.7)), "y": float(s.get("y", 0.25))}
               for s in raw_sfx]

        moves = ["push_in", "pan_r", "push_out", "pan_l", "push_in", "shake",
                 "pan_l", "push_in", "shake", "push_out"]
        words = split_words(shot["narration"].get("en") or shot["narration"]["text"],
                            item["narr_start"], item["narr_dur"])
        shots.append({
            "id": sid,
            "start": item["start"],
            "dur": item["dur"],
            "panels": cuts,
            "mv": spec.get("mv") or moves[i % len(moves)],
            "balloon": balloon,
            "sfx": sfx,
            "words": words,
            # the spoken line, for the landscape page's Amharic margin
            "am": shot["narration"]["text"] if shot["narration"].get("lang") != "en" else "",
        })

    if missing:
        sys.exit("missing keyframes: %s\nrun: make keyframes" % ", ".join(missing))

    end = sb["end_card"]
    film = {
        "fps": FPS,
        "width": 1080,
        "height": 1920,
        "duration": round(total, 3),
        "shots": shots,
        "ratios": list(sb["meta"]["aspect_ratios"]),
        "end": {
            "start": round(total - float(end.get("seconds", 3.0)), 3),
            "dur": float(end.get("seconds", 3.0)),
            "title": sb["meta"]["title"],
            "text": end["text"],
            "text_am": end.get("text_am", ""),
            "sub": end.get("subtitle", "made with AI"),
        },
    }
    FILM_JSON.write_text(json.dumps(film, ensure_ascii=False, indent=1))
    print("film.json: %d shots, %.1fs -> %s" % (len(shots), total, FILM_JSON))
    return film


def narration_is_current(sb):
    """True when every WAV on disk was recorded from the storyboard's line.

    The upgrade changed the Amharic script; rendering before re-TTS would pair
    new English captions with old audio. Refuse instead.
    """
    style = sb["meta"].get("narrator_style", "calm, warm, unhurried")
    voice = common.env_key("TTS_VOICE") or "Kore"
    version = common.env_key("TTS_CACHE_VERSION") or "tts-v2"
    stale = []
    for shot in sb["shots"]:
        n = shot["narration"]
        out = common.OUT / "narration" / ("%s.wav" % shot["id"])
        key = common.hash_key(n["text"], n.get("lang", "am"), style, voice, version)
        meta = out.with_suffix(".json")
        if not out.exists() or not meta.exists() \
                or json.loads(meta.read_text()).get("key") != key:
            stale.append(shot["id"])
    return stale


LAYOUTS = {
    # ratio name: (picture width, picture height, extra cargo flags)
    "9x16": (1080, 1920, []),
    "16x9": (1920, 1080, ["--features", "wide"]),
}
DISCLOSE = ("AI-generated film. Synthetic images (MiniMax image-01), synthetic "
            "narration (Gemini TTS), a score synthesised by code. A traditional "
            "folk tale of Aleqa Gebre Hanna, retold.")


def picture_for(ratio):
    return OUT / ("picture.mp4" if ratio == "9x16" else "picture_16x9.mp4")


def guard_narration():
    stale = narration_is_current(common.load_storyboard())
    if stale:
        sys.exit("narration does not match the current script: %s\n"
                 "run `make narration` first (a line that is already recorded "
                 "and unchanged is a cache hit)." % ", ".join(stale))


def render(ratio="9x16"):
    """CPU-render the picture for one layout, then mix and mux the film."""
    guard_narration()
    w, h, feat = LAYOUTS[ratio]
    OUT.mkdir(parents=True, exist_ok=True)
    env = {"PATH": str(Path.home() / ".cargo" / "bin") + ":" + "/usr/local/bin:/usr/bin:/bin"}
    cargo = cargo_bin()
    t0 = time.time()
    b = subprocess.run([cargo, "build", "--release"] + feat, cwd=str(COMIC), env=env,
                       capture_output=True, text=True)
    if b.returncode != 0:
        sys.exit("cargo build failed:\n" + (b.stderr or "")[-1500:])
    picture = picture_for(ratio)
    if picture.exists():
        picture.unlink()
    r = subprocess.run([cargo, "run", "--release", "--quiet"] + feat +
                       ["--", "render", "--renderer", "cpu", "-o", str(picture)],
                       cwd=str(COMIC), env=env, capture_output=True, text=True)
    if r.returncode != 0 or not picture.exists():
        sys.exit("render failed:\n" + ((r.stderr or "") + (r.stdout or ""))[-1500:])
    common.log_call(stage="comic", model="fframes-cpu", latency_ms=int((time.time() - t0) * 1000),
                    params={"fps": FPS, "w": w, "h": h, "ratio": ratio}, status="ok",
                    output=str(picture), note="motion-comic picture render (%s)" % ratio)
    return finish(picture, ratio)


def finish(picture, ratio="9x16"):
    """Audio master + subtitles + mux, reusing an existing picture render."""
    sb = common.load_storyboard()
    durations, fit_dir = narr.ensure_fit(sb)
    asm.NARR_DIR = fit_dir
    timed, total = asm.build_timeline(sb, durations)
    work = common.stage_dir("comic")
    asm.WORK = work
    asm.write_srt(timed, work / "subtitles.srt")

    score = common.OUT / "music" / "score_final.wav"
    master = work / "master.wav"
    if score.exists() and common.probe_duration(score):
        asm.build_audio_master(timed, total, master)
        audio_note = "full mix (voice + ducked score)"
    else:
        build_narration_master(timed, total, master)
        audio_note = "radio cut (voice only; score not generated yet)"
    common.log_call(stage="comic", model="ffmpeg", status="ok",
                    params={"seconds": round(total, 1), "ratio": ratio}, output=str(master),
                    note=audio_note)

    final = common.OUT / ("film_%s.mp4" % ratio)
    common.run_ffmpeg(["-i", str(picture), "-i", str(master), "-i", "subtitles.srt",
                    "-map", "0:v", "-map", "1:a", "-map", "2:s",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                    "-metadata", "title=%s" % sb["meta"]["title"],
                    "-metadata", "comment=%s" % DISCLOSE,
                    "-movflags", "+faststart", str(final)],
                   stage="comic", note="mux picture + master + subtitles (%s)" % ratio, cwd=work)
    d = common.probe_duration(final)
    print("DONE %s: %.1fs, %.1f MB" % (final.name, d or 0, final.stat().st_size / 1e6))
    if not (55 <= d <= 90):
        print("  ! %.1fs is outside the brief's 60-90s (end card included)" % d)
    return final


def remux(ratio="9x16"):
    """Re-mix audio and mux over an existing picture (no CPU re-render)."""
    guard_narration()
    picture = picture_for(ratio)
    if not picture.exists():
        sys.exit("no picture at %s — run: python3 -m pipeline.comic %s"
                 % (picture, "render" if ratio == "9x16" else "render-wide"))
    return finish(picture, ratio)


def build_narration_master(timed, total, out_wav):
    """Radio cut: narration placed on the timeline, two-pass loudnorm, no score."""
    inputs, chain = asm.build_narration_track(timed, total)
    voice = "voice_raw.wav"
    common.run_ffmpeg(inputs + ["-filter_complex", chain, "-map", "[voice]",
                                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", voice],
                      stage="comic", note="narration track placement", cwd=asm.WORK)
    import re
    p = subprocess.run(
        [common._ffmpeg_bin(), "-hide_banner", "-nostats", "-i", voice,
         "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, cwd=str(asm.WORK))
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', p.stderr, re.S)
    if not m:
        sys.exit("loudnorm measure pass failed:\n" + p.stderr[-800:])
    mv = json.loads(m.group(0))
    common.run_ffmpeg(["-i", voice, "-af",
                       ("loudnorm=I=-14:TP=-1:LRA=11:measured_I=%s:measured_TP=%s:"
                        "measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
                        % (mv["input_i"], mv["input_tp"], mv["input_lra"],
                           mv["input_thresh"], mv["target_offset"])),
                       "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out_wav.name],
                      stage="comic", note="loudnorm -14 LUFS (radio cut)", cwd=asm.WORK)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    ratio = sys.argv[2] if len(sys.argv) > 2 else "9x16"
    if ratio not in LAYOUTS:
        sys.exit("unknown ratio %r (use 9x16 or 16x9)" % ratio)
    if cmd in ("build", "all"):
        build()
    if cmd in ("render", "all"):
        render("9x16")
    if cmd == "render-wide":
        render("16x9")
    if cmd == "remux":
        remux(ratio)


if __name__ == "__main__":
    main()
