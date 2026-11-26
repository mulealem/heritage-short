# Architecture

## The one command

`make short` (`pipeline/short.py`) chains the stages that made the submitted
film: validate → narration → cast → keyframes → panels → comic build → score →
comic render (9:16) → comic render (16:9). Each stage is its own process, so a
stage's exit code is the only thing the next one depends on, and the log
(`runs.jsonl`) is the record of what the run actually called. At the end it
prints what the run cost: N real model calls, M cache hits, and the two films.

## The contract

`storyboard.json` is the single source of truth. Every stage reads it; no
stage reads another stage's *inputs* — only its *outputs*, and only through
files in `outputs/` whose names the storyboard implies (`<shot_id>.wav`,
`<shot_id>.png`, `<shot_id>.mp4`). The schema in `schema/storyboard.schema.json`
is validated **before every stage**: every script goes through
`common.load_storyboard()`, which refuses a storyboard that does not validate,
so a broken contract stops the run before any model is called (`make validate`
runs that check alone).

The contract also carries the edit: `meta.timing` says how the recorded
narration is fitted to the cut (`beat_pad_seconds`, `pause_cap_seconds`,
`narration_tempo`), a shot's `duration_s` above its line is a held beat, and
`comic/panels.json` holds the direction per beat (which panels, where they
cut, balloons, sound effects, which cast portrait anchors a cut).

Why a JSON contract: every stage can be run, cached, tested and re-run in
isolation; the film is a pure function of the storyboard plus cached artifacts;
regenerating one shot never touches the other shots.

## Stage boundaries

```
storyboard.json ─┬─ narration ─── outputs/narration/<id>.wav      (Gemini TTS, real only)
                 ├─ cast ─────── outputs/character_refs/<actor>.jpg (image-01 portrait)
                 ├─ keyframes ── outputs/keyframes/<id>.png        (MiniMax image-01 | FLUX)
                 ├─ panels ───── outputs/comic_panels/<id>_xN.jpg  (interaction/reaction panels)
                 │
                 ├─ shots ────── outputs/shots/<id>.mp4 | plan.json (Wan 2.2 clips, real only)
                 ├─ assemble ─── outputs/film_9x16.mp4, film_16x9.mp4  (real clips + FFmpeg)
                 │
                 └─ comic ────── outputs/film_9x16.mp4, film_16x9.mp4  (fframes CPU motion comic)
                                   ↑ score: outputs/music/score_final.wav (pipeline/score.py)
```

Two renderers read the same contract: `assemble.py` cuts real moving clips,
`comic.py` animates the still panels. Both write the same film names from the
same storyboard, narration and score; run the one the film wants.

- `script.py` is upstream of everything: it drafts the storyboard from
  `story_brief.md` (optional — the storyboard is hand-reviewed either way).
- `shots.py` never calls a model from this machine (no GPU here). It writes
  `kaggle/manifest_shots.json`, then requires a valid clip for EVERY shot and
  records it in `outputs/shots/plan.json`, which `assemble.py` consumes.
  A missing clip stops the stage with the exact Kaggle-worker instructions —
  the pipeline is real-only; there is no still-image fallback.
- `assemble.py` is deterministic FFmpeg: timeline from measured narration
  durations, per-shot segments per aspect ratio, end card, concat, sidechain
  ducking, two-pass loudnorm to −14 LUFS / −1 dBTP, burned-in English subtitles,
  faststart MP4.
- `narration.py` also *edits* the recording to the contract
  (`ensure_fit`): internal pauses longer than `pause_cap_seconds` are held to
  that length (cut inside silence) and a pitch-preserving tempo is applied, so
  the cut fits its target length without re-recording. The raw WAVs are never
  modified; the fitted lines go to `outputs/narration_fit/` and are what the
  timeline and the mix use.
- `score.py` is the score slot as the one command needs it: a chosen score
  (an ACE-Step take copied to `score_final.wav`) is kept; an empty slot is
  filled with the deterministic qenet bed (`tools/make_qenet_bed.py`), never a
  placeholder. `make music` is the music-model path proper and refuses to
  guess between candidates.
- `comic.py` is the motion-comic renderer. It builds `comic/film.json` from the
  storyboard plus the fitted narration (per-shot timing, word timings for
  kinetic captions, balloons, SFX and cuts from `comic/panels.json`), renders
  the picture with the `comic/` fframes scene on CPU (full-bleed panels, **N
  cuts per shot** — wide establishing, interaction, reaction — camera moves,
  halftone screens, ink border, pop-in balloons, starburst SFX, quick-cut
  flashes), mixes the same audio master as `assemble.py`, and muxes a soft
  English subtitle track. Same inputs give the same frames (the encoded file
  is not bit-reproducible — `FAILURES.md` F17); no GPU, no video API.
  **Two layouts of one timeline**: the renderer is compiled once
  per layout (cargo feature `wide`); 9:16 is the full-bleed vertical frame,
  16:9 is a landscape comic page with the same panel strip centred and the
  Amharic line and English subtitle in the margins. The mix normalises the
  bed to −24 LUFS and sidechain-ducks it under the voice.

## Swapping models

The stages are deliberately model-agnostic. Each GPU stage's contract with
the rest of the pipeline is a *file*, not an API:

- **Video**: `outputs/shots/<shot_id>.mp4` + the mode decision in
  `outputs/shots/plan.json`. Whatever makes those files — Wan 2.2 (the
  included Kaggle worker), HunyuanVideo, or a hosted API like Veo/Runway/
  Kling — the assemble stage consumes them identically: any resolution is
  scale-cropped to 9:16 / 16:9, re-timed to 24 fps, and a short clip is
  padded by holding its last frame (`tpad`), so a 5 s hosted-model clip
  still fills a 7 s shot without breaking the timeline.
  Ingest external clips with `python3 tools/import_clips.py <folder> --model veo-3`
  (validates, names, and logs them to runs.jsonl), then `make shots && make assemble`.
- **Keyframes**: `IMAGE_PROVIDER` picks the image model — `minimax` (image-01,
  paid plan, supports one `subject_reference` portrait so faces stay consistent
  across shots) or `cloudflare` (FLUX-2 klein, free daily allowance, text-only
  so faces drift). The prompt, seed, reference and cache scaffolding is shared;
  `tools/comic_cast.py` generates the cast anchors, `tools/comic_panels.py` the
  interaction/reaction panels cut into each beat.
- **Narration / music**: model names are env-configurable (`GEMINI_TTS_MODEL`);
  the Kaggle workers are the only ACE-Step-specific code.

What a swap does NOT give you for free, and where to record it: seeds may not
be honoured by hosted APIs (note reproducibility limits in EXPERIMENTS.md),
cost must be logged per call at list price (the adapters call
`common.log_call`), and per-model quirks belong in FAILURES.md. The
comparison itself (same shot, two models, blind preference) is a strong
"curiosity beyond the floor" experiment.

## Caching

Content-hash caching in `narration.py`, `keyframes.py`, `comic_panels.py` and
`comic_cast.py`: the cache key is the sha256 of **exactly what would be sent**
— provider, the model token for that provider, the composed prompt (style
block + shot prompt + that character's identity directive), reference,
dimensions, seed, and for narration the text, language, voice and style.
Artifacts live next to their `<name>.json` key sidecars, and those sidecars
are committed, so a clone recognises its own cache.

Three properties the keys are built to have:

- **One change, one call.** Edit one prompt and only that key changes; every
  other asset is a cache hit and costs nothing.
- **Independent of unrelated settings.** The key holds no environment value
  the asset did not depend on, so a clone without a `.env` still hits.
- **Honest status.** `tools/export_prompts.py` recomputes every key and
  reports each of the 26 cuts as `in sync` or `stale` in `PROMPTS.md`.

Keys are requested only on a real miss: a clone that carries `outputs/`
rebuilds both films with no credentials.

The fitted narration (`narration_fit`) is cached against the raw files'
mtimes plus the timing settings, and is cheap to rebuild. `shots.py` treats an
existing `<id>.mp4` with a valid probe as its cache. The comic picture is
re-rendered in one CPU pass (~5 min) — it is deterministic and free; what is
cached per shot is every model call behind it.

## Failure handling

- **Retries**: `pipeline/net.py` retries every HTTP call 3× with exponential
  backoff on 429/5xx and network errors, and logs every attempt's outcome.
- **Real-only, fail loud**: there are no placeholder generators. A missing API
  key (asked for only when an uncached asset needs it) or a failed call (after
  retries) stops the stage with instructions; a missing clip stops
  `shots`/`assemble` with the exact Kaggle-worker steps that produce it.
  Failures are logged to `runs.jsonl` (`status: error`) before the stage
  exits, and finished work stays cached — fixing the cause and rerunning never
  pays twice.
- **Guards on the edit**: the renderer refuses to run while a narration WAV
  was recorded from a different line than the storyboard's (so new captions
  can never be paired with old audio), and the mux warns when the film falls
  outside the brief's 60–90 s.
- **Secrets**: only in `.env` (gitignored), loaded by `pipeline/common.py`;
  never logged (params carry prompts and seeds, not credentials).
- **GPU quota**: heavy generation runs as save-as-you-go, resume-safe Kaggle
  workers (`kaggle/*_worker.py` write `kaggle_runs.jsonl` even on error and
  skip artifacts that already exist).

## Cost and latency accounting

Every model call appends one line to `runs.jsonl`: stage, model, params
(prompt hash + dimensions), seed, latency_ms, status, estimated list-price
cost. `COSTS.md` summarises it; the summary is written from the log, not from
memory.
