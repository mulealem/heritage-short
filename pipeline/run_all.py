"""The video-clip route (`make film`): validate -> narration -> keyframes ->
shots -> music -> assemble.

This is NOT the command that made the submitted film — that is `make short`
(pipeline/short.py), the motion-comic route. This one uses real moving shots
from Wan 2.2 on Kaggle, so it needs the Kaggle round-trip: narration and
keyframes (hosted APIs) come first, their outputs are uploaded to Kaggle, and
the shots/music stages stop with instructions until the clips and a chosen
score are in outputs/. Rerun after each round-trip; finished work is
cache-hit and costs nothing. Real only, and untested end to end (no Wan clip
was ever produced — FAILURES.md F6).
"""
import sys

from pipeline import common

KEYS = [
    ("GEMINI_API_KEY", "narration/script — free key: https://aistudio.google.com/apikey"),
    ("CF_ACCOUNT_ID", "keyframes — your Cloudflare account id (dash.cloudflare.com)"),
    ("CF_API_TOKEN", "keyframes — Cloudflare Workers AI token"),
]


def preflight():
    print("=== heritage-short pipeline, run %s (real only) ===" % common.RUN_ID)
    missing = [(k, hint) for k, hint in KEYS if not common.has_key(k)]
    if missing:
        print("missing API keys in .env:")
        for k, hint in missing:
            print("  %s — %s" % (k, hint))
        sys.exit("copy .env.example to .env and fill in every key above")

    clips = sorted((common.OUT / "shots").glob("*.mp4")) if (common.OUT / "shots").exists() else []
    score = common.OUT / "music" / "score_final.wav"
    print("keys: ok (gemini, cloudflare)")
    print("kaggle artifacts: %d/8 clips, score %s"
          % (len(clips), "ready" if score.exists() else "missing"))
    if len(clips) < 8 or not score.exists():
        print("(stages needing them will stop with instructions — expected on a "
              "first run; narration+keyframes come first because the Kaggle "
              "workers consume their outputs)")


def main():
    stages = [
        ("validate", "pipeline.validate_sb"),
        ("narration", "pipeline.narration"),
        ("keyframes", "pipeline.keyframes"),
        ("shots", "pipeline.shots"),
        ("music", "pipeline.music"),
        ("assemble", "pipeline.assemble"),
    ]
    preflight()

    for name, module in stages:
        print("\n--- %s ---" % name)
        mod = __import__(module, fromlist=["main"])
        mod.main()

    print("\n=== done ===")
    print("films: outputs/film_9x16.mp4, outputs/film_16x9.mp4")
    print("logs : runs.jsonl (%d calls this run)" % sum(
        1 for _ in open(common.RUNS_LOG)))


if __name__ == "__main__":
    main()
