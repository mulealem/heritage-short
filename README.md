# Heritage Short — a storyboard-to-film pipeline

One file — `storyboard.json` — is the contract. Six stages read it and write
their outputs; the last stage edits a finished short film with FFmpeg.

**The one command** (after `cp .env.example .env` and filling in keys):

```bash
make film
```

That runs: validate → narration (Gemini TTS) → keyframes (FLUX on Cloudflare)
→ shots (Wan 2.2 clips when present, Ken Burns fallback otherwise) → music
(ACE-Step score or placeholder pad) → assemble (ducking, subtitles, loudness,
end card) and writes **`outputs/film_9x16.mp4`** and **`outputs/film_16x9.mp4`**.

No keys yet? It still runs end to end in offline mock mode (placeholder voice,
images and score with real timing) — that is how you can verify the pipeline
on a clean machine:

```bash
make mock
```

## What you need

| Stage | Model | Where | Key |
|---|---|---|---|
| narration, drafting | Gemini Flash TTS | hosted | `GEMINI_API_KEY` (Google AI Studio, free tier) |
| keyframes | FLUX.1 schnell | Cloudflare Workers AI | `CF_ACCOUNT_ID`, `CF_API_TOKEN` (free daily allowance) |
| moving shots | Wan 2.2 TI2V-5B | Kaggle T4 (no key) | run `kaggle/` workers by hand |
| music | ACE-Step 1.5 | Kaggle/Colab (no key) | run `kaggle/` workers by hand |
| assembly | FFmpeg | this machine | none |

Copy `.env.example` to `.env` and fill in what you have; missing pieces fall
back to clearly-marked mock outputs so the pipeline never dead-ends.

## Stages

| Stage | Script | Reads | Writes |
|---|---|---|---|
| validate | `pipeline/validate_sb.py` | `storyboard.json`, `schema/` | errors (or passes) |
| script | `pipeline/script.py` | `story_brief.md` | `storyboard.json` draft |
| narration | `pipeline/narration.py` | storyboard | `outputs/narration/*.wav` |
| keyframes | `pipeline/keyframes.py` | storyboard | `outputs/keyframes/*.png` |
| shots | `pipeline/shots.py` | storyboard | `outputs/shots/plan.json`, clips |
| music | `pipeline/music.py` | storyboard | `outputs/music/score_final.wav` |
| assemble | `pipeline/assemble.py` | everything above | `outputs/film_*.mp4` |

Change one shot in `storyboard.json`, rerun `make film`: only that shot's
narration/keyframe is regenerated (content-hash caching) and only that segment
is re-rendered into the cut. Every model call appends a line to `runs.jsonl`
(model, parameters, seed, latency, estimated cost, status).

## Repo map

The docs that tell the story of building this:

- `ARCHITECTURE.md` — stages, contracts, caching, failure handling
- `DESIGN.md` — audience, intent, the two user tests
- `EXPERIMENTS.md` — hypothesis → change → result
- `FAILURES.md` — what broke and what fixed it
- `COSTS.md` — measured latency and list-price equivalents
- `ETHICS.md` — consent, licences, labelling

`outputs/` media is gitignored (it regenerates from the storyboard — that is
the point of the pipeline); `runs.jsonl` and all manifests are committed.

## Requirements

Python 3.8+ (stdlib only — nothing to `pip install`), FFmpeg with libx264 and
libass (`sudo apt install ffmpeg` covers it on Ubuntu). GPU stages run on
Kaggle's free T4s; see `kaggle/README.md`.
