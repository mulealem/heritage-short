# Running the GPU stages on Kaggle (free)

This machine has no GPU, so the video and music models run on Kaggle's free
GPUs (about 30 GPU-hours a week; phone verification required). Both workers
are **resume-safe**: files already produced are skipped, so a timed-out
session just needs another run, not a restart.

## One-time setup (5 minutes)

1. Create/verify a Kaggle account → Settings → phone verification
   (unlocks the GPU quota).
2. kaggle.com → Code → New Notebook → Session options (right panel) →
   Accelerator → **GPU T4 x2** (one T4 is enough; both workers use one).

## Video: Wan 2.2 TI2V-5B (~30–60 min for all 8 clips)

1. On this machine: `make keyframes && make shots`
   (writes `outputs/keyframes/*.png` + `kaggle/manifest_shots.json`).
2. In the notebook, add a **setup cell** and run it (installs nothing heavy —
   diffusers is preinstalled, but make sure it is current):
   ```
   !pip install -U diffusers
   ```
3. Upload into `/kaggle/working/` (drag & drop onto the file browser):
   - `kaggle/manifest_shots.json`
   - the 8 PNGs from `outputs/keyframes/` — put them in a `keyframes/`
     subfolder (New → Folder `keyframes`, then upload into it).
4. Add a second cell, paste in all of `kaggle/wan22_worker.py`, run it.
   It prints one line per shot and writes:
   - `shotclips/<shot_id>.mp4` — the 8 clips (121 frames, 720p-class, 24 fps)
   - `kaggle_runs.jsonl` — per-shot status/latency evidence
5. Download the whole `shotclips/` folder (tick checkbox → Download) and drop
   it in a folder on this machine, then tell me the path — I import the clips
   with `tools/import_clips.py`. (Or copy them to `outputs/shots/` yourself.)
   Also copy `kaggle_runs.jsonl` into the repo root — it merges into the
   COSTS.md evidence.

Notes: the worker auto-picks fp16 on T4 (Turing has no bf16) and resizes
your keyframes to Wan's 704×1280 budget. If a shot errors, the run continues;
rerun the cell and only the missing shots generate.

## Music: ACE-Step 1.5 (~15–30 min for 3 candidates)

1. On this machine: `make music` (writes `kaggle/manifest_music.json`).
2. New notebook (T4 again) → setup cell (the 1.5 API needs its own install):
   ```
   !git clone https://github.com/ace-step/ACE-Step-1.5 /kaggle/working/ACE-Step-1.5
   %cd /kaggle/working/ACE-Step-1.5
   !pip install -e . && pip install vllm
   ```
3. Upload `kaggle/manifest_music.json` into `/kaggle/working/`.
4. New cell, paste in all of `kaggle/ace_step_worker.py`, run it.
   First run downloads checkpoints (a few GB — one-time). It writes:
   - `musiccand/candidate_<seed>.mp3` — 3 score candidates (seeds 42/43/44)
   - `kaggle_runs.jsonl` — per-candidate status/latency
5. Download `musiccand/` and put it somewhere I can see; then **audition**:
   listen to the three candidates under the narration at low volume, pick
   one, and tell me the seed number — I copy it to
   `outputs/music/score_final.wav`. Note WHY you chose it in EXPERIMENTS.md
   (that one line is graded).
   Also copy `kaggle_runs.jsonl` into the repo root.

## Moving files around

Drag & drop in the Kaggle web UI is the simplest way in both directions.
The Kaggle CLI (`pip install kaggle`, needs `kaggle.json`) also works but is
not needed for this flow.
