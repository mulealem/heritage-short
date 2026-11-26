# Costs: measured latency and list-price equivalents

Every number below is read from `runs.jsonl` (`python3 tools/cost_report.py`),
not from memory. Machine: a 6-core AMD EPYC VPS, 15 GB RAM, **no GPU**.

## The headline

- **GPU minutes used: 0.** No stage of the submitted film ran on a GPU. Wan 2.2
  and ACE-Step were never executed; the picture is drawn on CPU and the score
  is synthesised by code.
- **Whole project, every iteration included:** 285 paid-model calls ≈ **$0.65**
  at list prices.
- **The assets in the final film:** 29 images + 10 narration lines ≈ **$0.11**.
- **Rebuilding both films from a clone: $0** — every model output is cached and
  committed; only the two CPU renders run.

## Per-stage measurements

| Stage | Model | n | median | max | GPU min | List price |
|---|---|---|---|---|---|---|
| narration | Gemini 3.8 Flash TTS | 27 | 3.8 s | 6.7 s | — | $0.028 |
| narration (older model) | Gemini 2.5 Flash TTS | 21 | 6.1 s | 15.5 s | — | $0.024 |
| narration tail trim | FFmpeg | 10 | ~0.1 s | 0.1 s | — | free |
| narration edit-to-time | FFmpeg (`atempo`, pause cap) | 20 | ~0.2 s | 0.4 s | — | free |
| cast portraits | MiniMax image-01 | 4 | 18.8 s | 19.1 s | — | $0.014 |
| keyframes | MiniMax image-01 | 76 | 19.5 s | 152.8 s | — | $0.266 |
| panels (interaction/reaction) | MiniMax image-01 | 56 | 18.6 s | 39.9 s | — | $0.196 |
| keyframes (draft) | FLUX-2 klein, Cloudflare | 97 | 9.1 s | 15.0 s | — | $0.116 |
| score | qenet bed (own code) | — | ~10 s | — | — | free |
| picture render | fframes, CPU (6 cores) | 12 | 211 s | 407 s | — | free |
| mix + loudnorm + mux | FFmpeg, CPU | ~200 | ~4.5 s | 38.5 s | — | free |
| moving shots | Wan 2.2 (Kaggle T4) | 0 | not run | — | 0 | — |
| score (model) | ACE-Step 1.5 | 0 | not run | — | 0 | — |

Counts for image-01 and FLUX include every iteration: three full re-styles, a
character redesign, and the 26-cut ensemble revision. The production set is 11
keyframes + 16 panels + 2 cast portraits = 29 images ≈ $0.10 at $0.0035/image,
and 10 narration lines (656 characters) ≈ $0.007.

## Notes

- **The one slow call.** A 152.8 s image-01 request was a provider-side stall;
  the median is 19.5 s.
- **The final films.** 9:16 and 16:9, each **89.7 s** at 24 fps, h264 + AAC +
  an English subtitle track, −17.4 dB mean / −1.0 dB peak. Each is one CPU
  pass of 3.5–7 minutes. The narration is 84.4 s as recorded and 77.8 s after
  the edit-to-time (`EXPERIMENTS.md` E11).
- **Free tier limits found, not assumed.** Gemini TTS: 10 requests/day per key
  and 3 per minute on the free tier (F3, F10). Cloudflare Workers AI: 10,000
  neurons/day (F8). MiniMax M plan: images allowed, video not (F6), and a plan
  usage cap after ~85 images in a day (F12). The brief's "50–170 images/day"
  was never the bottleneck; request quotas were.
- **Where the money went.** Image generation is cheap; API ceilings are what
  shape the workflow. Two free-tier TTS keys and one paid image plan produced
  everything here.

## Open vs paid image model (E1)

Same prompts and style block, 720×1280:

| | MiniMax image-01 | FLUX-2 klein (Cloudflare) |
|---|---|---|
| median latency | 19.5 s | 9.1 s |
| price per image | $0.0035 | free (10k neurons/day) |
| reference-conditioned (same face) | yes | no |
| look | stronger ink contours and halftone texture | both produce the style |

FLUX is twice as fast and free, and is kept as the draft path; image-01 won on
reference conditioning (consistent faces) and on not hitting a daily wall
mid-restyle.

## Frontier comparison

None. Nano Banana, Omni Flash and Lyria 3.5 are behind paid billing that was
not available, so no frontier model was run and no comparison is claimed. The
comparison above is open/free vs a low-cost paid API.

## About these prices

List-price equivalents use the `LIST_PRICES` table in `pipeline/common.py` and
are **estimates** — check current prices and update both places together.
The 58 rows from 24 Nov 2026, 12:52–13:14 UTC with `status: "mock"` are the
initial mock scaffold and carry no cost.
