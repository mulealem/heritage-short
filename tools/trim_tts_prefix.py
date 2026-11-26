"""Trim the spoken style-instruction prefix out of TTS narration files.

Cause: narration.py used to send `style:
text` to Gemini TTS; a bare descriptive
phrase ("a warm Amharic folk storyteller ...") is read aloud as if it were part
of the line. Every file therefore starts with ~6-7 s of English before the
actual narration.

This tool cuts each WAV at the first long silence (>=0.5 s at -35 dB, within the
first 10 s) and keeps the rest. It refuses to cut if no such pause is found or
if the remaining audio would be implausibly short. Every edit is logged.

Usage: python3 tools/trim_tts_prefix.py [--dry-run]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common

NARR = common.OUT / "narration"
MAX_PREFIX = 10.0     # only consider a prefix pause inside the first 10 s
MIN_LEFT = 3.0        # refuse to leave less than this


def first_long_silence_end(path):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-af",
         "silencedetect=noise=-35dB:d=0.5", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    for m in re.finditer(r"silence_end: ([\d.]+)", out):
        end = float(m.group(1))
        if end <= MAX_PREFIX:
            return end
        break
    return None


def main():
    dry = "--dry-run" in sys.argv
    files = sorted(NARR.glob("s*.wav"))
    if not files:
        sys.exit("no narration files — run: make narration")
    for f in files:
        dur = common.probe_duration(f)
        cut = first_long_silence_end(f)
        if cut is None:
            print("  %-24s no prefix pause found; left as is" % f.name)
            continue
        left = dur - cut
        if left < MIN_LEFT:
            print("  %-24s pause at %.2f leaves %.2fs — refusing" % (f.name, cut, left))
            continue
        print("  %-24s %.2fs -> cut at %.2f -> %.2fs" % (f.name, dur, cut, left))
        if dry:
            continue
        tmp = f.with_suffix(".trim.wav")
        common.run_ffmpeg(["-i", str(f), "-ss", "%.3f" % cut,
                           "-c:a", "pcm_s16le", str(tmp)],
                          stage="narration", note="trim spoken style prefix")
        tmp.replace(f)
    if dry:
        print("(dry run — nothing written)")
    else:
        print("done; now refresh durations: make narration (all cache hits)")


if __name__ == "__main__":
    main()
