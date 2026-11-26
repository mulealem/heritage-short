# Report — “Eat, My Clothes, Eat!” (ብሉ ልብሶቼ ብሉ)

*B2W0: AI-Content Generation — The Heritage Short. Draft for the owner to finish:
every block marked **TODO (yours)** needs your own words — the interview checks
that the thinking is yours, and the audience section cannot be written before
the audience tests have happened.*

Owner: [name] · Repository: [public GitHub URL] · Films: [9:16 link] · [16:9 link]

---

## 1. What I set out to make, and for whom

A 90-second short about a story my family already half-knows: the Aleqa Gebre
Hanna folk tale in which a man turned away from a feast for his dusty clothes
returns dressed like a king — and feeds the feast to his clothes. I chose it
over a family memory because the pleasure of a well-known tale is in the
re-telling, and because its punchline is a proverb every Habesha household
uses on people who judge by appearance.

**Audience:** Habesha households — families who grew up on Gebre Hanna stories
— watching on a phone, half of whom already know the ending.
**Intent:** they should laugh, feel the sting (everyone knows a gatekeeper who
judges cloth before character), and leave quoting the line.
**Language:** Amharic narration, English subtitles.

**TODO (yours) — one or two sentences on why *this* story matters to you
personally.** The brief asks for a story that matters to you and your family;
that reason is yours to state.

The result: an 89.7-second motion comic in 9:16 and 16:9, with narration, an
original score ducked under the voice, English subtitles and an AI end card,
made entirely by a pipeline in code.

## 2. The pipeline

One file, `storyboard.json`, is the contract. `make short` turns it into both
films: validate → narration → cast → keyframes → panels → comic build → score
→ render 9:16 → render 16:9.

| Stage | Model / tool | What it produces |
|---|---|---|
| narration | Gemini 3.8 Flash TTS (voice Kore) | 10 Amharic lines |
| cast, keyframes, panels | MiniMax image-01 with one reference portrait per character | 2 portraits, 11 keyframes, 16 panels (26 cuts) |
| score | my own synthesiser (`tools/make_qenet_bed.py`) | an Ethiopian-pentatonic bed, ducked under the voice |
| picture, mix, mux | fframes (Rust, CPU) + FFmpeg | `film_9x16.mp4` and `film_16x9.mp4` |

Three properties I care about and can show:

- **Validated.** Every stage validates the storyboard against a JSON Schema
  before doing anything.
- **Cached.** Each model call is keyed by a hash of exactly what was sent.
  Change one prompt, rerun: one call, everything else a cache hit.
- **Logged.** `runs.jsonl` has one line per call — model, parameters, seed,
  latency, estimated cost. `COSTS.md` is read from it.

I did not use a video model. Wan 2.2 was never run (my MiniMax plan could not
call video at all, `FAILURES.md` F6), so I built the moving image as a motion
comic: generated panels cut and moved like a comic page — camera moves,
over-the-shoulder cuts, speech balloons, sound-effect bursts, word-by-word
captions — drawn deterministically on CPU in about five minutes.

## 3. What I learned from my audience

**TODO (yours).** This section must report the two tests the brief asks for:
the first cut played to at least three people from the audience, and the
near-final cut played to at least three people again — what each person said,
and what in the storyboard changed because of it. The notes belong in
`DESIGN.md` under “Test 1” and “Test 2”. Two honest rules: quote people where
you can, and if something they said did *not* change the film, say so and why.

What I can already say is what changed from the owner's own review during
production (recorded in `DESIGN.md`): the first comic cut was too tight and
too solitary — close-ups in the mess scene, one character per shot — so every
beat was rebuilt around a wide establishing cut plus interaction and reaction
cuts. The audience tests are the next, external version of that loop.

## 4. The hardest problem, and how I solved it

Two candidates are written out below. **TODO (yours): choose one (or name
another), and retell it in your own words.**

**(a) Consistency versus composition.** The reference portrait kept the hero's
face across shots, but it did much more than that: on any wide prompt it
dragged the model into a giant portrait — a huge gatekeeper head over a tiny
scene (`FAILURES.md` F13). And a single identity directive, written for the
hero, leaked his turban onto the bare-headed gatekeeper. The fix was to stop
treating the reference as an identity-only tool. Each character now has his
own directive, and only close-up and reaction cuts are anchored; wide
ensemble shots are described in full and left unanchored. It cost a full
regeneration of the anchored keyframes to learn it.

**(b) Hearing what was not there.** The narrator's Amharic sounded wrong in a
way I could not at first name. Measurement found it twice: the model was
reading my style instruction aloud before every line (F11 — 6–7 s of English
per line, 158 s of “speech” for a 90 s script), and, after that was fixed,
every line ended in a 100 ms burst of full-scale noise (F14). Both were
deterministic, both were invisible in a duration check, and both were found by
looking at the first and last 500 ms of the audio rather than trusting it.

## 5. A suggested practice that beat my instinct — and one that did not

**TODO (yours).** The brief wants one of each, with evidence. Here is the
evidence from the log for each; the judgement is yours to write.

- **Beat my instinct — “log every call.”** I expected `runs.jsonl` to be
  bookkeeping. It was the instrument: the per-line durations made the
  read-aloud style bug visible, the latency columns showed a 152 s provider
  stall for what it was, and `COSTS.md` was written by reading the log rather
  than remembering.
- **Beat my instinct — “validate the storyboard with a schema.”** The contract
  is checked before every stage, so a bad edit stops the run before any money
  is spent; the schema also forced me to decide what a beat *is*.
- **Did not — “attach the character reference to every shot.”** The brief's
  consistency practice assumes a reference fixes identity and nothing else.
  For ensemble framing it broke composition (F13); the working rule became
  the opposite of the instinct — anchor the close-ups, describe the wides.
- **Did not — “make the radio cut and test it first.”** I built pictures before
  the narration had been played to anyone. The narration-first habit is right
  and I skipped it; the edit-to-time work in E11 is partly the bill for that.

## 6. Ceiling work

- **A renderer instead of a video model.** A Rust/fframes motion-comic scene:
  N cuts per beat, camera moves, halftone, balloons, SFX, kinetic captions, a
  bilingual end card. Zero GPU minutes, zero marginal cost (`EXPERIMENTS.md`
  E3).
- **Bilingual landscape page.** 16:9 is not a letterbox: the same panel strip
  sits at full height with the whole Amharic line in one margin and the English
  in the other, from the same timeline and audio master (E12).
- **Edit-to-time as contract.** The narration is fitted to the cut — pauses
  held, a 5 % tempo — from two numbers in the storyboard, without
  re-recording: 99.9 s → 89.7 s (E11).
- **A web editor** to edit every model-facing field and regenerate one
  keyframe, one panel or one line (`tools/editor_server.py`).
- **Reproducibility proven by cloning.** A fresh clone with no credentials
  rebuilds both films: the committed cache is keyed only by what was sent
  (F16).
- **An original score from code.** A deterministic qenet bed that follows the
  shot list (E10).
- **Comparisons.** Paid image model against the free one, same prompts (E1);
  reference conditioning against none (E2).

## 7. What I would build next

- **Run the audience tests properly and let them change the cut.**
- **A real score and a song.** ACE-Step 1.5 with Amharic lyrics, tested for how
  it pronounces the language; the worker is written but has never run.
- **Wan 2.2 for two or three shots** — the gate rejection and the pouring of
  the tej — to measure what real motion buys over the comic cut.
- **A tool for family:** a small page where a relative types a story and gets
  the same pipeline back.

## 8. Limits, stated plainly

- The two three-person audience tests are not yet done (Section 3).
- No video model and no music model was run; 0 GPU minutes.
- The score is synthesised by my code, not a produced track.
- No frontier model was available, so no frontier comparison is claimed.
- A few unanchored panels drift on period details (eyeglasses, a head-wrap on
  the gatekeeper); each can be regenerated on its own from the editor.

- The comic picture is re-rendered whole (about five minutes); what is cached
  per shot is every model call behind it.
