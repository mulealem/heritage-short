"""Ingest video clips from ANY generator into the pipeline.

The shots stage' contract with assemble is just: outputs/shots/<shot_id>.mp4.
This tool validates, normalises the name, and logs whatever produced them —
so clips made by Veo, Runway, Kling, Hunyuan, or downloaded from any web UI
become first-class pipeline inputs with a runs.jsonl trail.

Usage:
    python3 tools/import_clips.py <folder-or-file>... [--model NAME]

Files may be named <shot_id>.mp4 (or .mov/.webm/.mkv); shot ids come from
storyboard.json. Afterwards run: make shots && make assemble
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common  # noqa: E402

EXTS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--model", default="external",
                    help="label written to runs.jsonl, e.g. veo-3, runway-gen4")
    args = ap.parse_args()

    sb = common.load_storyboard()
    ids = {s["id"]: s for s in sb["shots"]}
    shots_dir = common.stage_dir("shots")

    found = {}
    for p in args.paths:
        p = Path(p)
        it = p.iterdir() if p.is_dir() else [p]
        for f in it:
            if f.suffix.lower() in EXTS:
                found[f.stem] = f

    matched, unmatched = 0, []
    for stem, src in sorted(found.items()):
        if stem not in ids:
            unmatched.append(src.name)
            continue
        shot = ids[stem]
        dst = shots_dir / ("%s.mp4" % stem)
        dur = common.probe_duration(src)
        if not dur:
            print("! %s: not decodable, skipped" % src.name)
            continue
        shutil.copy(src, dst)
        short = " (SHORT: %.1fs < %.1fs shot — last-frame hold will pad it)" % (
            dur, shot["duration_s"]) if dur < shot["duration_s"] else ""
        common.log_call(stage="shots", model=args.model, seed=shot.get("seed"),
                        params={"shot": stem, "duration_s": round(dur, 2),
                                "imported_from": src.name},
                        status="ok", output=str(dst),
                        note="imported %s clip%s" % (args.model, short))
        print("  %s <- %s (%.1fs)%s" % (dst.name, src.name, dur, short))
        matched += 1

    if unmatched:
        print("\nnot matched to any shot id (check spelling): %s" % ", ".join(unmatched))
    print("\n%d/%d shots imported as %r. Now: make shots && make assemble"
          % (matched, len(ids), args.model))


if __name__ == "__main__":
    main()
