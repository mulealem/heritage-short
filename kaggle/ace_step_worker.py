"""Kaggle worker: ACE-Step 1.5 score candidates from the music manifest.

Runs on Kaggle GPU (T4). Reads /kaggle/working/manifest_music.json (written by
`make music`), renders one candidate per seed into /kaggle/working/musiccand/
as candidate_<seed>.mp3, and appends one JSON line per candidate to
/kaggle/working/kaggle_runs.jsonl.

Verified against the ACE-Step 1.5 repo docs (INFERENCE.md +
GPU_COMPATIBILITY.md, Nov 2026): the 1.5 API is handler-based —
AceStepHandler + LLMHandler + generate_music() — NOT AceStepPipeline. bpm /
keyscale / timesignature are explicit call parameters. Instrumental tracks
use instrumental=True. Tier-5 (12-16 GB) settings: offload_to_cpu=True,
INT8 quantization (default), batch <= 4; vllm is fine on T4 (compute 7.5).

Setup (paste as a first notebook cell, one T4 session):
    !git clone https://github.com/ace-step/ACE-Step-1.5 /kaggle/working/ACE-Step-1.5
    %cd /kaggle/working/ACE-Step-1.5
    !pip install -e . && pip install vllm

Resume-safe: seeds whose candidate mp3 already exists are skipped.
"""
import glob
import json
import os
import shutil
import time

MANIFEST = "/kaggle/working/manifest_music.json"
PROJECT = "/kaggle/working/ACE-Step-1.5"
CHECKPOINTS = "/kaggle/working/checkpoints"
OUTDIR = "/kaggle/working/musiccand"
RUNS = "/kaggle/working/kaggle_runs.jsonl"


def log(rec):
    with open(RUNS, "a") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    from acestep.handler import AceStepHandler
    from acestep.llm_inference import LLMHandler
    from acestep.inference import GenerationParams, GenerationConfig, generate_music

    m = json.load(open(MANIFEST))

    dit_handler = AceStepHandler()
    dit_handler.initialize_service(
        project_root=PROJECT,
        config_path="acestep-v15-turbo",
        device="cuda",
        offload_to_cpu=True,            # Tier 5 (16 GB T4) recommendation
        quantization="int8_weight_only",
    )
    llm_handler = LLMHandler()
    llm_handler.initialize(
        checkpoint_dir=CHECKPOINTS,     # weights download here on first run
        lm_model_path="acestep-5Hz-lm-0.6B",
        backend="vllm",
        device="cuda",
    )

    for seed in m["seeds"]:
        final_path = "%s/candidate_%d.mp3" % (OUTDIR, seed)
        if os.path.exists(final_path):  # resume after a session timeout
            rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "stage": "music", "model": "ace-step-1.5", "seed": seed,
                   "status": "cache", "note": "candidate already present; skipped"}
            log(rec)
            print(rec)
            continue
        t0 = time.time()
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "stage": "music", "model": "ace-step-1.5", "seed": seed,
               "status": "started"}
        log(rec)
        try:
            params = GenerationParams(
                caption=m["caption"],
                lyrics="",                       # instrumental: no lyrics
                instrumental=bool(m.get("instrumental", True)),
                bpm=m.get("bpm"),
                keyscale=m.get("key", ""),       # e.g. "A major"
                timesignature="",
                duration=float(m["seconds"]),
                seed=int(seed),
                inference_steps=8,               # turbo default
            )
            config = GenerationConfig(
                batch_size=1,                    # Tier 5: max 4; 1 = save-as-you-go
                use_random_seed=False,           # respect params.seed exactly
                audio_format="mp3",
            )
            result = generate_music(dit_handler, llm_handler, params, config,
                                    save_dir=OUTDIR)
            if not result.success:
                raise RuntimeError(result.error or "generate_music returned failure")
            # Rename the produced file to the contract name candidate_<seed>.mp3.
            produced = []
            for audio in result.audios:
                produced.append(audio["path"])
            src = produced[0]
            if os.path.abspath(src) != os.path.abspath(final_path):
                shutil.move(src, final_path)
            rec.update(status="ok", latency_s=round(time.time() - t0, 1),
                       output="musiccand/candidate_%d.mp3" % seed)
        except Exception as e:  # keep going — save-as-you-go on quota-limited GPUs
            rec.update(status="error", note=str(e)[:300], latency_s=round(time.time() - t0, 1))
        log(rec)
        print(rec)

    print("done — candidates in %s:" % OUTDIR)
    for p in sorted(glob.glob("%s/candidate_*.mp3" % OUTDIR)):
        print(" ", p)


if __name__ == "__main__":
    main()
