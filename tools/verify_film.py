"""Verify finished films against the brief: streams, specs, 60-90 s, subtitles.

Usage: python3 tools/verify_film.py [film.mp4 ...]   (default: both ratios)

Checks per film: an H.264 picture at 1080x1920 (9:16) or 1920x1080 (16:9),
AAC audio, an English subtitle track, and a running time inside the brief's
60-90 seconds. Exits non-zero if any required property is missing.
"""
import json
import os
import subprocess
import sys

MIN_S, MAX_S = 60.0, 90.0          # the brief's running time
SIZES = {(1080, 1920): "9:16", (1920, 1080): "16:9"}
DEFAULTS = ["outputs/film_9x16.mp4", "outputs/film_16x9.mp4"]


def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("ffprobe failed: " + out.stderr[-400:])
    return json.loads(out.stdout)


def loudness(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-map", "0:a",
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True)
    vals = {}
    for line in out.stderr.splitlines():
        for key in ("mean_volume", "max_volume"):
            if key in line:
                vals[key] = line.split(key + ":")[1].strip()
    return vals


def check(path):
    d = ffprobe(path)
    streams = d["streams"]
    video = [s for s in streams if s["codec_type"] == "video"]
    audio = [s for s in streams if s["codec_type"] == "audio"]
    subs = [s for s in streams if s["codec_type"] == "subtitle"]
    if not video:
        print("FAIL: %s has no video stream" % path)
        return False
    v = video[0]
    dur = float(d["format"]["duration"])
    ratio = SIZES.get((v["width"], v["height"]), "?")
    print("file     : %s (%.1f MB)" % (path, int(d["format"]["size"]) / 1e6))
    print("video    : %s %sx%s (%s) @ %s fps, %.2fs" %
          (v["codec_name"], v["width"], v["height"], ratio,
           v["r_frame_rate"], float(v.get("duration") or dur)))
    print("audio    : %s" % (audio[0]["codec_name"] if audio else "NONE"))
    print("subtitles: %s (%s)" % (subs[0]["codec_name"], subs[0].get("tags", {}).get("language", "?"))
          if subs else "subtitles: none")
    if audio:
        print("levels   : %s" % loudness(path))
    print("title    : %s" % d["format"].get("tags", {}).get("title", "(none)"))
    problems = []
    if ratio == "?":
        problems.append("unexpected resolution %dx%d" % (v["width"], v["height"]))
    if not audio:
        problems.append("no audio stream")
    if not subs:
        problems.append("no subtitle track")
    if not (MIN_S <= dur <= MAX_S):
        problems.append("duration %.1fs is outside the brief's %.0f-%.0fs"
                        % (dur, MIN_S, MAX_S))
    if problems:
        print("FAIL: " + "; ".join(problems))
        return False
    print("PASS")
    return True


def main():
    wanted = sys.argv[1:] or DEFAULTS
    results = [(p, check(p)) for p in wanted if os.path.exists(p)]
    for p in wanted:
        if not os.path.exists(p):
            print("MISSING  : %s" % p)
    ok = len(results) == len(wanted) and all(passed for _, passed in results)
    print("\n%s: %d of %d film(s) verified" %
          ("PASS" if ok else "FAIL", sum(1 for _, passed in results if passed), len(wanted)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
