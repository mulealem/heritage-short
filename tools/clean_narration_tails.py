"""Remove the terminal noise burst Gemini TTS leaves on every narration line.

Run once on existing WAVs, or rely on `pipeline.narration` doing it inline for
new recordings. Updates the cache sidecar's duration and durations.json, then
the film can be rebuilt/re-rendered.

Usage: python3 tools/clean_narration_tails.py [--dry-run]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common, narration

NARR = common.OUT / "narration"


def main():
    dry = "--dry-run" in sys.argv
    files = sorted(NARR.glob("s*.wav"))
    if not files:
        sys.exit("no narration files — run: make narration")
    changed = 0
    for f in files:
        before = common.probe_duration(f)
        if dry:
            print("  %-22s %.2fs (dry run)" % (f.name, before or 0))
            continue
        trimmed = narration.trim_terminal_burst(f)
        after = common.probe_duration(f)
        if trimmed:
            changed += 1
            meta = f.with_suffix(".json")
            if meta.exists():
                doc = json.loads(meta.read_text())
                doc.setdefault("extra", {})["seconds"] = after
                meta.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
            common.log_call(stage="narration", model="ffmpeg", status="ok",
                            params={"shot": f.stem, "before": round(before or 0, 3),
                                    "after": round(after or 0, 3)},
                            output=str(f), note="trim terminal TTS burst")
            print("  %-22s %.2fs -> %.2fs (burst removed)"
                  % (f.name, before or 0, after or 0))
        else:
            print("  %-22s %.2fs (no burst found)" % (f.name, before or 0))

    durations = {}
    for f in files:
        durations[f.stem] = common.probe_duration(f)
    (NARR / "durations.json").write_text(
        json.dumps(durations, indent=1, sort_keys=True) + "\n")
    print("durations.json refreshed; %d file(s) cleaned, total %.2fs"
          % (changed, sum(durations.values())))


if __name__ == "__main__":
    main()
