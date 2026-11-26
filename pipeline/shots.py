"""Stage: shots — real Wan 2.2 clips only (generated on Kaggle, no GPU here).

This stage does not call a model from this machine. It:
  1. writes kaggle/manifest_shots.json for the Kaggle worker,
  2. requires a valid outputs/shots/<id>.mp4 for EVERY shot — a missing or
     undecodable clip stops the stage with instructions (no Ken Burns
     fallback exists any more),
  3. writes outputs/shots/plan.json (all shots are mode "clip").

Workflow: run this -> upload outputs/keyframes + the manifest to Kaggle (see
kaggle/README.md) -> run the worker notebook -> drop the resulting mp4s into
outputs/shots/ -> rerun this stage.
"""
import json
import sys

from pipeline import common


def main():
    sb = common.load_storyboard()
    shots_dir = common.stage_dir("shots")

    manifest = {
        "model": "Wan-AI/Wan2.2-TI2V-5B-Diffusers",
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

    missing = []
    plan = {}
    for s in sb["shots"]:
        clip = shots_dir / ("%s.mp4" % s["id"])
        d = common.probe_duration(clip) if clip.exists() else None
        if not d:
            missing.append(s["id"])
            continue
        plan[s["id"]] = {"mode": "clip", "path": str(clip.relative_to(common.ROOT)),
                         "duration_s": d}
        common.log_call(stage="shots", model="wan2.2-ti2v-5b", seed=s.get("seed"),
                        params={"shot": s["id"], "duration_s": d},
                        status="ok", output=str(clip), note="clip present")
    (shots_dir / "plan.json").write_text(json.dumps(plan, indent=1))

    print("kaggle manifest written -> %s" % mf_path)
    if missing:
        sys.exit(
            "shots: %d/%d clips missing or unreadable: %s\n"
            "the pipeline is real-only — no still-image fallback exists.\n"
            "generate them on Kaggle: kaggle/README.md (Wan 2.2 TI2V-5B, free T4;\n"
            "upload the manifest + outputs/keyframes/, run the worker, drop the\n"
            "mp4s into outputs/shots/ named <shot_id>.mp4) or import clips from\n"
            "any generator: python3 tools/import_clips.py <folder> --model <name>"
            % (len(sb["shots"]) - len(missing), len(sb["shots"]), ", ".join(missing)))
    print("shots: %d/%d real clips present -> %s"
          % (len(plan), len(sb["shots"]), shots_dir / "plan.json"))


if __name__ == "__main__":
    main()
