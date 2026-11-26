# The GPU stages on Kaggle (free)

Two stages can run on a borrowed GPU instead of this machine: **moving
shots** with Wan 2.2 and **music** with ACE-Step 1.5. Kaggle gives about 30
GPU-hours a week after phone verification. Both workers are resume-safe: files
already produced are skipped, so a timed-out session just needs another run.

> **Status, stated plainly: neither worker has been run end to end.** The
> submitted film is a motion comic with a score synthesised by code; no Wan
> clip and no ACE-Step take exists in `outputs/` or in `runs.jsonl`. The
> workers are written against the models' current documentation and are
> untested. That is the honest state of the video-clip route and of the
> music-model route (`FAILURES.md` F6 explains why the first never ran).

## One-time setup (5 minutes)

1. Kaggle → Settings → phone verification (unlocks the GPU quota).
2. Kaggle → Code → New Notebook → Session options (right panel) →
   Accelerator → **GPU T4 x2** (one T4 is enough; both workers use one).

## Video: Wan 2.2 TI2V-5B (several minutes per shot on a T4)

1. On this machine:
   ```bash
   make keyframes && make shots        # keyframes + kaggle/manifest_shots.json
   python3 tools/build_bundles.py      # outputs/kaggle_upload/video_bundle.zip
   ```
2. In the notebook, upload `outputs/kaggle_upload/video_bundle.zip` to
   `/kaggle/working/` and unpack it (`!unzip -o video_bundle.zip`). It holds
   the manifest and every keyframe it lists, in a `keyframes/` folder.
3. Add a setup cell (`!pip install -U diffusers`), then a second cell with all
   of `kaggle/wan22_worker.py`, and run it. It writes:
   - `shotclips/<shot_id>.mp4` — one clip per shot (121 frames, about 720p,
     24 fps)
   - `kaggle_runs.jsonl` — one line per shot with status and latency
4. Download `shotclips/` and bring it to this machine, then:
   ```bash
   python3 tools/import_clips.py <folder-with-the-clips> --model wan2.2-ti2v-5b
   make shots && make assemble
   ```
5. Copy `kaggle_runs.jsonl` into the repository root: it is the GPU-time
   evidence for `COSTS.md`.

Notes: the worker picks fp16 on a T4 (Turing has no bf16) and resizes each
keyframe to Wan's 704×1280 budget. If a shot errors, the run continues; rerun
the cell and only the missing shots are generated.

## Music: ACE-Step 1.5 (about 15–30 minutes for three candidates)

1. On this machine: `make music` (writes `kaggle/manifest_music.json`, sized
   to the current cut).
2. New notebook (T4) → setup cell (the 1.5 API needs its own install):
   ```
   !git clone https://github.com/ace-step/ACE-Step-1.5 /kaggle/working/ACE-Step-1.5
   %cd /kaggle/working/ACE-Step-1.5
   !pip install -e . && pip install vllm
   ```
3. Upload `kaggle/manifest_music.json` to `/kaggle/working/`.
4. New cell with all of `kaggle/ace_step_worker.py`; run it. The first run
   downloads checkpoints (a few GB, once). It writes:
   - `musiccand/candidate_<seed>.mp3` — three candidates (seeds 42, 43, 44)
   - `kaggle_runs.jsonl` — one line per candidate
5. Download `musiccand/` into `outputs/music/`, then **audition**: play each
   candidate under the narration at low volume and pick one. Then:
   ```bash
   ffmpeg -i outputs/music/candidate_42.mp3 -c:a pcm_s16le outputs/music/score_final.wav
   echo "ace-step-1.5 seed 42" > outputs/music/score_source.txt
   python3 -m pipeline.comic remux 9x16 && python3 -m pipeline.comic remux 16x9
   ```
   (Use the seed you chose. The remux re-mixes both films in about 20 seconds
   each, with no re-render.) Write down *why* you chose it in
   `EXPERIMENTS.md`, and copy `kaggle_runs.jsonl` into the repository root.

Until a model take is chosen, `make short` fills the score slot with a
deterministic bed that this repository synthesises itself
(`tools/make_qenet_bed.py`), so the film is never silent and never uses a
placeholder.

## Moving files around

Drag and drop in the Kaggle web UI is the simplest way in both directions.
The Kaggle CLI (`pip install kaggle`, needs `kaggle.json`) also works but is
not needed for this flow.
