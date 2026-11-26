"""One command: storyboard.json -> both films. `make short`.

This is the command the README leads with. It chains the stages that made the
submitted film, in dependency order:

    validate -> narration -> cast -> keyframes -> panels -> comic build
             -> score -> comic render (9:16) -> comic render (16:9)

Guarantees, all visible in runs.jsonl:
  - every stage validates storyboard.json against schema/ before it runs
    (pipeline.common.load_storyboard), so a broken contract stops everything;
  - content-hash caching: an unchanged line, image or panel is a cache hit and
    costs nothing — change one prompt and exactly one model call is made;
  - real only: a stage that is missing an input stops with instructions,
    it never writes a placeholder;
  - keys are requested only for an asset that is not cached, so a clone that
    carries outputs/ rebuilds both films with no credentials at all.

The vertical and horizontal films share one timeline and one audio master; the
renderer is compiled once per layout (cargo feature `wide`).
"""
import json
import subprocess
import sys

from pipeline import common

STAGES = [
    ("validate", ["-m", "pipeline.validate_sb"]),
    ("narration", ["-m", "pipeline.narration"]),
    ("cast", ["tools/comic_cast.py"]),
    ("keyframes", ["-m", "pipeline.keyframes"]),
    ("panels", ["tools/comic_panels.py"]),
    ("comic build", ["-m", "pipeline.comic", "build"]),
    ("score", ["-m", "pipeline.score"]),
    ("comic render 9:16", ["-m", "pipeline.comic", "render"]),
    ("comic render 16:9", ["-m", "pipeline.comic", "render-wide"]),
]
FREE_TOOLS = ("ffmpeg", "fframes", "jsonschema", "qenet-bed", "ffmpeg-atempo")


def run_stage(name, args):
    print("\n=== %s ===" % name, flush=True)
    r = subprocess.run([sys.executable] + args, cwd=str(common.ROOT))
    if r.returncode != 0:
        sys.exit("\n`make short` stopped at stage '%s' (exit %d). Fix what it "
                 "printed and rerun: finished work is cached." % (name, r.returncode))


def summarize(log_before):
    """What this run cost, read back from the lines it appended to runs.jsonl."""
    calls, cache, errors, cost = [], 0, 0, 0.0
    with open(common.RUNS_LOG) as fh:
        lines = fh.readlines()[log_before:]
    for line in lines:
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("status") == "cache":
            cache += 1
        elif rec.get("status") == "error":
            errors += 1
        elif rec.get("latency_ms") is not None and not str(rec.get("model", "")).startswith(FREE_TOOLS) \
                and rec.get("stage") != "validate":
            calls.append(rec)
            cost += rec.get("cost_usd_est") or 0.0
    print("\n=== done ===")
    films = [common.OUT / "film_9x16.mp4", common.OUT / "film_16x9.mp4"]
    for f in films:
        if f.exists():
            d = common.probe_duration(f)
            print("  %-24s %.1fs  %.1f MB" % (f.name, d or 0, f.stat().st_size / 1e6))
        else:
            print("  %-24s missing" % f.name)
    print("this run: %d real model call(s) (~$%.4f list price), %d cache hit(s), %d error(s)"
          % (len(calls), cost, cache, errors))
    for rec in calls:
        print("  + %-10s %-30s %s" % (rec.get("stage"), rec.get("model"),
                                      (rec.get("params") or {}).get("label")
                                      or (rec.get("params") or {}).get("shot")
                                      or (rec.get("params") or {}).get("file") or ""))
    if not calls:
        print("  (everything was cached: the films were rebuilt from the committed assets)")


def main():
    before = sum(1 for _ in open(common.RUNS_LOG)) if common.RUNS_LOG.exists() else 0
    print("heritage-short: storyboard.json -> film_9x16.mp4 + film_16x9.mp4 (real only)")
    for name, args in STAGES:
        run_stage(name, args)
    summarize(before)


if __name__ == "__main__":
    main()
