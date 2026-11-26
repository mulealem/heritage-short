# Report — “Eat, My Clothes, Eat!” (ብሉ ልብሶቼ ብሉ)

B2W0: AI-Content Generation — The Heritage Short

- **Repository:** https://github.com/mulealem/heritage-short
- **Films:** attached to the repository's `v1.0` release — `film_9x16.mp4` (main
  submission) and `film_16x9.mp4`
- **Length:** 89.7 s, both ratios, Amharic narration, English subtitles

---

## 1. What I set out to make, and for whom

A 90-second film of a story my audience already half-knows: the Aleqa Gebre
Hanna folk tale in which a man turned away from a feast for his dusty clothes
returns dressed like a king — and feeds the feast to his clothes. The proverb
that ends it is the one every Habesha household uses on people who judge by
appearance: *judge a person by their character, not their cloth.*

**Audience:** Habesha households — families who grew up on Gebre Hanna
stories — watching on a phone, half of whom already know the ending.
**Intent:** they should laugh, feel the sting (everyone knows a gatekeeper who
judges cloth before character), and leave quoting the line.

**Why this story, and not the first one.** The first draft was a family memory,
“What Are You Seeing?”. I set it aside. The reason is an audience reason: a
family memory asks a stranger to care about people they have never met, while a
tale the audience already knows asks them to enjoy a punchline they are
anticipating — the pleasure is in the re-telling, and everyone in the room is in
on it. `storyboard.english.json` keeps the English-voiced variant of the final
storyboard for comparison.

The result: an 89.7-second motion comic in 9:16 and 16:9, with narration, an
original score ducked under the voice, English subtitles, and an AI end card,
made entirely by a pipeline in code.

## 2. The pipeline

One file, `storyboard.json`, is the contract. `make short` turns it into both
films:

```
validate → narration → cast → keyframes → panels → comic build
         → score → render 9:16 → render 16:9
```

| Stage | Model / tool | What it produces |
|---|---|---|
| narration | Gemini 3.8 Flash TTS (voice Kore) | 10 Amharic lines |
| cast, keyframes, panels | MiniMax image-01, one reference portrait per character | 2 portraits, 11 keyframes, 16 panels — 26 cuts |
| score | my own synthesiser (`tools/make_qenet_bed.py`) | an Ethiopian-pentatonic bed, ducked under the voice |
| picture, mix, mux | fframes (Rust, CPU) + FFmpeg | `film_9x16.mp4`, `film_16x9.mp4` |

Three properties I care about, each of which can be checked rather than taken
on trust:

- **Validated.** Every stage validates the contract against a JSON Schema
  before doing anything, so a broken storyboard stops the run before a model is
  called.
- **Cached.** Each model call is keyed by the sha256 of exactly what was sent.
  Change one prompt, rerun: one call, everything else a cache hit — measured,
  one call at 18.5 s and $0.0035, with ten cache hits (`README.md`).
- **Logged.** `runs.jsonl` has one line per call — model, parameters, seed,
  latency, estimated cost, status. `COSTS.md` is read from it.

**There is no video model in this film.** Wan 2.2 was never run: my MiniMax
plan could not call video at all (`FAILURES.md` F6), and the remaining route was
a Kaggle round-trip I did not complete. So the moving image is a motion comic —
generated panels cut and moved like a comic page: camera pushes and pans,
over-the-shoulder cuts, pop-in balloons, starburst sound effects, word-by-word
captions — drawn on CPU in about four minutes, with no GPU and no video API. The
clip route remains in the repository (`make film`, `kaggle/README.md`) and is
honestly labelled untested.

## 3. What I learned from my audience

**The formal test was not run.** No three-person external test happened before
the deadline, and I am not going to describe one that did not. What happened
instead is a review loop with one person — me, the narrator, inside the intended
audience but also the author, which is the worst position for finding what does
not land. Seven review notes came out of it and each changed the film; they are
recorded in `DESIGN.md` with the change each one caused.

The three things that loop caught, and what it says about the loop:

1. **Framing.** The first comic cut was too tight — close-ups in the mess scene,
   one character per shot. Every beat was rebuilt around a wide establishing cut
   plus interaction and reaction cuts: 26 panels over 10 beats.
2. **Interaction.** Characters were shown one per shot. Adding over-the-shoulder
   and group cuts — the rejection, the host's greeting, the host lunging at
   Gebre Hanna's arm — turned announcements into relationships.
3. **Headwear.** Faces stayed consistent while hats changed between shots. One
   identity directive per character fixed it, and the gatekeeper became
   explicitly bare-headed.

What the missing test cost is stated in `DESIGN.md` and I will not soften it:
nothing in this repository claims that a specific joke or cut worked for a
viewer. All three problems above are exactly what a first-time viewer reports in
one sentence, and I found them late, by re-reading the frames myself. The 89.7 s
runtime against a 60–90 s brief is the same bill: the narration was written for
a slower read than the one it got, which a radio-cut test would have caught
before any picture was drawn.

`DESIGN.md` now carries the twenty-minute protocol — the four questions, in
order, one listener at a time — so the test can be run and appended with real
answers rather than written from imagination.

## 4. The hardest problem, and how I solved it

Keeping one character the same person across 26 cuts, without destroying the
shots.

The standard answer is a reference portrait per character, and it works: with
the portrait attached, the model holds the face across arrival, dismissal and
punchline. But the portrait is not only an identity prior, it is a composition
prior. Attached to a prompt asking for a wide environmental shot, it produced a
giant head over a tiny scene — the gatekeeper's face filling the frame above a
gate he was meant to be standing in. And a single directive written for the hero
leaked his turban onto the bare-headed gatekeeper.

The fix was to stop treating the reference as an identity-only tool and start
treating it as something that belongs to a *kind of shot*:

- one identity directive per character, each naming only that character and
  what must not change;
- the directive and the portrait attached **only to close-up and reaction
  cuts**, where the face is the subject;
- **wide ensemble shots unanchored**, described in full instead, so the model
  composes the scene it was asked for and does not clone one face across a
  crowd.

That cost a full regeneration of the anchored keyframes to learn
(`FAILURES.md` F13, `EXPERIMENTS.md` E9). The same lesson showed up twice more
in smaller ways: unanchored period shots drifted on props (eyeglasses, modern
glassware, a head-wrap on the bare-headed gatekeeper), and red doro wot read as
blood until the wording named visible chicken and egg and said the shamma stays
wrapped closed. The general form of the lesson is in `FAILURES.md`: **a
reference image is a composition prior, not just an identity prior.**

## 5. A suggested practice that beat my instinct, and one that did not

**Beat my instinct — “log every call.”** I expected `runs.jsonl` to be
paperwork. It was the instrument. The per-line durations made a real bug visible:
the model was reading my style instruction aloud before every line, 6–7 seconds
of English per line, 158 seconds of “speech” for a 90-second script
(`FAILURES.md` F11). The latency columns showed a 152-second provider stall for
what it was instead of a mystery. And `COSTS.md` was written by reading the log,
not by remembering.

**Beat my instinct — “validate the storyboard with a schema.”** Checking the
contract before every stage means a bad edit stops the run before money is
spent. It also forced decisions I would otherwise have drifted on: what a beat
is, what a held beat is, what the timing contract carries. When the cut had to
come down to 90 seconds, the fix was two numbers in the storyboard rather than
editing code.

**Did not — “attach the character reference to every shot.”** The brief's
consistency practice assumes a reference fixes identity and nothing else. For
ensemble framing it broke the composition, and the working rule ended up closer
to the opposite: anchor the close-ups, describe the wides. This is the practice
I most wanted to work and most had to overrule.

**Did not — “make the radio cut and test it first.”** I built pictures before
the narration had been played to anyone. The narration-first habit is right and
I skipped it, and the edit-to-time work in `EXPERIMENTS.md` E11 is partly the
bill for skipping it.

## 6. Ceiling work

- **A renderer instead of a video model.** A Rust/fframes motion-comic scene:
  N cuts per beat, camera moves, halftone screens, balloons, SFX, kinetic
  captions, bilingual end card. Zero GPU minutes, zero marginal cost
  (`EXPERIMENTS.md` E3).
- **Bilingual landscape page.** 16:9 is not a letterbox: the same panel strip
  sits at full height with the whole Amharic line in one margin and the English
  in the other, from the same timeline and the same audio master (E12).
- **Edit-to-time as contract.** The narration is fitted to the cut — long pauses
  held to 0.40 s, a 5 % pitch-preserving tempo — from two numbers in the
  storyboard, without re-recording: 99.9 s → 89.7 s (E11).
- **A web editor** to edit every model-facing field and regenerate one keyframe,
  one panel or one line, with a preview of the exact composed prompt.
- **Reproducibility proven by cloning.** A fresh clone with no `.env` rebuilds
  both films: 0 model calls, 39 cache hits, 8 min 19 s including the Rust build.
  That test found two bugs a cache-only run could not (`FAILURES.md` F16, F18,
  F19).
- **An original score from code.** A deterministic qenet bed that follows the
  shot list and thins out for the deadpan (E10).
- **Comparisons.** A paid image model against the free one, same prompts (E1);
  reference conditioning against none (E2).

## 7. What I would build next

1. **Run the audience test and let it change the cut.** The protocol is written
   in `DESIGN.md`; the first thing I would do with another day is the thing I
   skipped.
2. **A real score, then a song.** ACE-Step 1.5 with Amharic lyrics, tested for
   how it pronounces the language; the worker is written and has never run.
3. **Wan 2.2 for two or three shots** — the rejection at the gate and the
   pouring of the tej — to measure what real motion buys over the comic cut.
4. **A tool for family.** A page where a relative types a story and gets the
   same pipeline back, which is the actual reason I built this.

## 8. Limits, stated plainly

- **No external audience test was run** (Section 3). The review loop is
  recorded; it is not a substitute, and it is not described as one.
- **No video model and no music model was run.** 0 GPU minutes. The clip route
  and the music-model route are implemented, documented and labelled untested.
- **The score is synthesised by my code**, not a produced track: a bed, not an
  arrangement.
- **No frontier comparison is claimed.** Nano Banana, Omni Flash and Lyria 3.5
  were behind paid billing I could not attach.
- **Some unanchored panels drift** on period detail (eyeglasses, wine glasses, a
  head-wrap on the gatekeeper, stew that reads strong). Each can be regenerated
  on its own from the editor, at about $0.004 an image.
- **`runs.jsonl` keeps 58 lines from the first hour** of the project
  (`status: "mock"`) from the mock-first scaffold it started as. Everything
  after that is a real call; the log was not rewritten.
