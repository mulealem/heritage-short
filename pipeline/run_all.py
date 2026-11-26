"""One-command run: validate -> narration -> keyframes -> shots -> music -> assemble.

Real only. A preflight checks API keys before anything runs; each stage then
hard-fails with instructions if its inputs are missing. Note the bootstrap
order on a fresh project: narration + keyframes (hosted APIs) come first —
their outputs are what you upload to Kaggle to produce the clips and the
score that the shots/music stages require. Rerun `make film` after each
Kaggle round-trip; finished work is cache-hit and costs nothing.
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
