"""Stage: score — make sure a real score sits in the slot, then record it.

The score slot is `outputs/music/score_final.wav`. Two honest ways to fill it:

  1. a chosen music-model take — run the ACE-Step worker on Kaggle
     (`kaggle/README.md`), copy the winner to `score_final.wav` and write its
     source into `outputs/music/score_source.txt`. `make music` handles that
     path and refuses to guess between candidates;
  2. the deterministic qenet bed (`tools/make_qenet_bed.py`): an original
     Ethiopian-pentatonic cue synthesised by code from the current film.json —
     no model, no quota, the same output every run.

This stage is what the one command (`make short`) runs: if a score is already
chosen it is kept; if the slot is empty it builds the qenet bed, so the film is
never silent and never uses a placeholder. It then runs the music stage so the
choice is logged in runs.jsonl and the Kaggle manifest is refreshed.
"""
import subprocess
import sys

from pipeline import common

SCORE = common.OUT / "music" / "score_final.wav"


def main():
    common.load_storyboard()  # the contract is validated before anything runs
    if not (SCORE.exists() and common.probe_duration(SCORE)):
        print("score: no chosen score in outputs/music/ — building the "
              "deterministic qenet bed (tools/make_qenet_bed.py)")
        r = subprocess.run([sys.executable, "tools/make_qenet_bed.py"],
                           cwd=str(common.ROOT))
        if r.returncode != 0 or not SCORE.exists():
            sys.exit("score: could not build the qenet bed (exit %d)" % r.returncode)
    else:
        src = common.OUT / "music" / "score_source.txt"
        print("score: keeping the chosen score_final.wav (source %s)"
              % (src.read_text().strip() if src.exists() else "unrecorded"))
    from pipeline import music
    music.main()


if __name__ == "__main__":
    main()
