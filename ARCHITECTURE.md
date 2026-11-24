# Architecture

## The contract

`storyboard.json` is the single source of truth. Every stage reads it; no
stage reads another stage's *inputs* — only its *outputs*, and only through
files in `outputs/` whose names the storyboard implies (`<shot_id>.wav`,
`<shot_id>.png`, `<shot_id>.mp4`). The schema in `schema/storyboard.schema.json`
is validated by `pipeline/validate_sb.py` before every run (`pipeline/run_all.py`
runs it first, and `make validate` runs it alone).

Why a JSON contract: every stage can be run, cached, tested and re-run in
isolation; the film is a pure function of the storyboard plus cached artifacts;
regenerating one shot never touches the other shots.

## Stage boundaries

```
storyboard.json ─┬─ narration ─── outputs/narration/<id>.wav        (Gemini TTS | mock tone)
                 ├─ keyframes ── outputs/keyframes/<id>.png        (FLUX/CF   | mock placeholder)
                 ├─ shots ────── outputs/shots/<id>.mp4 | plan.json (Wan 2.2  | Ken Burns fallback)
                 ├─ music ────── outputs/music/score_final.wav     (ACE-Step | placeholder pad)
                 └─ assemble ─── outputs/film_9x16.mp4, film_16x9.mp4 (FFmpeg only)
```

- `script.py` is upstream of everything: it drafts the storyboard from
  `story_brief.md` (optional — the storyboard is hand-reviewed either way).
- `shots.py` never calls a model from this machine (no GPU here). It writes
  `kaggle/manifest_shots.json`, checks which clips exist, and records the
  decision (real clip vs Ken Burns) in `outputs/shots/plan.json`, which
  `assemble.py` consumes. This is the brief's fallback made structural:
  the film assembles with any number of real clips.
- `assemble.py` is deterministic FFmpeg: timeline from measured narration
  durations, per-shot segments per aspect ratio, end card, concat, sidechain
  ducking, two-pass loudnorm to −14 LUFS / −1 dBTP, burned-in English subtitles,
  faststart MP4.

## Caching

Content-hash caching in `narration.py` and `keyframes.py`: the cache key is
`sha256(model, prompt, dimensions, seed, voice, lang, style)`; artifacts live
next to their `<name>.json` key sidecars. A re-run regenerates only shots whose
storyboard lines actually changed. `shots.py` treats an existing `<id>.mp4`
with a valid probe as its cache; `assemble.py` always re-renders (it is cheap
and deterministic, and catches storyboard timing changes).

## Failure handling

- **Retries**: `pipeline/net.py` retries every HTTP call 3× with exponential
  backoff on 429/5xx and network errors, and logs every attempt's outcome.
- **Fallbacks**: TTS fails → placeholder tone (real duration); FLUX fails →
  placeholder keyframe; no Wan clip → Ken Burns; no ACE-Step score →
  placeholder pad. The pipeline never dead-ends; degradations are visible in
  `runs.jsonl` (`status: mock/error/skip`).
- **Secrets**: only in `.env` (gitignored), loaded by `pipeline/common.py`;
  never logged (params carry prompts and seeds, not credentials).
- **GPU quota**: heavy generation runs as save-as-you-go Kaggle workers
  (`kaggle/*_worker.py` write `kaggle_runs.jsonl` even on error).

## Cost and latency accounting

Every model call appends one line to `runs.jsonl`: stage, model, params
(prompt hash + dimensions), seed, latency_ms, status, estimated list-price
cost. `COSTS.md` summarises it; the summary is written from the log, not from
memory.
