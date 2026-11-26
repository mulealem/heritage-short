# Heritage Short — a storyboard-to-film pipeline

One file — **`storyboard.json`** — is the contract. Every stage reads it,
validates it against `schema/storyboard.schema.json`, and writes its output.
Change one prompt or one line, rerun, and only that asset is regenerated.

The film it makes: **“Eat, My Clothes, Eat!” (ብሉ ልብሶቼ ብሉ)** — the Aleqa Gebre
Hanna folk tale, 89.7 s, narrated in Amharic with English subtitles, an
original score ducked under the voice, an AI end card, in **9:16 and 16:9**.
It is a *motion comic*: generated comic panels cut and moved like a comic
page, rendered deterministically on CPU by an [fframes](https://fframes.studio)
(Rust) scene — no video model, no GPU. Same inputs give the same frames.

## The one command

```bash
make short
```

That runs, in order:

```
validate → narration → cast → keyframes → panels → comic build
         → score → comic render (9:16) → comic render (16:9)
```

and writes `outputs/film_9x16.mp4` and `outputs/film_16x9.mp4`.

What it costs and how long it takes:

| Starting point | Model calls | Time |
|---|---|---|
| A clone of this repository (the cached outputs come with it) | **none** | **8 min 19 s measured**, clone to both films, Rust build included |
| One prompt or line changed | exactly one call (~$0.004) | that call, then the renders |
| Empty `outputs/` with keys in `.env` | 29 images + 10 narration lines, ~**$0.11** at list prices | the above plus ~5 min of generation |

Credentials are requested **only for an asset that is not cached**. A clone
that keeps `outputs/` rebuilds both films with no `.env` at all.

To regenerate from scratch, add keys: `cp .env.example .env` and fill in
`GEMINI_API_KEY` (narration — free tier) and `MINIMAX_API_KEY` (images), or set
`IMAGE_PROVIDER=cloudflare` and add the two Cloudflare values to use the free
FLUX draft path instead.

## What you need

- **Python 3.8+**, standard library only — nothing to `pip install`.
- **FFmpeg** with libx264 (`sudo apt install ffmpeg` on Ubuntu).
- **Rust** (rustup, stable) for the comic renderer.
- **x264 build 163** — the renderer's bundled libavcodec links one exact x264
  ABI. Ubuntu 22.04's `libx264-dev` is build 163 and works as is. On other
  systems build it once; the five commands are in [`comic/README.md`](comic/README.md).
- About 35 MB of tracked model outputs ship with the clone (see below).

| Stage | Model | Where | Key |
|---|---|---|---|
| narration | Gemini 3.8 Flash TTS (130+ languages incl. Amharic) | hosted | `GEMINI_API_KEY` (free tier) |
| keyframes, panels, cast | MiniMax image-01 | hosted | `MINIMAX_API_KEY` (one subject reference per image) |
| keyframes (free draft) | FLUX-2 klein | Cloudflare Workers AI | `CF_ACCOUNT_ID`, `CF_API_TOKEN` |
| score | the qenet bed, synthesised by code — or an ACE-Step 1.5 take from Kaggle | local, or Kaggle | none, or run `kaggle/` |
| picture, mix, mux | fframes (Rust, CPU) + FFmpeg | this machine | none |

The pipeline is **real only**: no placeholder voice, image, clip or score is
ever written. A stage that is missing an input stops with the exact command
that produces it.

## Stages

| Stage | Script | Reads | Writes |
|---|---|---|---|
| validate | `pipeline/validate_sb.py` | `storyboard.json`, `schema/` | errors (or passes) |
| script | `pipeline/script.py` | `story_brief.md` | `storyboard.json` draft (optional) |
| narration | `pipeline/narration.py` | storyboard | `outputs/narration/*.wav` |
| cast | `tools/comic_cast.py` | storyboard | `outputs/character_refs/*.jpg` |
| keyframes | `pipeline/keyframes.py` | storyboard + cast | `outputs/keyframes/*.png` |
| panels | `tools/comic_panels.py` | storyboard + `comic/panels.json` | `outputs/comic_panels/*.jpg` |
| score | `pipeline/score.py` | storyboard, `comic/film.json` | `outputs/music/score_final.wav` |
| comic | `pipeline/comic.py`, `comic/` | panels + narration + score | `outputs/film_9x16.mp4`, `outputs/film_16x9.mp4` |
| shots, assemble | `pipeline/shots.py`, `pipeline/assemble.py` | clips | the video-clip route (`make film`) |

Every stage starts with `common.load_storyboard()`, which validates the
contract, so a storyboard that breaks the schema stops everything before any
model is called.

## Change one thing, regenerate one thing

Every model call is cached by a hash of exactly what was sent (prompt,
reference, model, size, seed). Edit one image prompt in `storyboard.json`:

```bash
make short
#   s1_das: cache hit … s5_dressed: cache hit
#   keyframes  image-01  /…/outputs/keyframes/s5_dressed.png   <- the one call
```

Nine keyframes and sixteen panels are cache hits; one image is drawn; the
films are re-rendered from the same timeline. Narration works the same way,
per line. Measured in a clone (`FAILURES.md` F19): with one prompt changed and
no key, the stage stops and asks for the key; with the key it makes exactly one
call (image-01, 18.5 s, $0.0035) and reports ten cache hits. The same is true from the web editor, with a **Regenerate** button
per keyframe, per panel and per line.

## The two pictures from one timeline

Both films share `comic/film.json` and one audio master. The renderer is
compiled once per layout (cargo feature `wide`):

- **9:16 (1080×1920)** — full-bleed panels, camera moves, pop-in speech
  balloons, starburst sound effects, word-by-word English captions, halftone
  screen, ink border.
- **16:9 (1920×1080)** — a landscape comic page: the same panel strip at full
  height in the centre, the **spoken Amharic line in the left margin and its
  English subtitle in the right**, shot counter and title in the footers.

Each beat is cut into 1–3 panels (wide establishing shot, interaction,
reaction), 26 cuts in all. Timing comes from the recorded narration, edited to
the contract's `meta.timing`: long internal pauses held to 0.40 s, a 5 %
pitch-preserving tempo, 0.5 s of air after each line, and the held beats the
story needs (the deadpan, the laughing crowd after the punchline).

## The video-clip route

`make film` is the other renderer: real moving shots from Wan 2.2 on Kaggle,
assembled by FFmpeg. It is real-only and untested end to end — no Wan clip was
ever produced for this film (see `FAILURES.md` F6), and the submitted film was
made with `make short`. `kaggle/README.md` has the steps if you want to try it.

## Edit and regenerate (local web editor)

```bash
make editor          # http://127.0.0.1:8765
```

A stdlib server and a single page to review and change the contract: every
field that reaches a model (image prompt, motion prompt, narration, subtitle
line, duration, seed, reason, each panel's prompt and cut point), a read-only
preview of the exact composed prompt, per-asset regeneration, and a Render
button that streams the log. Saving validates against the schema.

`bash tools/serve_public.sh` puts an ephemeral Cloudflare tunnel in front of
it with a secret token. Anyone with the link can spend your API quota.

## What is in `outputs/`, and why it is tracked

The model outputs are the evidence and the cache, so they are committed:
narration WAVs and their durations, 11 keyframes, 16 panels, 2 cast portraits,
the score, and `runs.jsonl`. What is rebuilt on every run is not tracked
(render intermediates, the fitted narration, the films) — `make short` writes
them. The two films are attached to the repository's Release because of their
size.

## Reading the project

- [`STORY.md`](STORY.md) — the film as a story, plus the subtitle text
- [`PROMPTS.md`](PROMPTS.md) — every prompt of the film: story, narration,
  style block, identity directives, cast anchors, all 26 cuts with their sync
  status (`make prompts` regenerates it)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — stages, contracts, caching, failure handling
- [`DESIGN.md`](DESIGN.md) — audience, intent, the user tests
- [`EXPERIMENTS.md`](EXPERIMENTS.md) — hypothesis → change → result
- [`FAILURES.md`](FAILURES.md) — what broke, what was tried, what fixed it
- [`COSTS.md`](COSTS.md) — measured latency and list-price equivalents
- [`ETHICS.md`](ETHICS.md) — consent, licences, labelling
- [`REPORT.md`](REPORT.md) — the written report for the brief
- `docs/architecture.html` — a visual map (`make serve`, then
  http://127.0.0.1:8123/architecture.html)

## The log

`runs.jsonl` has one line per call: stage, model, parameters, seed, latency,
estimated cost, status, output path. `python3 tools/cost_report.py` summarises
it. 58 lines from the first hour of the project (24 Nov 2026, 12:52–13:14 UTC,
`status: "mock"` or model `veo-fake`) are the mock-first scaffold it started
from; every line after that is a real call.
