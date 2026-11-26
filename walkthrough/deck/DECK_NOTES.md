# Walkthrough deck — speaker notes

Twelve slides, 16:9. Present `deck.pdf` full-screen,
talk at your own pace, and record your screen with your voice. There is
no timing to hit: the suggested seconds below are what the same script
takes when read calmly, and nothing breaks if you take twice as long.

The brief wants three things: the architecture, one hard decision, and
one change to the storyboard followed by a rerun that regenerates only
that shot. Slides 4–6 and 9–11 carry those; do not skip 9.

## Recording

1. Open `deck.pdf`, press full-screen, and share that window (not the
   whole desktop — it keeps the aspect tidy).
2. Record with OBS, QuickTime, Game Bar or your phone pointed at the
   screen. Voice and screen together is fine; a separate voice file
   also works.
3. Advance on the sentence, not on a clock. You may pause, backtrack or
   repeat a slide.
4. Keep it under five minutes. If you overshoot, the slide to cut is 2
   or 12 — 9, 10 and 11 must stay.

## The slides

### 1. Eat, My Clothes, Eat!  ·  about 9 s

**Say:**

> This is a walkthrough of Heritage Short: a pipeline that turns one JSON
> storyboard into a finished short film. The film is an Ethiopian folk tale,
> narrated in Amharic with English subtitles.

**Slide:** `slide_01.png`

### 2. 9:16 — 1080×1920 · 89.7 s  ·  about 19 s

**Say:**

> The film is a motion comic. Generated panels are cut and moved like a comic
> page: camera pushes, over-the-shoulder cuts, speech balloons, sound effects,
> word-by-word captions. There is no video model and no GPU in this film; the
> picture is drawn on the CPU in about four minutes.

**Slide:** `slide_02.png`

### 3. 16:9 — the same timeline, a comic page  ·  about 17 s

**Say:**

> The same timeline renders twice. The landscape version is a comic page: the
> panel strip stays centred at full height, the spoken Amharic runs down the
> left margin, the English down the right. One film data file, one audio
> master, two layouts.

**Slide:** `slide_03.png`

### 4. storyboard.json — the contract  ·  about 24 s

**Say:**

> Everything starts from storyboard.json: ten beats, each with a duration, an
> image prompt, a motion prompt, the narration and its English line, a reason,
> and a seed. Beside it, panels.json says how each beat is cut. Every stage
> validates this against the schema before it runs, so a broken contract stops
> the build before a model is called.

**Slide:** `slide_04.png`

### 5. make short — nine stages, one command  ·  about 22 s

**Say:**

> The pipeline is nine stages. Narration records ten lines. Two cast portraits
> anchor the characters. Keyframes and sixteen interaction panels are
> generated from prompts. The build turns them into a timeline, the score is
> synthesised from that timeline, and the picture is rendered in both ratios
> and muxed with one audio master.

**Slide:** `slide_05.png`

### 6. A clone rebuilds both films with no keys  ·  about 20 s

**Say:**

> One command runs all of it. On a fresh clone with no API keys, both films
> rebuild from the committed cache: zero model calls, thirty-nine cache hits,
> about nine minutes including the Rust build.

**Slide:** `slide_06.png`

### 7. The hard decision: a reference is a composition prior  ·  about 26 s

**Say:**

> The hardest problem was keeping a character the same person across
> twenty-six cuts without wrecking the shot. A reference portrait holds the
> face, but it is also a composition prior: attached to a wide shot it
> produced a giant head over a tiny scene. So: anchor the close-ups, and
> describe the wides in full.

**Slide:** `slide_07.png`

### 8. Change one prompt  ·  about 14 s

**Say:**

> Here is the live part. I change one image prompt — one shot, one line of the
> storyboard.

**Slide:** `slide_08.png`

### 9. Rerun the stage: ten cache hits, one call  ·  about 22 s

**Say:**

> Then I rerun the keyframe stage. Ten jobs are served from the cache. One
> image is drawn: seventeen point nine seconds, about a third of a cent. The
> log records exactly one call, with its seed.

**Slide:** `slide_09.png`

### 10. runs.jsonl — one line per call  ·  about 20 s

**Say:**

> Every call lands in runs.jsonl with its model, parameters, seed, latency and
> cost. The whole project, every iteration included, came to about sixty-five
> cents at list prices. The assets in the final film: eleven cents.

**Slide:** `slide_10.png`

### 11. What this is not  ·  about 24 s

**Say:**

> What this is not. There is no video model in the film: the clip route is
> implemented and untested. There is no music model: the score is a bed my own
> code synthesises. And the audience test the brief asks for was not run —
> that is written down in DESIGN.md rather than invented.

**Slide:** `slide_11.png`

### 12. github.com/mulealem/heritage-short  ·  about 12 s

**Say:**

> The repository, both films and this transcript are linked below. Every
> number in the documentation can be checked against the run log.

**Slide:** `slide_12.png`

---

Read end to end the same script runs 229 seconds. The five-minute limit
is not close, so there is room to slow down, or to add one sentence of
your own about why this story matters — that is the part a viewer
remembers, and the part no script can write for you.

## PowerPoint

`deck.pptx` is a native, editable deck: twelve 16:9 slides with real
text boxes, the film stills as images, and **this script in each
slide's speaker notes** — open Presenter View and the words are in
front of you while the audience sees the slide. It is generated by
`node tools/make_deck_pptx.js`, not converted from the PDF.

Use `deck.pptx` if you want to present in PowerPoint, Keynote or
Google Slides; use `deck.pdf` if you only need something that opens
anywhere with the layout guaranteed. Both carry the same twelve
slides, and the notes file here is the same script.

## If you would rather present the HTML

The same slides exist as HTML under `walkthrough/slides/`; open any of
them in a browser and go full-screen. The PNGs in this folder are
identical, and are what the PDF and PPTX contain.
