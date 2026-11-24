"""Kaggle/Colab worker: ACE-Step 1.5 score candidates from the music manifest.

Reads kaggle/manifest_music.json, generates N candidates (different seeds),
saves candidate_<seed>.mp3 + kaggle_runs.jsonl.

NOTE: written against the ACE-Step usage pattern; if the API moved, check the
current repo README (https://github.com/ACE-Step/ACE-Step-1.5) and record what
changed in FAILURES.md.
"""
import json
import time

MANIFEST = "manifest_music.json"


def log(rec):
    with open("kaggle_runs.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    from acestep.pipeline import AceStepPipeline  # verify import path against the repo
    m = json.load(open(MANIFEST))
    pipe = AceStepPipeline()
    for seed in m["seeds"]:
        t0 = time.time()
        rec = {"stage": "music", "model": "ace-step-1.5", "seed": seed, "status": "started"}
        log(rec)
        try:
            pipe(
                caption=m["caption"],
                lyrics="" if m["instrumental"] else m.get("lyrics", "[inst]"),
                duration_seconds=m["seconds"],
                bpm=m["bpm"],
                key=m["key"],
                seed=seed,
                output_path=f"candidate_{seed}.mp3",
            )
            rec.update(status="ok", latency_s=round(time.time() - t0, 1),
                       output=f"candidate_{seed}.mp3")
        except Exception as e:
            rec.update(status="error", note=str(e)[:300])
        log(rec)
        print(rec)


if __name__ == "__main__":
    main()
