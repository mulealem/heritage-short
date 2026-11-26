"""Generate the comic panels cut into each beat (one or two per shot).

Reads the `extras` of comic/panels.json and draws
outputs/comic_panels/<shot_id>_xN.jpg with the configured image provider
(MiniMax image-01, or Cloudflare FLUX as the free draft path). The style
block from the storyboard is prepended, so the panels match the keyframes,
and a panel that names an actor is drawn with that character's portrait and
identity directive. Wide ensemble panels are left unanchored on purpose
(FAILURES.md F13). Cache sidecars make reruns free.

Usage: python3 tools/comic_panels.py [shot_id ...]
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common
from pipeline.prompting import compose

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "comic_panels"


def cache_get(path, key):
    meta = path.with_suffix(".json")
    return path.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key


def main():
    sb = common.load_storyboard()
    panels = json.loads((ROOT / "comic" / "panels.json").read_text())
    provider = common.image_provider()
    style = sb["meta"]["style_block"]
    OUT.mkdir(parents=True, exist_ok=True)

    wanted = sys.argv[1:] or [s["id"] for s in sb["shots"]]
    for shot_id in wanted:
        spec = panels["shots"].get(shot_id, {})
        jobs = []
        if spec.get("insert"):
            jobs.append(("%s.jpg" % shot_id, spec["insert"], spec.get("actor")))
        for i, ex in enumerate(spec.get("extras", []), 1):
            actor = ex["actor"] if "actor" in ex else spec.get("actor")
            jobs.append(("%s_x%d.jpg" % (shot_id, i), ex["prompt"], actor))
        if not jobs:
            print("  %s: no extra panels defined" % shot_id)
            continue
        for fname, prompt, actor in jobs:
            full = compose(style, prompt, actor)
            out = OUT / fname
            ref = common.OUT / "character_refs" / ("%s.jpg" % actor) if actor else None
            key = common.hash_key(provider, actor or "-", full, "9:16", "insert-v4")
            if cache_get(out, key):
                common.log_call(stage="panels", model="insert", status="cache",
                                params={"shot": shot_id, "file": fname},
                                output=str(out), note="cache hit")
                continue
            t0 = time.time()
            if provider == "minimax":
                from pipeline.minimax_image import minimax_image
                data, model, _ = minimax_image(full, "9:16", ref_path=ref)
            else:
                from pipeline.keyframes import cf_flux
                seed = int(common.hash_key(provider, actor or "-", prompt)[:8], 16) % 10000
                data, model, _ = cf_flux(full, 720, 1280, seed)
            out.write_bytes(data)
            (out.with_suffix(".json")).write_text(json.dumps({"key": key}))
            cost = common.est_cost("minimax-image-01-per-image" if provider == "minimax"
                                   else "flux-klein-4b-per-image", 1)
            common.log_call(stage="panels", model=model,
                            latency_ms=int((time.time() - t0) * 1000),
                            status="ok", params={"shot": shot_id, "file": fname},
                            output=str(out), cost_usd_est=cost, note="comic panel")
            print("  %s: ok" % fname)


if __name__ == "__main__":
    main()
