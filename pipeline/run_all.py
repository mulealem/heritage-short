"""One-command run: validate -> narration -> keyframes -> shots -> music -> assemble.

Usage:
    python3 -m pipeline.run_all            # real mode where keys exist, mock elsewhere
    FORCE_MOCK=1 python3 -m pipeline.run_all   # fully offline
"""
import sys

from pipeline import common


def main():
    stages = [
        ("validate", "pipeline.validate_sb"),
        ("narration", "pipeline.narration"),
        ("keyframes", "pipeline.keyframes"),
        ("shots", "pipeline.shots"),
        ("music", "pipeline.music"),
        ("assemble", "pipeline.assemble"),
    ]
    print("=== heritage-short pipeline, run %s ===" % common.RUN_ID)
    if common.force_mock():
        print("mode: FORCE MOCK (no network model calls)")
    else:
        have = {
            "gemini(tts/script)": common.has_key("GEMINI_API_KEY"),
            "cloudflare(keyframes)": common.has_key("CF_ACCOUNT_ID") and common.has_key("CF_API_TOKEN"),
        }
        print("mode: " + ", ".join("%s=%s" % (k, "real" if v else "MOCK") for k, v in have.items()))
        print("wan2.2 clips: picked up from outputs/shots/ when present (Kaggle)")

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
