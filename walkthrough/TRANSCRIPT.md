# Walkthrough — transcript and recording sheet

The video `walkthrough_1080p.mp4` is **silent on purpose**: it is the
picture cut, so a voice can be recorded over it without fighting an
existing narration. This file is the script, timed to the cut, with a
soft English subtitle track already muxed (`WALKTHROUGH.srt`).

- **Length:** 229.0 s (3.82 min) — under the brief's five minutes
- **Picture:** 1920×1080, 30 fps, H.264
- **Audio:** a silent stereo track (48 kHz), ready to be replaced
- **Rebuild it:** `python3 tools/make_walkthrough.py` (needs chromium + ffmpeg)

## The timed script

| in | out | on screen | say |
|---|---|---|---|
| 0:00 | 0:09 | Eat, My Clothes, Eat! | This is a walkthrough of Heritage Short: a pipeline that turns one JSON storyboard into a finished short film. The film is an Ethiopian folk tale, narrated in Amharic with English subtitles. |
| 0:09 | 0:28 | 9:16 — 1080×1920 · 89.7 s | The film is a motion comic. Generated panels are cut and moved like a comic page: camera pushes, over-the-shoulder cuts, speech balloons, sound effects, word-by-word captions. There is no video model and no GPU in this film; the picture is drawn on the CPU in about four minutes. |
| 0:28 | 0:45 | 16:9 — the same timeline, a comic page | The same timeline renders twice. The landscape version is a comic page: the panel strip stays centred at full height, the spoken Amharic runs down the left margin, the English down the right. One film data file, one audio master, two layouts. |
| 0:45 | 1:09 | storyboard.json — the contract | Everything starts from storyboard.json: ten beats, each with a duration, an image prompt, a motion prompt, the narration and its English line, a reason, and a seed. Beside it, panels.json says how each beat is cut. Every stage validates this against the schema before it runs, so a broken contract stops the build before a model is called. |
| 1:09 | 1:31 | make short — nine stages, one command | The pipeline is nine stages. Narration records ten lines. Two cast portraits anchor the characters. Keyframes and sixteen interaction panels are generated from prompts. The build turns them into a timeline, the score is synthesised from that timeline, and the picture is rendered in both ratios and muxed with one audio master. |
| 1:31 | 1:51 | A clone rebuilds both films with no keys | One command runs all of it. On a fresh clone with no API keys, both films rebuild from the committed cache: zero model calls, thirty-nine cache hits, about nine minutes including the Rust build. |
| 1:51 | 2:17 | The hard decision: a reference is a composition prior | The hardest problem was keeping a character the same person across twenty-six cuts without wrecking the shot. A reference portrait holds the face, but it is also a composition prior: attached to a wide shot it produced a giant head over a tiny scene. So: anchor the close-ups, and describe the wides in full. |
| 2:17 | 2:31 | Change one prompt | Here is the live part. I change one image prompt — one shot, one line of the storyboard. |
| 2:31 | 2:53 | Rerun the stage: ten cache hits, one call | Then I rerun the keyframe stage. Ten jobs are served from the cache. One image is drawn: seventeen point nine seconds, about a third of a cent. The log records exactly one call, with its seed. |
| 2:53 | 3:13 | runs.jsonl — one line per call | Every call lands in runs.jsonl with its model, parameters, seed, latency and cost. The whole project, every iteration included, came to about sixty-five cents at list prices. The assets in the final film: eleven cents. |
| 3:13 | 3:37 | What this is not | What this is not. There is no video model in the film: the clip route is implemented and untested. There is no music model: the score is a bed my own code synthesises. And the audience test the brief asks for was not run — that is written down in DESIGN.md rather than invented. |
| 3:37 | 3:49 | github.com/mulealem/heritage-short | The repository, both films and this transcript are linked below. Every number in the documentation can be checked against the run log. |

## The words in order

Read at a normal pace; each block is one scene, and the scene changes on
screen when the block ends. About 485 words, roughly 3.2 minutes of
speech at a relaxed 150 words a minute.

**0:00 – 0:09** — Eat, My Clothes, Eat!

> This is a walkthrough of Heritage Short: a pipeline that turns one JSON
> storyboard into a finished short film. The film is an Ethiopian folk tale,
> narrated in Amharic with English subtitles.

**0:09 – 0:28** — 9:16 — 1080×1920 · 89.7 s

> The film is a motion comic. Generated panels are cut and moved like a comic
> page: camera pushes, over-the-shoulder cuts, speech balloons, sound effects,
> word-by-word captions. There is no video model and no GPU in this film; the
> picture is drawn on the CPU in about four minutes.

**0:28 – 0:45** — 16:9 — the same timeline, a comic page

> The same timeline renders twice. The landscape version is a comic page: the
> panel strip stays centred at full height, the spoken Amharic runs down the
> left margin, the English down the right. One film data file, one audio
> master, two layouts.

**0:45 – 1:09** — storyboard.json — the contract

> Everything starts from storyboard.json: ten beats, each with a duration, an
> image prompt, a motion prompt, the narration and its English line, a reason,
> and a seed. Beside it, panels.json says how each beat is cut. Every stage
> validates this against the schema before it runs, so a broken contract stops
> the build before a model is called.

**1:09 – 1:31** — make short — nine stages, one command

> The pipeline is nine stages. Narration records ten lines. Two cast portraits
> anchor the characters. Keyframes and sixteen interaction panels are
> generated from prompts. The build turns them into a timeline, the score is
> synthesised from that timeline, and the picture is rendered in both ratios
> and muxed with one audio master.

**1:31 – 1:51** — A clone rebuilds both films with no keys

> One command runs all of it. On a fresh clone with no API keys, both films
> rebuild from the committed cache: zero model calls, thirty-nine cache hits,
> about nine minutes including the Rust build.

**1:51 – 2:17** — The hard decision: a reference is a composition prior

> The hardest problem was keeping a character the same person across
> twenty-six cuts without wrecking the shot. A reference portrait holds the
> face, but it is also a composition prior: attached to a wide shot it
> produced a giant head over a tiny scene. So: anchor the close-ups, and
> describe the wides in full.

**2:17 – 2:31** — Change one prompt

> Here is the live part. I change one image prompt — one shot, one line of the
> storyboard.

**2:31 – 2:53** — Rerun the stage: ten cache hits, one call

> Then I rerun the keyframe stage. Ten jobs are served from the cache. One
> image is drawn: seventeen point nine seconds, about a third of a cent. The
> log records exactly one call, with its seed.

**2:53 – 3:13** — runs.jsonl — one line per call

> Every call lands in runs.jsonl with its model, parameters, seed, latency and
> cost. The whole project, every iteration included, came to about sixty-five
> cents at list prices. The assets in the final film: eleven cents.

**3:13 – 3:37** — What this is not

> What this is not. There is no video model in the film: the clip route is
> implemented and untested. There is no music model: the score is a bed my own
> code synthesises. And the audience test the brief asks for was not run —
> that is written down in DESIGN.md rather than invented.

**3:37 – 3:49** — github.com/mulealem/heritage-short

> The repository, both films and this transcript are linked below. Every
> number in the documentation can be checked against the run log.

## Record it

Record to a single file, 48 kHz, mono or stereo, WAV. On a phone, a
voice-memo app is fine — export it rather than keeping it in the app.

```bash
# 1. record (or export) to walkthrough/vo.wav
# 2. replace the silent track and remux, keeping the subtitle stream
ffmpeg -i walkthrough_silent.mp4 -i vo.wav \
  -map 0:v -map 1:a -map 0:s -c:v copy -c:a aac -b:a 160k -c:s copy \
  walkthrough_final.mp4
```

If your recording runs long or short in one scene, cut or pad that block
rather than speeding the whole track: the picture will not follow a
tempo change.

## If you would rather not use your own voice

The brief does not require your voice — it requires that you explain the
architecture, one hard decision, and a live regeneration. A synthetic
voice reading this same script is honest as long as the video says so;
the repository already discloses which models made which asset. What
would not be honest is a walkthrough that claims a demo it does not show.

## What is on screen, and where it comes from

| scene | source |
|---|---|
| title, stages, limits, end | HTML slides rendered headlessly from this repository |
| 9:16 and 16:9 clips | cut from `outputs/film_9x16.mp4` and `outputs/film_16x9.mp4` |
| the contract | a real excerpt of `storyboard.json` |
| clone, diff, run, log | captured terminal output of the runs described |
| the regenerated image | the actual file those runs produced |

No model was called to make this video: the clips are the film's own
fframes render, and everything else is text, HTML and FFmpeg.
