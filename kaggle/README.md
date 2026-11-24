# Running the GPU stages on Kaggle (free)

This machine has no GPU, so the video and music models run on Kaggle's free
GPUs (about 30 GPU-hours a week; phone verification required).

## One-time setup

1. Create/verify a Kaggle account (phone verification unlocks the GPU quota).
2. New Notebook → Session options → Accelerator → GPU T4 x2.

## Video: Wan 2.2 TI2V-5B

1. On this machine: `make keyframes && make shots` (writes `kaggle/manifest_shots.json`).
2. Zip and upload to the notebook (drag & drop):
   - `outputs/keyframes/*.png`
   - `kaggle/manifest_shots.json`
3. Open `kaggle/wan22_worker.py`, paste it as a notebook cell, fix the three
   paths at the top if your upload layout differs, and run it.
4. It writes `shotclips/<id>.mp4` per shot and `kaggle_runs.jsonl`.
5. Download the clips, put them in `outputs/shots/` here, and copy
   `kaggle_runs.jsonl` into the repo root (it merges into COSTS.md evidence).

Tips: draft at 720p with `num_inference_steps=30`; batch all shots in one
session; sessions time out — the worker saves as it goes.

## Music: ACE-Step 1.5

1. `make music` writes `kaggle/manifest_music.json`.
2. Upload it, paste `kaggle/ace_step_worker.py`, run — it renders N candidates.
3. Listen to them under the narration at low volume, pick one, rename it
   `outputs/music/score_final.wav`, and note WHY you chose it in EXPERIMENTS.md.

## Moving files around

You can use the Kaggle API (`pip install kaggle`, needs `kaggle.json`) or just
drag files in the web UI — both work; the web UI is simpler for a one-week project.
