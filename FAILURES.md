# Failures: what broke, what was tried, what fixed it

Real blockers only — quota, memory, consistency, language, tooling that moved.
This file is graded: what earns marks is the honest loop of break → try → fix.

## Template

```
### F1: <what broke>
- When/symptom: ...
- What I tried: ...
- Fix or workaround: ...
- Lesson: ...
```

## Known-so-far

- This dev machine has no GPU and a broken `pip3` → the whole pipeline was
  written stdlib-only on purpose; GPU stages run on Kaggle (see kaggle/README.md).
- FFmpeg here is 4.2.7: no `xfade` (hard cuts + fades instead), no `gradients`
  lavfi source (the end card uses `color` + drawtext). Version-pinning matters:
  record the exact version any filter assumption depends on.

### F1: `gemini-2.5-flash` retired for new users (404 on first real call)
- When/symptom: 2026-11-25, `make preflight` — text smoke call returned
  `404: This model models/gemini-2.5-flash is no longer available to new
  users. Please update your code to use models/gemini-3.8-flash`.
- What I tried: the call as written (model name from `.env.example` defaults).
- Fix or workaround: `GEMINI_TEXT_MODEL=gemini-3.8-flash` in `.env`.
  Affects only the optional script-drafting stage; `gemini-2.5-flash-preview-tts`
  still works for narration. Second call hit `503 high demand` — transient,
  retried later.
- Lesson: the .env.example comment ("free-tier model names change often") was
  right. Smallest possible fix: model names stay env-configurable; never
  hardcode them in code.

### F2: Cloudflare renamed `flux-schnell` → `flux-1-schnell` and dropped width/height/seed
- When/symptom: 2026-11-25, `make preflight` — `400: No route for that URI`
  for `@cf/black-forest-labs/flux-schnell` (the model card URL everyone has
  bookmarked is gone).
- What I tried: (1) listed the live catalog via
  `ai/models/search` with the account token — 337 models, the renamed route
  is `flux-1-schnell`; (2) called it — `400: Additional or unevaluated
  properties '/width, /height' not allowed`: the renamed model accepts ONLY
  `prompt` + `steps` (checked schema-input.json: `additionalProperties: false`).
  No dimensions = no portrait keyframes; no seed = no reproducibility.
- Fix or workaround: switched the keyframes stage to
  `@cf/black-forest-labs/flux-2-klein-4b` (newer gen, ~$0.0012/image at
  720×1280). It requires multipart/form-data — added `net.http_multipart`
  (stdlib, same retry/backoff) and transport selection by model prefix.
  Verified live: 720×1280 returned exactly, seed accepted. It returns JPEG
  bytes; consumers sniff content so the `.png` contract names stay.
- Lesson: model routes on a hosted API are not stable identifiers. Catalog
  query beats bookmark; schemas drift independently of names. Seed-diff
  experiments must note that different model = different weights.

### F3: Gemini TTS free tier = 10 requests/day (quota wall, mid-run)
- When/symptom: 2026-11-26, regenerating narration for the new storyboard —
  shot 1 generated fine, shot 2 returned `429: Quota exceeded for metric
  generate_content_free_tier_requests, limit: 10/day` with retry in 3h31m.
- What I tried: rerunning immediately (the stage hard-stopped instead of
  faking, by design); counting calls: 8 narration + 2 smoke calls the same
  day had already spent the daily 10.
- Fix or workaround: content-hash caching means shot 1 is a permanent cache
  hit; wait out the daily window and rerun `make narration` — 7 calls remain,
  which fits. No billing change needed for one film; a second same-day
  iteration would need paid tier.
- Lesson: design budgets per-day, not per-run. The cache makes the quota
  wall cheap: a failed 8-shot run resumes with 7 fresh calls, not 8. The
  hard-stop (no mock tone) is what kept fake audio out of a real film.

### F4: Cloudflare safety filter false-positive on the closing keyframe
- When/symptom: 2026-11-26, `make keyframes` — 8 of 9 images fine; s8_memory
  returned `400 code 3030: "Your output has been flagged. Please choose
  another prompt / input image combination"`.
- What I tried: rerunning as-is (the stage hard-stopped, no placeholder).
  The prompt described "the round-cheeked boy now a grown man laughing with
  his sisters" — the child→adult phrasing almost certainly tripped the
  classifier; the image itself (family laughing at a wedding) is benign.
- Fix or workaround: reworded the prompt to describe the adult directly
  ("an Ethiopian man in his thirties laughing warmly with his two older
  sisters") — no child wording at all. Regenerated on the spot; the other 8
  frames were cache hits and cost nothing.
- Lesson: content filters read prompts literally. When a benign idea trips
  one, rewrite the description, not the idea — and keep the flagged prompt
  in git history as the receipt.

### F5: composition drift — "two kids on a chair" needed three prompts
- When/symptom: 2026-11-26, keyframe s3_doorway (the film's signature shot:
  two sisters elevated at the doorway watching the wedding). Attempt 1
  ("perched on top of the doorframe") produced girls floating mid-air with
  dangling feet — the user caught it. Attempt 2 ("standing on a wooden
  chair") added a phantom seated adult on the chair. Attempt 3 ("standing on
  the chair, no adults") dropped them onto the floor hugging beside an empty
  chair, with a market street instead of the wedding.
- What I tried: progressively more explicit grounding geometry; naming the
  furniture ("chair") made the model add a sitter; re-asserting "no adults"
  pushed the girls off the furniture entirely.
- Fix or workaround: switched furniture to a *bench* (wide enough for two
  figures to stand side by side, no seating affordance to sit on), shot
  from behind, and named the beyond-the-door content explicitly ("wedding
  guests in white and a bride"). Fourth prompt landed: feet on bench, one
  sister's arm around the other, wedding visible through the door.
- Lesson: image models treat "on X" as a loose spatial hint, not a physical
  constraint. Wider platforms beat narrow ones for multi-figure grounding,
  and every element you DON'T re-anchor gets re-invented — including people.
  Each iteration cost ~$0.0012 and one cache entry; the failed prompts stay
  in git as the iteration log.
### F6: MiniMax "M Plan" (sk-cp-…) key is text-models-only — no video
- When/symptom: 2026-11-26, wiring `tools/minimax_clips.py` for Hailuo I2V.
  The key authenticates (no 401), but every video route refuses:
  `v2` + MiniMax-H3 → 402 "The current Token Plan tier does not support this
  model" (2068); `v1` + video-01/I2V-01/Hailuo-02 → 2056 "Token Plan usage
  limit reached: Upgrade your Token Plan or purchase Credits".
- What I tried: probing v2 with 6 model names (H3, Hailuo-02/2.3, T2V/I2V-01
  variants), v1 with the classic payloads, and `GET /v1/models` — the key's
  entitlement list is MiniMax-M* text/coding models only. The `sk-cp-` prefix
  means Coding Plan: LLM tokens, not video credits.
- Fix or workaround: keep `tools/minimax_clips.py` (it is correct and
  resume-safe, and will work the moment the account has video credits); use
  the free Kaggle/Wan worker for this film, or buy a video credit pack.
  Cost if credits are added: H3 ≈ $0.07–0.12/s, ~65 s of clips ≈ $5–8.
- Lesson: "I have a subscription" ≠ "my API key can call the model". Probe
  entitlements with GET /v1/models and a one-shot submit before building a
  provider against a plan; plan tiers, not keys, gate model access.
### F7: adopting fframes (comic renderer) — the release is broken, the RC works
- When/symptom: 2026-11-26, `cargo fframes new` + `cargo build --release`:
  (a) fframes 1.4.0 fails to compile — its own dep `fframes-media 1.4.1`
  requires usvgr 0.50 while fframes 1.4.0 requires 0.46 (12 type errors);
  (b) after switching to the release candidate `=1.4.2-rc.11`, compile passes
  but the link fails: `undefined symbol: x264_encoder_open_163` — the
  prebuilt libavcodec was built against x264 build 163 (Ubuntu 22.04's
  libx264), while this box has 155 (system) and 165 (/usr/local).
- What I tried: pinned the RC (whose whole graph is on usvgr 0.50.3);
  confirmed the missing ABI symbol; checked `nm -D` on both installed x264s
  (they export `_165` and `_155` only — x264 version-symbols are ABI-exact,
  so no version can substitute for another).
- Fix or workaround: built x264 at the exact ABI commit (`5db6aa6`,
  X264_BUILD 163) statically into `/opt/x264-163`, and added
  `rustflags = ["-L", "native=/opt/x264-163/lib"]` in the project's
  `.cargo/config.toml` (a static-only prefix wins over the system .so, and
  the other session's /usr/local x264-165 is left untouched).
- Result: 120 frames at 1080x1920/24fps rendered in 20.3 s on CPU
  (tiny-skia), h264+aac muxed by the bundled libav — ~0.17x realtime, so a
  90 s film is ~6 min. Raster panels (`ctx.get_image`), multi-track audio
  (`AudioTrack`), spring easings and SVG shapes all verified in one scene.
- Lesson: agent-facing 2026 tooling ships fast but shallow: "latest stable"
  can be unbuildable while the RC is fine, and binary deps pin exact ABI
  symbols. Pin versions, isolate ABI-matched builds in private prefixes,
  never overwrite system libraries a parallel session may rely on.
### F8: Cloudflare's free 10,000 neurons/day ran out mid-restyle (4006)
- When/symptom: 2026-11-26, re-styling the comic to a Spider-Verse palette —
  after ~25 images the API returned `429 ... you have used up your daily free
  allocation of 10,000 neurons`.
- What I tried: reducing sizes and steps (the wall is per neuron, roughly per
  512×512 tile), and waiting.
- Fix or workaround: switched `IMAGE_PROVIDER` to MiniMax image-01, which the
  M-plan key *is* entitled for (verified with one call). The Cloudflare path
  stays in the code as the free draft option; its sidecars are separate.
- Lesson: free allowances are per day per account, not per project — budget
  iterations, not final outputs. A paid provider at $0.0035/image removed the
  ceiling entirely.

### F9: MiniMax's Music API is closed to new users (410)
- When/symptom: probing `/v1/music_generation` with music-01 / 1.5 →
  `410 ... This Music API is no longer available to new users. Existing paying
  customers can continue.`
- What I tried: three model names with a valid paid image key.
- Fix or workaround: keep ACE-Step 1.5 on Kaggle for the score (free, already
  wired); the comic film ships as the radio cut until that notebook runs.
- Lesson: "the same vendor" does not mean "the same entitlement". Probe each
  endpoint once before writing it into a plan.

### F10: TTS also has a per-minute cap (3 req/min), not just 10/day
- When/symptom: 2026-11-26 08:01, the daily window reset and narration resumed —
  six lines rendered, then `429 ... limit: 3, model: gemini-2.5-flash-tts ...
  requests per minute ... retry in 51.7s`. The stage's 3 retries (max 30 s
  backoff) are shorter than the window.
- What I tried: rerunning immediately (fails on the same minute), then pacing.
- Fix or workaround: added `TTS_SECONDS_BETWEEN_CALLS` pacing (default 21 s)
  in `pipeline/narration.py` after each real call; reruns are cache hits, so a
  walled run resumes with only the missing lines. The 10 lines then completed
  in ~3 minutes.
- Lesson: free tiers often have *three* simultaneous limits (per minute, per
  day, per model). Pace inside the stage instead of relying on transport
  retries, and make every model call cacheable so a wall costs only the
  calls not yet made.
### F11: Gemini TTS read the style instruction aloud before every line
- When/symptom: the user heard an English sentence ("a warm Amharic folk
  storyteller, playful and theatrical ...") before every Amharic line, so each
  file played a spoken production note then the narration.
- Cause: `narration.py` sent `style + ":

" + text` as the TTS prompt. A
  bare descriptive phrase is not an instruction to this model — it reads it.
  Detection: silencedetect showed a uniform speech block of ~6-7 s followed by
  a 0.5-1.3 s pause at the start of all ten files; total speech 158 s.
- Fix: (a) cut the prefix at that first pause with `tools/trim_tts_prefix.py`
  (every edit logged; Amharic left intact, speech 158 s -> 89.7 s);
  (b) stop sending style as prose — `TTS_STYLE_PREFIX` is empty by default and
  tone comes from the voice; (c) `TTS_CACHE_VERSION` added so the next
  re-record can force new synthesis instead of hitting the trimmed cache.
- Lesson: TTS "style" must be written as a direction or omitted; listen to the
  first generated line before batching the rest. Silence detection is a cheap,
  reliable way to locate a spoken prefix.
### F12: MiniMax image credits also have a plan cap (2056)
- When/symptom: while adding reaction/two-shot panels, image-01 began returning
  `2056 Token Plan usage limit reached` after ~85 images across the day
  (keyframes + inserts + cast + iterations).
- What I tried: rerunning (fails), checking the models endpoint (fine — it is a
  usage cap, not entitlement).
- Fix or workaround: the renderer skips panels whose files are absent, so the
  film ships with the panels that exist; the remaining 8 extras are queued for
  the next plan window. Cloudflare's free path is also daily-capped (F8).
- Lesson: budget paid image quotas like GPU hours — one restyle can eat a
  day's allowance. Generate the final prompt set once, then iterate text.
- TODO: OOM on Kaggle T4, character drift across shots, TTS mispronouncing
  place names in your language — as they happen.

### F13: subject_reference destroys wide framing; unanchored wides drift on props
- When/symptom: 2026-11-26, after the ensemble revision. A "wide environmental
  two-shot" prompt plus the gatekeeper portrait produced a giant gatekeeper
  head over a tiny scene; the s9 wide plus Gebre Hanna's portrait produced a
  portrait-and-collage. Re-running the same prompts with `actor: null` gave the
  intended wide staging. Separately, unanchored period panels kept inventing
  eyeglasses, a head-wrap on the bare-headed gatekeeper, wine glasses and
  cutlery, and red doro wot that reads as blood on white cloth.
- What I tried: refs on every cut (bad composition), refs on none (face drift),
  and wording like "no eyeglasses" (often ignored or summoned the object).
- Fix or workaround: anchors only on close-up/reaction cuts; wide bases are
  described with period props (woven mesob, reed mats, berele flask); food
  stains named with visible chicken/egg and "shamma stays wrapped closed";
  failed panels are re-rolled per asset in the editor.
- Lesson: a reference portrait is a composition prior, not just an identity
  prior. Treat "wide" and "referenced" as mutually exclusive.

### F14: Gemini TTS appends a 100 ms full-scale noise burst to every line
- When/symptom: 2026-11-26, after the upgraded narration was recorded. The
  user heard "trailing static" at the end of every line. Sample analysis showed
  the last 100 ms of every WAV at −9…−3 dBFS (peak 0 dBFS), preceded by a block
  of digital silence; it was identical in all ten files and is not speech.
- What I tried: `silencedetect` (no help — the burst is loud), then a per-block
  RMS scan. The first trimmer walked back with a −35 dB threshold and stopped
  inside the burst ramp, leaving 20–40 ms behind; a −45 dB threshold fixed it.
- Fix or workaround: `pipeline.narration.trim_terminal_burst()` detects the
  terminal loud run, requires a quiet gap before it, cuts 10 ms before the
  burst and applies a 10 ms fade. The narration stage calls it after every TTS
  response; `tools/clean_narration_tails.py` cleans existing files and refreshes
  `durations.json`.
- Lesson: treat model audio as untrusted at both ends. The prefix bug (F11) and
  this tail bug were both deterministic; inspect first/last 500 ms, not just
  duration.

### F15: the full-mix path had never run — and wrote master.wav onto itself
- When/symptom: 2026-11-26, the first render with a score. FFmpeg refused:
  `Output master.wav same as Input #0 - exiting`.
- What I tried: rerun (same), then read the mix code.
- Cause: `build_audio_master` wrote the mix to `master.wav`, then ran its
  two-pass loudnorm reading `master.wav` and writing `master.wav`. The path
  had never executed, because no score existed until that day; the radio-cut
  path carried its own, correct copy of the same logic.
- Fix or workaround: an intermediate `mix_raw.wav`; and `python3 -m
  pipeline.comic remux`, which re-mixes audio over an existing picture in
  about 20 s instead of a 5-minute re-render.
- Lesson: a code path that has never run is untested code, however simple it
  looks. Under "real only", a path stays untested until its input exists — so
  exercise it the first time the input appears, and do not keep two copies of
  shared logic.

### F16: the cache did not survive a clean clone, and the "one command" could not make the film
- When/symptom: 2026-11-26, auditing the repository against the brief before
  submission. The README called `make film` the one command; it needs Wan
  clips from Kaggle and stops at `shots`. `make comic` assumed every asset
  already existed. No single command regenerated the film.
- What I tried: traced one cache key by hand. The stage hashed the model
  token `@cf/black-forest-labs/flux-2-klein-4b` for an image that image-01
  drew (the token came from `CF_FLUX_MODEL` in `.env`); the exporter assumed a
  different token; a clone without a `.env` hashed a third. On top of that,
  stages demanded API keys before looking at the cache, and only `make film`
  validated the storyboard.
- Fix or workaround: `make short` chains the stages that make the film
  (validate → narration → cast → keyframes → panels → comic build → score →
  render 9:16 → render 16:9). `common.load_storyboard()` validates for every
  stage. The model token in a cache key is owned by the provider (`image-01`)
  and read from no unrelated setting. Keys are requested only on a real miss.
  The 11 keyframe sidecars were re-signed to the new token — and the sanity
  check refused the one anchored keyframe, because my migration had dropped
  its identity directive from the hashed prompt; redone with it. Proof: a
  fresh clone with no `.env` ran `make short` end to end — 0 model calls, 39
  cache hits, 0 errors, 8 min 19 s from clone to both films, Rust build
  included. (That run also exposed F18.)
- Lesson: reproducibility is a property of the whole path — env, keys,
  validation, build — and it is only proven by cloning.

### F17: two renders of the same frames were not byte-identical
- When/symptom: 2026-11-26. After adding the 16:9 layout to the renderer I
  re-rendered 9:16 to prove the vertical path unchanged: 2,079 of 2,151 frames
  bit-identical, 72 different, in three 24-frame windows (PSNR 36.7 dB).
- What I tried: per-frame MD5, PSNR, a difference image (fine speckle on the
  halftone dots only; nothing in text or shapes; frames on either side of each
  window identical), then the fframes encoder source: it renders in parallel
  GOP-sized chunks (`split_gop_chunks`) whose boundaries depend on available
  concurrency. The first render had overlapped a cargo build.
- Fix or workaround: none needed. The drawn frames are deterministic; the
  encoded file is not bit-reproducible, and the seams are the encoder's own
  chunk joins, present in every render.
- Lesson: "deterministic" needs a unit — frames yes, bytes no. Measure before
  claiming either.

### F18: the timeline depended on whether the narration edit was cached
- When/symptom: 2026-11-26, found by the clean-clone test. The clone's films
  passed every check, but 1,765 of 2,151 encoded frames differed from the
  working copy's. Comparing the frames the renderer *draws* (PNG, before
  encoding) showed 5 of 7 differing by 1–2 levels on up to 4 % of pixels, and
  `film.json` differed by a millisecond: shot start `15.567` in the clone,
  `15.56725` in the working copy.
- What I tried: compared the fitted WAVs (byte-identical), the fitted durations
  (identical), then the two code paths that produce them.
- Cause: `ensure_fit` returned durations rounded to 3 decimals when it had just
  fitted the lines (`fit_s`) and unrounded ones when it loaded them from its
  own cache (`probe_duration`). A fresh clone always takes the first path, my
  working copy the second — so the cut shifted by up to 1 ms, and the camera
  moves with it.
- Fix or workaround: both paths now measure the file. Re-test: a clean clone
  with a fresh fit builds a `film.json` byte-identical to the working copy's,
  and 7 of 7 sampled frames are byte-identical in both layouts.
- Lesson: a cache must return the same value it computed, bit for bit. Two
  code paths that "mean the same thing" are two answers. This is exactly why
  the brief asks for the clean-clone run.

### F19: the uncached path of the keyframe stage crashed — and only a real call could show it
- When/symptom: 2026-11-26. Testing "change one prompt, make one call" in a
  clone: with the key present, `python3 -m pipeline.keyframes` died with
  `NameError: name 'minimax_image' is not defined` instead of drawing the
  image.
- What I tried: read the traceback. While making the stage ask for its key only
  on a cache miss (F16) I moved the key check into a helper and, with it,
  dropped the `from pipeline.minimax_image import minimax_image` line that
  lived beside it.
- Why nothing caught it: the clean-clone run passes with every asset cached,
  so the miss path never executed; and the error was a `NameError` outside the
  `except RuntimeError` that logs failures, so it left no line in `runs.jsonl`.
- Fix or workaround: import restored. Re-test in a clone: with one prompt
  changed and no key, the stage asks for the key; with the key, it makes
  exactly one call (image-01, 18.5 s, $0.0035) and reports ten cache hits.
- Lesson: a reproducibility test that only replays cache hits proves the cache,
  not the pipeline. Exercise the miss path with a real call before a live demo.
