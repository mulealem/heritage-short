# Experiments

Hypothesis → change → result. Seeds and prompts are in the repo; numbers come
from `runs.jsonl`.

### E1: paid image model vs free draft model for the comic look
- Hypothesis: at ~$0.0035/image, MiniMax image-01 buys visibly better comic
  art than Cloudflare FLUX-2 klein's free daily allowance.
- Change: same prompts and style block, `IMAGE_PROVIDER` switched between
  `cloudflare` and `minimax`; 720×1280, fixed seeds.
- Result: both produce the style; image-01 renders stronger ink contours and
  halftone/splatter texture at full 720×1280 (median 19 s). Cloudflare hit the
  10,000-neuron daily wall after ~25 images (`429`, F-code 4006), which was
  the deciding operational factor.
- Decision: image-01 is the production provider; Cloudflare stays as the free
  draft path in code.

### E2: subject_reference for face consistency
- Hypothesis: attaching one character portrait (`subject_reference`) keeps
  Gebre Hanna and the Gatekeeper recognisable across shots.
- Change: `tools/comic_cast.py` produced two anchors; shots s2/s3/s5/s6/s8/s10
  regenerate with the anchor attached.
- Result: identity holds (same face in arrival, dismissal and punchline), but
  the model drifts toward painterly semi-realism and starts ignoring costume
  details (s10 lost the food stains). A "redraw as flat-colour comic" directive
  restored most of the style; stain wording had to be re-emphasised.
- Decision: keep references for identity, keep the directive, and write
  costume-critical details into the prompt explicitly.

### E3: motion comic on CPU vs video-model clips
- Hypothesis: a deterministic panel renderer can replace AI video for this
  folk tale at a fraction of the cost and risk.
- Change: fframes (Rust, tiny-skia CPU) scene with camera moves, insert cuts,
  balloons and kinetic captions; same storyboard, narration and score.
- Result: 84 s film, 2016 frames at 1080×1920/24 fps, ~5 minutes CPU, no GPU,
  no video API, $0 marginal cost. (Later cuts ran 99.9 s and then 89.7 s —
  see E11.) Hailuo video would have cost ~$5–8 for 65 s
  of clips — and the M-plan key could not call it at all (F6).
- Decision: comic is the film's renderer; `assemble.py` remains for real-clip
  films and for the challenge's video route.

### E4: TTS model bump under quota pressure
- Hypothesis: `gemini-3.8-flash-tts` matches the older model's delivery while
  the free TTS quota is 10 requests/day.
- Change: `GEMINI_TTS_MODEL` bumped; same text, voice Kore.
- Result: 3.6 s average vs 6.9 s per line (7 calls measured). Listening test
  pending — that is a subjective call for the family.
- Decision: keep the newer model; record the listen test in DESIGN.md.

### E5: insert-panel cuts at 55 % of a shot
- Hypothesis: cutting to a second detail panel mid-shot reads as comic motion
  rather than a slideshow.
- Change: one generated insert per shot, `insert_at = 0.55`, white cut flash.
- Result: works; the frame rate of "information" roughly doubles. Un-referenced
  inserts drift in face identity (the gatekeeper insert did not match his
  keyframe), so inserts now inherit the shot's cast reference.
- Decision: keep, with references on character inserts.

### E6: deterministic comic-print post-process (rejected)
- Hypothesis: posterize + edge multiply + halftone overlay would unify the
  painterly referenced panels with the ink panels.
- Change: PIL pass tested on s1 and s10.
- Result: s10 only slightly inkier; s1 lost shadow detail badly (faces crushed
  to black). Rejected — the renderer's own halftone overlay and ink border
  already unify the look on screen.
- Decision: no post-process; spend the effort on prompts instead.

### E7 (open): the radio cut
- Hypothesis: narration alone carries the story before any picture spend.
- Change: `make narration` then listen without images.
- Result: pending — the narrator voice and pacing are the user's subjective
  call (Test 1 in DESIGN.md).

### E8: Amharic narration with English subtitles
- Hypothesis: the same storyboard can be voiced in Amharic while the soft
  subtitle track and on-screen captions stay English (`narration.en`).
- Change: `narration.text` → Amharic, `narration.en` → the English line,
  `meta.narration_language = "am"`, voice model `gemini-3.8-flash-tts`.
- Result: Gemini's native TTS does speak Amharic (the 24-language list on
  third-party wrappers is wrong; the native model covers it). The first cut
  measured **158.2 s** — but 6–7 s per line turned out to be the style
  instruction being read aloud (F11), not slow Amharic. After trimming that
  prefix the real speech was **89.7 s** for 10 lines. The upgraded, idiomatic
  script was then re-recorded with a second free-tier key at **86.1 s** of
  raw speech (no prefix sent); after trimming the F14 terminal burst it is
  **84.4 s**, and assembles to **99.9 s** with pads + end card.
  Captions/subtitles correctly stayed English.
- Decision: ship the Amharic cut; keep the English storyboard
  (`storyboard.english.json`) for comparison.

### E9: ensemble revision — 26 cuts, per-character directives, unanchored wides
- Hypothesis: the film reads as a comic *story* (relationships, crowd reaction,
  social theatre) rather than a slideshow of solo portraits if every beat pairs
  a wide establishing cut with interaction and reaction cuts.
- Change: all 10 beats re-cut into 26 panels (base + 1–2 extras), each beat gets
  a camera move, balloons timed to the line, and up to two SFX. Identity
  directives split per character (A: Gebre Hanna's turban; B: bare-headed
  gatekeeper). Anchors are attached only to close-up/reaction cuts; wide
  ensemble cuts are unanchored with full period descriptions.
- Result: wide framing and interaction read clearly (s2 arrival, s3 OTS
  rejection, s5 hero reveal, s6 bow, s7 seating, s8 frozen room, s10
  confrontation). But `subject_reference` on a wide prompt pulls the model into
  a portrait/collage — s3/s6/s9 bases had to be regenerated without anchors.
  Unanchored cuts drift on small period details the prompt does not force:
  eyeglasses on the host, a head-wrap on the gatekeeper, modern glassware, and
  red doro wot reading as blood until the wording named visible chicken/egg and
  "stays wrapped closed".
- Decision: keep the 26-cut grammar; anchors on close-ups only. Treat red-stew
  wording and "no eyeglasses / bare-headed / period props" as per-panel fixes in
  the editor, not global prompt laws.

### E10: a hand-synthesized qenet bed while ACE-Step is pending
- Hypothesis: a fixed, low-level Ethiopian-pentatonic bed is better than
  silence for a 100 s narration cut, and can be produced deterministically on
  this machine without a GPU or a model entitlement.
- Change: `tools/make_qenet_bed.py` synthesizes 24 kHz mono audio at 118 BPM —
  A1/A2 drone, kebero pattern, masinko-like bowed/plucked phrases in A minor
  pentatonic, washint long tones, a light shaker and three-tap reverb. Intensity
  follows the shot list (drops for `s8_deadpan`, returns for the feast and
  punchline). It writes `score_final.wav` plus `score_source.txt`
  (`qenet-bed-v1`), and `MUSIC_LUFS` (default −24) sets the bed level before the
  sidechain duck.
- Result: the film is no longer voice-only; the bed is a real, reproducible
  composition, but it is synthesized, not ACE-Step. It may read as a
  drone-and-pulse cue rather than a produced score; the mix is deliberately low
  so narration stays in front.
- Decision: ship it as the current static bed. ACE-Step remains the upgrade
  path: replace `score_final.wav`, delete `score_source.txt`, and rerun
  `make comic`; `make music` will log the Kaggle source again.

### E11: edit-to-time — fit the narration to the brief's 90 s without re-recording
- Hypothesis: the film could come down from 99.9 s to the brief's 90 s cap
  without changing a word or a voice take, by holding long internal pauses and
  applying a tempo small enough to be inaudible.
- Change: measured the pauses first — 6.8 s of the 84.4 s of speech sat in
  internal pauses of 0.30–0.90 s. A new `meta.timing` block in the storyboard
  carries the edit as contract: pauses held to 0.40 s, tempo 1.05, 0.5 s of air
  after each line, 3 s end card. Three beats are deliberately held (the
  opening, the deadpan, the laughing crowd after the punchline). The raw WAVs
  are never modified; the fitted lines live in `outputs/narration_fit/`.
- Result: speech 84.4 s → 77.8 s; film 99.9 s → 89.7 s. A first attempt at
  tempo 1.035 came out at 91 s once the held beats were kept: the holds cost
  3.9 s and are what make the deadpan and the punchline land, so they stayed
  and the tempo took the rest. Whether it sounds hurried is an ear judgement
  and is the owner's call (listen test pending).
- Decision: ship at 89.7 s. Tempo and pause cap are two numbers in the
  storyboard, so the cut can be re-fitted in seconds.

### E12: 16:9 as a comic page instead of a letterbox
- Hypothesis: a landscape version can be more than the vertical film centred
  on a wide canvas: keep the panel strip at full height and give the margins
  to the two languages.
- Change: a cargo feature `wide` compiles the renderer for 1920×1080. The
  stage (where the panel lives) becomes a 608×1080 strip in the centre; the
  spoken Amharic line sits in the left margin (Noto Sans Ethiopic), the English
  subtitle in the right; balloons and SFX stay inside the strip, and the
  margins are painted after the stage so nothing bleeds out. One `film.json`
  and one audio master serve both layouts.
- Result: both films are 89.7 s from the same timeline. Frame checks at 22 s,
  50 s, 74.5 s, 86 s and 88.5 s: text blocks of 7–9 lines at 40–46 px, readable;
  balloons shrink to about 36 px inside the narrow strip, which is the cost of
  the layout. The vertical path is unchanged in source (F17 measures it).
- Decision: ship both. The landscape page is the bilingual one — the whole
  Amharic line is on screen — and the vertical keeps the kinetic captions.

