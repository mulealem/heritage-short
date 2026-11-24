"""Stage: shots — moving shots via Wan 2.2 on Kaggle, with local Ken Burns fallback.

This stage does not call a model from this machine (no GPU here). It:
  1. writes kaggle/manifest_shots.json for the Kaggle worker,
  2. checks which clips exist in outputs/shots/<id>.mp4,
  3. writes outputs/shots/plan.json telling assemble which shots use real clips
     and which get the Ken Burns pan-and-zoom fallback (per the brief, a
     narrated, scored, subtitled sequence of stills is still a film).

Workflow: run this -> upload outputs/keyframes + manifest to Kaggle (see
kaggle/README.md) -> run the worker notebook -> drop resulting mp4s into
outputs/shots/ -> rerun this stage.
"""
import json
import sys
from pathlib import Path

from pipeline import common


def main():
    sb = common.load_storyboard()
    shots_dir = common.stage_dir("shots")

    manifest = {
        "model": "Wan-AI/Wan2.2-TI2V-5B",
        "fps": 24,
        "resolution": 720,
        "shots": [
            {
                "id": s["id"],
                "image": "keyframes/%s.png" % s["id"],
                "prompt": s["motion_prompt"],
                "seconds": min(5.0, s["duration_s"]),
                "seed": int(s.get("seed", 0)),
            }
            for s in sb["shots"]
        ],
    }
    mf_path = common.ROOT / "kaggle" / "manifest_shots.json"
    mf_path.parent.mkdir(exist_ok=True)
    mf_path.write_text(json.dumps(manifest, indent=1))

    plan = {}
    have_clips = 0
    for s in sb["shots"]:
        clip = shots_dir / ("%s.mp4" % s["id"])
        if clip.exists() and common.probe_duration(clip):
            d = common.probe_duration(clip)
            plan[s["id"]] = {"mode": "clip", "path": str(clip.relative_to(common.ROOT)),
                             "duration_s": d}
            have_clips += 1
            common.log_call(stage="shots", model="wan2.2-ti2v-5b", seed=s.get("seed"),
                            params={"shot": s["id"], "duration_s": d},
                            status="cache" if s.get("_logged") else "ok",
                            output=str(clip), note="clip present")
        else:
            plan[s["id"]] = {"mode": "kenburns", "path": "outputs/keyframes/%s.png" % s["id"],
                             "duration_s": s["duration_s"]}
            common.log_call(stage="shots", model="kenburns-fallback",
                            params={"shot": s["id"], "duration_s": s["duration_s"]},
                            status="skip", note="no clip yet; Ken Burns fallback")
    (shots_dir / "plan.json").write_text(json.dumps(plan, indent=1))

    print("shots: %d/%d clips present; %d will use Ken Burns fallback"
          % (have_clips, len(sb["shots"]), len(sb["shots"]) - have_clips))
    print("kaggle manifest written -> %s" % mf_path)
    if have_clips < len(sb["shots"]):
        print("to generate real clips: see kaggle/README.md (Wan 2.2 on a free T4)")


if __name__ == "__main__":
    main()
