"""Stage: music — the real ACE-Step score, chosen from Kaggle candidates.

This stage does not call a model from this machine. It:
  1. writes kaggle/manifest_music.json for the Kaggle ACE-Step worker,
  2. requires a chosen score: outputs/music/score_final.wav. Candidates
     without a choice stop the stage (audition them first); no candidates at
     all stop the stage with the exact worker steps. No placeholder pad is
     ever generated.

Workflow: run this -> upload the manifest to Kaggle (kaggle/README.md) ->
run the worker -> download candidate_<seed>.mp3 into outputs/music/ ->
audition and copy the winner to score_final.wav -> rerun this stage.
"""
import json
import sys

from pipeline import common


def projected_total(sb):
    """Assembled film length, by the same arithmetic that assembles it.

    Uses the narration as edited for the cut (storyboard `meta.timing`) where it
    exists, and `assemble.build_timeline`, so the score is sized to the real
    film rather than to a second estimate.
    """
    from pipeline import assemble as asm
    from pipeline import narration as narr
    durations = json.loads((common.OUT / "narration" / "durations.json").read_text()) \
        if (common.OUT / "narration" / "durations.json").exists() else {}
    if not durations:
        return sum(s["duration_s"] for s in sb["shots"]) + float(sb["end_card"].get("seconds", 2.5))
    fitted = json.loads((common.OUT / "narration_fit" / "durations.json").read_text()) \
        if (common.OUT / "narration_fit" / "durations.json").exists() else durations
    _timed, total = asm.build_timeline(sb, fitted)
    return total


def main():
    sb = common.load_storyboard()
    mus = sb["music"]
    total = projected_total(sb)
    out_dir = common.stage_dir("music")

    # Manifest for the Kaggle ACE-Step worker.
    mf = {
        "caption": mus["caption"],
        "bpm": mus["bpm"],
        "key": mus["key"],
        "instrumental": mus.get("instrumental", True),
        "seconds": total,
        "candidates": mus.get("candidates", 3),
        "seeds": [int(mus.get("seed", 42)) + i for i in range(mus.get("candidates", 3))],
        "lyrics": mus.get("lyrics", ""),
    }
    mf_path = common.ROOT / "kaggle" / "manifest_music.json"
    mf_path.parent.mkdir(exist_ok=True)
    mf_path.write_text(json.dumps(mf, indent=1))
    basis = "the assembled timeline" if (common.OUT / "narration" / "durations.json").exists() \
        else "planned durations"
    print("music: manifest sized to %.1fs (%s)" % (total, basis))

    final = out_dir / "score_final.wav"
    candidates = sorted(out_dir.glob("candidate_*.mp3")) + sorted(out_dir.glob("candidate_*.wav"))

    if final.exists() and common.probe_duration(final):
        d = common.probe_duration(final)
        source = (out_dir / "score_source.txt").read_text().strip() \
            if (out_dir / "score_source.txt").exists() else "ace-step-1.5"
        if source.startswith("qenet-bed"):
            model = "qenet-bed"
            note = "chosen score_final.wav (hand-synthesized qenet bed, deterministic)"
        else:
            model = "ace-step-1.5"
            note = "score_final present (chosen on Kaggle)"
        common.log_call(stage="music", model=model, seed=None,
                        params={"mode": "chosen-final", "seconds": d, "source": source},
                        status="ok", output=str(final), note=note)
        print("music: using chosen score_final.wav (%.1fs, source %s)" % (d, source))
    elif candidates:
        sys.exit(
            "music: %d candidates found in %s but none chosen yet.\n"
            "audition them against the narration, then:\n"
            "  cp outputs/music/candidate_<seed>.mp3 outputs/music/score_final.wav\n"
            "and note WHY you picked it in EXPERIMENTS.md"
            % (len(candidates), out_dir))
    else:
        sys.exit(
            "music: no score in outputs/music/ — the pipeline is real-only, no\n"
            "placeholder pad exists. Generate the score on Kaggle (free GPU):\n"
            "  1. upload kaggle/manifest_music.json to a Kaggle notebook\n"
            "  2. paste kaggle/ace_step_worker.py as a cell and run it\n"
            "  3. download candidate_<seed>.mp3 into outputs/music/\n"
            "see kaggle/README.md for click-by-click steps")

    print("kaggle manifest written -> %s" % mf_path)


if __name__ == "__main__":
    main()
