"""Kaggle worker: Wan 2.2 TI2V-5B image-to-video for every shot.

Runs on Kaggle GPU (T4 x2 session, one T4 is enough). Reads
/kaggle/working/manifest_shots.json (written by `make shots`) and the
keyframes you uploaded, writes one mp4 per shot into /kaggle/working/shotclips/
and appends one JSON line per shot to /kaggle/working/kaggle_runs.jsonl.

Verified against the diffusers Wan docs (v0.43) and the Wan2.2 model card:
  - repo id must be the -Diffusers variant,
  - VAE loads in float32 (better decode quality),
  - the keyframe is resized to the model's 704x1280 budget with dims rounded
    to the VAE/patch modulus,
  - num_frames is 4n+1 (121 = 5 s at the model's native 24 fps),
  - guidance_scale 5.0.
T4 note: Turing has no bf16 support, so the dtype is picked from the GPU
( bf16 on Ampere+, fp16 elsewhere ). If fp16 clips show flicker or NaN
artifacts, record it in FAILURES.md and switch to a P100/other GPU.

Resume-safe: shots whose output mp4 already exists are skipped, so a timed-out
session only needs a rerun, not a restart.
"""
import json
import os
import time

import numpy as np
import torch
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
from diffusers.utils import export_to_video, load_image

MANIFEST = "/kaggle/working/manifest_shots.json"
KEYFRAMES = "/kaggle/working/keyframes"
OUTDIR = "/kaggle/working/shotclips"
RUNS = "/kaggle/working/kaggle_runs.jsonl"

# Wan 2.2's standard negative prompt (ignored by the model when CFG is off).
NEGATIVE = ("Bright tones, overexposed, static, blurred details, subtitles, style, "
            "works, paintings, images, overall gray, worst quality, low quality, "
            "JPEG compression residue, ugly, incomplete, extra fingers, poorly drawn "
            "hands, poorly drawn faces, deformed, disfigured, misshapen limbs, "
            "fused fingers, still picture, messy background, three legs, many people "
            "in the background, walking backwards")


def log(rec):
    with open(RUNS, "a") as f:
        f.write(json.dumps(rec) + "\n")


def aspect_ratio_resize(image, pipe, max_area=704 * 1280):
    """Resize to the TI2V-5B pixel budget, dims rounded to the VAE modulus."""
    aspect = image.height / image.width
    mod = pipe.vae_scale_factor_spatial * pipe.transformer.config.patch_size[1]
    height = round(np.sqrt(max_area * aspect)) // mod * mod
    width = round(np.sqrt(max_area / aspect)) // mod * mod
    return image.resize((width, height)), height, width


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    manifest = json.load(open(MANIFEST))

    model_id = manifest["model"]
    cap = torch.cuda.get_device_capability()
    dtype = torch.bfloat16 if cap >= (8, 0) else torch.float16
    print("gpu capability %s -> dtype %s" % (cap, dtype))

    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae",
                                           torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(model_id, vae=vae,
                                                   torch_dtype=dtype)
    pipe.enable_model_cpu_offload()  # 16 GB T4: offload keeps headroom

    for shot in manifest["shots"]:
        out_path = "%s/%s.mp4" % (OUTDIR, shot["id"])
        if os.path.exists(out_path):  # resume after a session timeout
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "stage": "shots", "model": model_id, "shot": shot["id"],
                   "seed": shot["seed"], "status": "cache",
                   "note": "clip already present; skipped"}
            log(rec)
            print(rec)
            continue
        t0 = time.time()
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "stage": "shots", "model": model_id,
               "shot": shot["id"], "seed": shot["seed"], "status": "started"}
        log(rec)
        try:
            image = load_image("%s/%s.png" % (KEYFRAMES, shot["id"])).convert("RGB")
            image, height, width = aspect_ratio_resize(image, pipe)
            frames = int(shot["seconds"] * manifest["fps"]) // 4 * 4 + 1  # 4n+1
            generator = torch.Generator(device="cuda").manual_seed(shot["seed"])
            out = pipe(
                image=image,
                prompt=shot["prompt"],
                negative_prompt=NEGATIVE,
                height=height,
                width=width,
                num_frames=min(frames, 121),      # model caps at 121 frames (5 s @ 24 fps)
                guidance_scale=5.0,
                num_inference_steps=30,           # quality knob for experiments
                generator=generator,
            ).frames[0]
            export_to_video(out, out_path, fps=manifest["fps"])
            rec.update(status="ok", latency_s=round(time.time() - t0, 1),
                       output="shotclips/%s.mp4" % shot["id"])
        except Exception as e:  # keep going — save-as-you-go on quota-limited GPUs
            rec.update(status="error", note=str(e)[:300], latency_s=round(time.time() - t0, 1))
        log(rec)
        print(rec)


if __name__ == "__main__":
    main()
