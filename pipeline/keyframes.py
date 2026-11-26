"""Stage: keyframes — character/style sheet first, then one still per shot.

Real only: Cloudflare Workers AI FLUX (needs CF_ACCOUNT_ID + CF_API_TOKEN).
The FLUX-2 klein family accepts multipart form-data only and honours
width/height/seed (verified against the live API, Nov 2026); the older
flux-1-schnell route took a JSON body but dropped width/height/seed.
A failed call (after net.py's retries) stops the stage — no placeholder
image is ever written.

Note: klein returns JPEG bytes; consumers (ffmpeg, PIL) sniff content, the
.png filenames are just the pipeline contract.

Output: outputs/keyframes/character_sheet.png and outputs/keyframes/<id>.png
"""
import base64
import json
import sys
import time

from pipeline import common, net

ASPECT = {"9:16": "9:16", "16:9": "16:9"}

from pipeline.prompting import directive_for  # noqa: E402


def cf_flux(prompt, width, height, seed, steps=4):
    acct = common.env_key("CF_ACCOUNT_ID")
    token = common.env_key("CF_API_TOKEN")
    model = common.env_key("CF_FLUX_MODEL") or "@cf/black-forest-labs/flux-2-klein-4b"
    url = "https://api.cloudflare.com/client/v4/accounts/%s/ai/run/%s" % (acct, model)
    auth = {"Authorization": "Bearer " + token}
    if model.startswith("@cf/black-forest-labs/flux-2"):
        body, _, ms = net.http_multipart(
            url, {"prompt": prompt, "steps": steps, "width": width,
                  "height": height, "seed": seed}, headers=auth, timeout=300)
    else:
        payload = {"prompt": prompt, "steps": steps, "width": width,
                   "height": height, "seed": seed}
        body, _, ms = net.http_json(url, payload, headers=auth, timeout=300)
    if not body.get("success"):
        raise RuntimeError("Cloudflare error: %s" % json.dumps(body.get("errors", body))[:300])
    img_b64 = body.get("result", {}).get("image")
    if not img_b64:
        raise RuntimeError("no image in response: %s" % json.dumps(body)[:300])
    return base64.b64decode(img_b64), model, ms


def cache_get(path, key):
    meta = path.with_suffix(".json")
    return path.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key


def cache_put(path, key):
    path.with_suffix(".json").write_text(json.dumps({"key": key}))


def main():
    sb = common.load_storyboard()
    meta = sb["meta"]
    W, H = int(meta["image_width"]), int(meta["image_height"])
    out_dir = common.stage_dir("keyframes")
    provider = common.image_provider()
    actors = {}
    panels_file = common.ROOT / "comic" / "panels.json"
    if panels_file.exists():
        actors = {sid: spec.get("actor") for sid, spec in
                  json.loads(panels_file.read_text()).get("shots", {}).items()}

    def need_keys():
        """Only when an image is really (re)drawn — a clone with the cache
        committed rebuilds the film with no credentials at all."""
        if provider == "minimax":
            common.require_key("MINIMAX_API_KEY", "MiniMax API platform key")
        else:
            common.require_key("CF_ACCOUNT_ID",
                               "your Cloudflare account id (dash.cloudflare.com, Workers AI)")
            common.require_key("CF_API_TOKEN",
                               "create a Workers AI token in the Cloudflare dashboard")

    jobs = [("character_sheet", 0, None,
             meta["style_block"] + " — " + sb["character_sheet"]["prompt"])]
    for shot in sb["shots"]:
        jobs.append((shot["id"], int(shot.get("seed", 0)), actors.get(shot["id"]),
                     meta["style_block"] + " — " + shot["image_prompt"]))

    for label, seed, actor, prompt in jobs:
        out_path = out_dir / ("%s.png" % label)
        ref_tag = actor or "-"
        # the identity directive is sent only with a reference portrait, and
        # only the MiniMax path takes one; the key hashes exactly what is sent
        full = prompt + (directive_for(actor) if provider == "minimax" else "")
        key = common.hash_key(provider, ref_tag, common.image_cache_model(provider),
                              full, W, H, seed, "flux-v6")
        if cache_get(out_path, key):
            common.log_call(stage="keyframes", model="flux", seed=seed,
                            params={"label": label, "w": W, "h": H},
                            status="cache", output=str(out_path), note="cache hit")
            print("  %s: cache hit" % label)
            continue
        need_keys()
        t0 = time.time()
        model = common.env_key("CF_FLUX_MODEL") or "@cf/black-forest-labs/flux-2-klein-4b"
        try:
            if provider == "minimax":
                # the sheet is a landscape page; panels are vertical
                ratio = "3:2" if label == "character_sheet" else \
                    ASPECT.get(meta["aspect_ratios"][0], "9:16")
                ref = None
                actor = actors.get(label)
                if actor:
                    ref = common.OUT / "character_refs" / ("%s.jpg" % actor)
                    if not ref.exists():
                        sys.exit("missing cast reference %s — run: python3 tools/comic_cast.py"
                                 % ref)
                full = prompt + directive_for(actor)
                png, model, _ms = minimax_image(full, ratio, ref_path=ref)
            else:
                png, model, _ms = cf_flux(prompt, W, H, seed)
        except RuntimeError as e:
            common.log_call(stage="keyframes", model=model, seed=seed, status="error",
                            params={"label": label}, note=str(e))
            sys.exit("FLUX failed for %s: %s\nfix the token/quota in .env and rerun "
                     "(done images are cache hits, you will not pay twice)"
                     % (label, e))
        out_path.write_bytes(png)
        cache_put(out_path, key)
        cost = common.est_cost("minimax-image-01-per-image" if provider == "minimax"
                               else "flux-klein-4b-per-image", 1)
        common.log_call(stage="keyframes", model=model, seed=seed,
                        latency_ms=int((time.time() - t0) * 1000),
                        params={"label": label, "w": W, "h": H, "steps": 4},
                        status="ok", output=str(out_path), cost_usd_est=cost)
        print("  %s: ok" % label)

    print("keyframes done -> %s" % out_dir)


if __name__ == "__main__":
    main()
