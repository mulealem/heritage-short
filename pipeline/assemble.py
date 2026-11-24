"""Stage: assemble — the finished edit, in code, from the storyboard.

Pipeline (FFmpeg only, deterministic):
  1. timeline from storyboard durations vs measured narration durations
  2. per-shot video segments per aspect ratio (real clip if present, else
     Ken Burns pan-and-zoom over the keyframe — the brief's fallback)
  3. end card segment ("Made with AI")
  4. concat -> picture.mp4
  5. audio master: narration placed on the timeline, music ducked under the
     voice (sidechaincompress), loudness normalised to -14 LUFS / -1 dBTP
  6. burn in subtitles, mux -> outputs/film_9x16.mp4 and outputs/film_16x9.mp4

Subtitles are English (narration.en when narration is in another language).
"""
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

from pipeline import common

WORK = None  # outputs/assemble, set in main
FPS = 24
SUB_FONT_SIZE = 10          # ASS units (PlayRes 288): ~3.5% of frame height
SUB_MARGIN_V_VERT = 34      # keeps text inside vertical safe area
SUB_MARGIN_V_HORZ = 22
NARR_OFFSET = 0.35          # narration starts this long after the shot cut


def srt_ts(t):
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def build_timeline(sb, durations):
    """Returns (shots_with_timing, total). Timing = narration placement."""
    t = 0.0
    timed = []
    for s in sb["shots"]:
        nd = durations.get(s["id"]) or s["duration_s"]
        dur = max(s["duration_s"], nd + 0.7)
        timed.append({
            "shot": s, "start": t, "dur": round(dur, 3),
            "narr_start": round(t + NARR_OFFSET, 3), "narr_dur": nd,
        })
        t += dur
    endcard = float(sb["end_card"].get("seconds", 2.5))
    return timed, round(t + endcard, 3)


def write_srt(timed, path):
    cues = []
    for item in timed:
        n = item["shot"]["narration"]
        text = n.get("en") or n["text"]
        wrapped = "\n".join(textwrap.wrap(text, width=38, max_lines=2,
                                          placeholder="…"))
        cues.append((item["narr_start"], item["narr_start"] + max(item["narr_dur"], 1.2), wrapped))
    lines = []
    for i, (a, b, txt) in enumerate(cues, 1):
        lines += [str(i), "%s --> %s" % (srt_ts(a), srt_ts(b)), txt, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def scale_crop(w, h):
    return ("scale=%d:%d:force_original_aspect_ratio=increase,"
            "crop=%d:%d" % (w, h, w, h))


def kenburns_chain(idx, dur, w, h):
    frames = max(int(dur * FPS), 2)
    up_w, up_h = w * 2, h * 2
    pre = "scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (up_w, up_h, up_w, up_h)
    cx = "iw/2-(iw/zoom)/2"
    cy = "ih/2-(ih/zoom)/2"
    variants = [
        ("1+0.10*on/%d" % frames, cx, cy),
        ("1.10-0.10*on/%d" % frames, cx, cy),
        ("1.06", "(iw-iw/zoom)*on/%d" % frames, cy),
        ("1.06", "(iw-iw/zoom)*(1-on/%d)" % frames, cy),
    ]
    z, x, y = variants[idx % len(variants)]
    zp = ("zoompan=z='%s':x='%s':y='%s':d=%d:s=%dx%d:fps=%d"
          % (z, x, y, frames, w, h, FPS))
    return "%s,%s,fade=t=in:st=0:d=0.12" % (pre, zp)


def clip_chain(dur, w, h):
    return "%s,fps=%d,fade=t=in:st=0:d=0.12" % (scale_crop(w, h), FPS)


def render_segment(idx, item, w, h, work):
    """Render one video-only segment with exact frame count."""
    s = item["shot"]
    plan = item.get("plan", {})
    out = work / ("seg_%02d.mp4" % idx)
    frames = int(round(item["dur"] * FPS))
    if plan.get("mode") == "clip":
        src = common.ROOT / plan["path"]
        head = 0.25  # trim the weak first half-second, per the brief
        args = ["-ss", head, "-i", src, "-frames:v", frames,
                "-vf", clip_chain(item["dur"], w, h)]
        note = "clip %s" % src.name
    else:
        src = common.ROOT / "outputs" / "keyframes" / ("%s.png" % s["id"])
        if not src.exists():
            sys.exit("missing keyframe %s — run: make keyframes" % src)
        args = ["-i", src, "-vf", kenburns_chain(idx, item["dur"], w, h),
                "-frames:v", frames]
        note = "kenburns %s" % src.name
    args += ["-r", FPS, "-pix_fmt", "yuv420p", "-c:v", "libx264",
             "-preset", "medium", "-crf", "20", "-an", str(out)]
    common.run_ffmpeg(args, stage="assemble", note="%s -> seg_%02d" % (note, idx), cwd=WORK)
    return out


def render_endcard(sb, w, h, work):
    dur = float(sb["end_card"].get("seconds", 2.5))
    font = common.find_font()
    out = work / "seg_endcard.mp4"
    frames = int(round(dur * FPS))
    vf = []
    if font:
        def dt(text, size, y_expr, color="white@0.92"):
            tf = work / ("ec_%s.txt" % abs(hash((text, size, y_expr))))
            tf.write_text(text, encoding="utf-8")
            return ("drawtext=fontfile=%s:textfile=%s:fontsize=%d:fontcolor=%s:"
                    "x=(w-text_w)/2:y=%s:line_spacing=%d"
                    % (font, tf, size, color, y_expr, size // 3))
        vf.append(dt(sb["meta"]["title"], h // 14, "h/2-h/5"))
        vf.append(dt(sb["end_card"]["text"], h // 16, "h/2+h/16"))
        if sb["end_card"].get("subtitle"):
            sub = "\n".join(textwrap.wrap(sb["end_card"]["subtitle"], width=34,
                                          max_lines=2, placeholder="…"))
            vf.append(dt(sub, h // 52, "h/2+h/6", "white@0.7"))
    vf.append("fade=t=in:st=0:d=0.5,fade=t=out:st=%.2f:d=0.5" % (dur - 0.5))
    args = ["-f", "lavfi", "-i", "color=c=0x101010:s=%dx%d:d=%.2f:r=%d" % (w, h, dur, FPS),
            "-vf", ",".join(vf), "-frames:v", frames, "-r", FPS,
            "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-an", str(out)]
    common.run_ffmpeg(args, stage="assemble", note="end card", cwd=WORK)
    return out


def concat_segments(segs, out_path):
    lst = work_file("concat.txt")
    lst.write_text("".join("file '%s'\n" % s.name for s in segs), encoding="utf-8")
    common.run_ffmpeg(["-f", "concat", "-safe", "0", "-i", lst.name,
                       "-c", "copy", out_path.name],
                      stage="assemble", note="concat %d segments" % len(segs), cwd=WORK)


def build_narration_track(timed, total):
    """Place each narration WAV on the timeline with silence gaps — gain-safe."""
    inputs = []
    parts = []
    cursor = 0.0
    for i, item in enumerate(timed):
        gap = max(item["narr_start"] - cursor, 0.02)
        parts.append("anullsrc=r=24000:cl=mono,atrim=0:%.3f,asetpts=PTS-STARTPTS[g%d]" % (gap, i))
        narr = common.ROOT / "outputs" / "narration" / ("%s.wav" % item["shot"]["id"])
        inputs += ["-i", narr]
        parts.append("[%d]aformat=sample_rates=24000:channel_layouts=mono[n%d]" % (i, i))
        cursor = item["narr_start"] + item["narr_dur"]
    tail = max(total - cursor, 0.05)
    parts.append("anullsrc=r=24000:cl=mono,atrim=0:%.3f,asetpts=PTS-STARTPTS[gt]" % tail)
    chain = ";".join(parts) + ";"
    labels = "".join("[g%d][n%d]" % (i, i) for i in range(len(timed))) + "[gt]"
    n = len(timed) * 2 + 1
    chain += labels + "concat=n=%d:v=0:a=1[voice]" % n
    return inputs, chain


def build_audio_master(timed, total, out_wav):
    inputs, vchain = build_narration_track(timed, total)
    music_final = common.ROOT / "outputs" / "music" / "score_final.wav"
    music_ph = common.ROOT / "outputs" / "music" / "score_placeholder.wav"
    if music_final.exists():
        music_src, mtag = music_final, "chosen score"
    elif music_ph.exists():
        music_src, mtag = music_ph, "PLACEHOLDER pad"
    else:
        sys.exit("no music in outputs/music/ — run: make music")

    fmt = "aformat=sample_fmts=flt:sample_rates=48000:channel_layouts=stereo"
    fc = vchain + (
        ";[%d]%s,atrim=0:%.3f,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,"
        "afade=t=out:st=%.2f:d=2.5,%s[mus0];"
        "[voice]%s,apad=whole_dur=%.3f,%s,asplit=2[vkey][vmix];"
        "[mus0][vkey]sidechaincompress=threshold=0.02:ratio=6:attack=300:release=1500[musd];"
        "[vmix][musd]amix=inputs=2:duration=longest,volume=2[mix]"
        % (len(timed), fmt, total, max(total - 2.5, 0), fmt, fmt, total, fmt)
    )
    args = inputs + ["-i", music_src, "-filter_complex", fc, "-map", "[mix]",
                     "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out_wav.name]
    common.run_ffmpeg(args, stage="assemble", note="mix voice + ducked music (%s)" % mtag,
                      cwd=WORK)

    # Loudness normalise: two-pass loudnorm to -14 LUFS, true peak -1 dB.
    p = subprocess.run(
        [common._ffmpeg_bin(), "-hide_banner", "-nostats", "-i", out_wav.name,
         "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, cwd=str(WORK))
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        sys.exit("loudnorm measure pass failed:\n" + p.stderr[-800:])
    mv = json.loads(m.group(0))
    common.run_ffmpeg(
        ["-i", out_wav.name, "-af",
         ("loudnorm=I=-14:TP=-1:LRA=11:measured_I=%s:measured_TP=%s:"
          "measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
          % (mv["input_i"], mv["input_tp"], mv["input_lra"],
             mv["input_thresh"], mv["target_offset"])),
         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", "master.wav"],
        stage="assemble", note="loudnorm -14 LUFS (two-pass)", cwd=WORK)


def final_mux(picture, ratio_name, w, h, subtitle_style):
    film = "film_%s.mp4" % ratio_name
    sub = "subtitles=filename=subtitles.srt:force_style='%s'" % subtitle_style
    vf = sub + ",fade=t=out:st=%.2f:d=0.6" % (common.probe_duration(picture) - 0.8)
    common.run_ffmpeg(["-i", picture.name, "-i", "master.wav",
                       "-vf", vf, "-map", "0:v", "-map", "1:a",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                       "-pix_fmt", "yuv420p", "-r", FPS,
                       "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                       "-movflags", "+faststart", "../" + film],
                      stage="assemble", note="final mux %s" % film, cwd=WORK)
    return common.ROOT / "outputs" / film


def work_file(name):
    return WORK / name


def main():
    global WORK
    sb = common.load_storyboard()
    WORK = common.stage_dir("assemble")

    dur_file = common.ROOT / "outputs" / "narration" / "durations.json"
    durations = json.loads(dur_file.read_text()) if dur_file.exists() else {}
    if not durations:
        print("! no narration found — run: make narration (using planned durations)")

    plan_file = common.ROOT / "outputs" / "shots" / "plan.json"
    plan = json.loads(plan_file.read_text()) if plan_file.exists() else {}

    timed, total = build_timeline(sb, durations)
    for item in timed:
        item["plan"] = plan.get(item["shot"]["id"], {})
    print("timeline: %d shots + end card = %.1fs" % (len(timed), total))

    # English subtitles (from narration.en when narration is not English)
    write_srt(timed, work_file("subtitles.srt"))

    finals = []
    ratios = {"9:16": (1080, 1920, SUB_MARGIN_V_VERT),
              "16:9": (1920, 1080, SUB_MARGIN_V_HORZ)}
    for ratio_name in sb["meta"]["aspect_ratios"]:
        w, h, mv = ratios[ratio_name]
        segs = [render_segment(i, item, w, h, WORK) for i, item in enumerate(timed)]
        segs.append(render_endcard(sb, w, h, WORK))
        picture = work_file("picture_%s.mp4" % ratio_name.replace(":", "x"))
        concat_segments(segs, picture)
        build_audio_master(timed, total, work_file("mix.wav"))
        style = ("FontName=DejaVu Sans,FontSize=%d,Outline=1,Shadow=0,"
                 "MarginV=%d,Alignment=2" % (SUB_FONT_SIZE, mv))
        finals.append(final_mux(picture, ratio_name.replace(":", "x"), w, h, style))
        print("  -> %s" % finals[-1])

    for f in finals:
        d = common.probe_duration(f)
        size_mb = f.stat().st_size / 1e6
        print("DONE %s: %.1fs, %.1f MB" % (f.name, d, size_mb))


if __name__ == "__main__":
    main()
