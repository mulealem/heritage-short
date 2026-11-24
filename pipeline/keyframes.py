"""Stage: keyframes — character/style sheet first, then one still per shot.

Real mode: Cloudflare Workers AI FLUX (needs CF_ACCOUNT_ID + CF_API_TOKEN).
Mock mode: deterministic ffmpeg placeholders with the shot id burned in.

Output: outputs/keyframes/character_sheet.png and outputs/keyframes/<id>.png
"""
import base64
import json
import sys
import time
from pathlib import Path

from pipeline import common, net


def cf_flux(prompt, width, height, seed, steps=4):
    acct = common.env_key("CF_ACCOUNT_ID")
    token = common.env_key("CF_API_TOKEN")
    model = common.env_key("CF_FLUX_MODEL") or "@cf/black-forest-labs/flux-schnell"
    url = "https://api.cloudflare.com/client/v4/accounts/%s/ai/run/%s" % (acct, model)
    payload = {"prompt": prompt, "steps": steps, "width": width, "height": height, "seed": seed}
    body, _, ms = net.http_json(url, payload,
                                headers={"Authorization": "Bearer " + token}, timeout=300)
    if not body.get("success"):
        raise RuntimeError("Cloudflare error: %s" % json.dumps(body.get("errors", body))[:300])
    img_b64 = body.get("result", {}).get("image")
    if not img_b64:
        raise RuntimeError("no image in response: %s" % json.dumps(body)[:300])
    return base64.b64decode(img_b64), model, ms


def mock_keyframe(out_path, width, height, label, sub, seed):
    """Deterministic gradient placeholder with text, via ffmpeg drawtext."""
    font = common.find_font()
    from pipeline.common import run_ffmpeg
    txt = (out_path.parent / ("%s.txt" % out_path.stem))
    txt.write_text(label, encoding="utf-8")
    vf = ["format=rgb24",
          "drawbox=x=iw/8:y=ih/8:w=iw*3/4:h=ih*3/4:color=white@0.15:t=6"]
    if font:
        vf.append("drawtext=fontfile=%s:textfile=%s:fontsize=h/14:fontcolor=white@0.9:"
                  "x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.35:boxborderw=12"
                  % (font, txt))
    if font and sub:
        vf.append("drawtext=fontfile=%s:text='%s':fontsize=h/34:fontcolor=white@0.8:"
                  "x=(w-text_w)/2:y=(h+text_h)/2+h/20" % (font, sub.replace("'", "").replace(":", "\\:")))
    run_ffmpeg(["-f", "lavfi", "-i", "color=c=0x2a1a12:s=%dx%d:d=0.1" % (width, height),
                "-vf", ",".join(vf), "-frames:v", "1", str(out_path)],
               stage="keyframes", note="mock placeholder %s" % label)
    txt.unlink()


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
    use_real = common.has_key("CF_ACCOUNT_ID") and common.has_key("CF_API_TOKEN") and not common.force_mock()

    if not use_real:
        why = "FORCE_MOCK=1" if common.force_mock() else "CF_ACCOUNT_ID/CF_API_TOKEN missing"
        print("keyframes: MOCK mode (%s) — placeholder images" % why)

    jobs = [("character_sheet", 0,
             meta["style_block"] + " — " + sb["character_sheet"]["prompt"],
             "CHARACTER / STYLE SHEET")]
    for shot in sb["shots"]:
        jobs.append((shot["id"], int(shot.get("seed", 0)),
                     meta["style_block"] + " — " + shot["image_prompt"],
                     "%s [%s]" % (shot["id"], shot["shot_size"])))

    for label, seed, prompt, sub in jobs:
        out_path = out_dir / ("%s.png" % label)
        key = common.hash_key("flux", prompt, W, H, seed)
        if cache_get(out_path, key):
            common.log_call(stage="keyframes", model="flux", seed=seed,
                            params={"label": label, "w": W, "h": H},
                            status="cache", output=str(out_path), note="cache hit")
            print("  %s: cache hit" % label)
            continue
        if use_real:
            t0 = time.time()
            try:
                png, model, ms = cf_flux(prompt, W, H, seed)
            except RuntimeError as e:
                common.log_call(stage="keyframes", model=model, seed=seed, status="error",
                                params={"label": label}, note=str(e))
                print("  ! FLUX failed for %s (%s); using mock placeholder" % (label, e))
                mock_keyframe(out_path, W, H, label, sub, seed)
                status = "mock"
            else:
                out_path.write_bytes(png)
                cost = common.est_cost("flux-schnell-per-image", 1)
                common.log_call(stage="keyframes", model=model, seed=seed, latency_ms=ms,
                                params={"label": label, "w": W, "h": H, "steps": 4},
                                status="ok", output=str(out_path), cost_usd_est=cost)
                status = "ok"
        else:
            mock_keyframe(out_path, W, H, label, sub, seed)
            status = "mock"
        cache_put(out_path, key)
        print("  %s: %s" % (label, status))

    print("keyframes done -> %s" % out_dir)


if __name__ == "__main__":
    main()
