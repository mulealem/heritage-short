# Design: audience, intent, and the two user tests

## Story

"Eat, My Clothes, Eat!" (ብሉ ልብሶቼ ብሉ) — the classic Aleqa Gebre Hanna folk
tale. Turned away from a feast for wearing a dusty gabi, he returns in
gleaming white and gold, is seated as guest of honor — and serves the feast
to his clothes instead of himself: "Eat, my clothes, eat! You invited my
clothes, not me." The film closes on the proverb: judge a person by their
character, not their cloth.

Format: a motion comic (comic panels, balloons, kinetic captions) — the comic
form suits a tale whose whole point is a witty line landing. Narration is
**Amharic**, subtitles and captions English, 9:16 and 16:9, **89.7 s**.

The story was chosen twice. The first draft was a family memory ("What Are
You Seeing?"); the owner set it aside for this folk tale — a story every
Habesha household already half-knows, which is what makes the re-telling a
shared joke rather than information. `storyboard.english.json` keeps an
English-voiced variant of the same storyboard.

## Audience

Habesha households everywhere — families who grew up on Gebre Hanna stories,
plus anyone who loves a sharp folk-tale sting. They watch vertical, on
phones, and half of them already know the punchline; the film's job is to
make the re-telling worth their 90 seconds.

## Intent

They should laugh at the satire and feel its sting: everyone knows a
gatekeeper who judges cloth before character — and they should leave
quoting the punchline. One sentence: *the feast goes to the clothes, so the
clothes eat.*

## How the film is told

- **Amharic spoken, English read.** Voice: Gemini 3.8 Flash TTS, Kore.
- **Ensemble, not portraits.** Every beat pairs a wide establishing cut with
  interaction and reaction cuts — 26 panels over 10 beats — so the social
  theatre (guests smirking, servers frozen, the host lunging) is visible,
  not narrated.
- **Cast consistency.** Two characters, anchored by `outputs/character_refs/`
  portraits (MiniMax image-01 `subject_reference`). Close-up and reaction cuts
  attach that character's anchor plus an identity directive naming only them;
  wide ensemble cuts go unanchored so the model does not clone one face across
  a crowd (`FAILURES.md` F13).
- **Timing from the recording.** The cut is built from measured narration,
  edited to the contract's `meta.timing`: internal pauses held to 0.40 s, a
  5 % pitch-preserving tempo, 0.5 s of air after each line, and held beats
  where the story breathes — the deadpan (1.4 s), the laughing crowd after the
  punchline (2.9 s).
- **16:9 is designed, not letterboxed.** The landscape version is a comic page:
  the panel strip centred, the Amharic line in the left margin, English in the
  right.

## Owner's cut notes (director's review — not the audience test)

These are the owner's own review notes during production, with what changed.
They are one person's notes and do not replace the two three-person tests
below.

| Note (owner's words, condensed) | What changed |
|---|---|
| Too many shots sit too close to the subject — in the mess scene they are close-ups. Wider shots would give context: the environment, how other characters react (guests, servers, bystanders). | Every beat rebuilt around a wide establishing cut; s9 opens on the whole feast table reacting. |
| Shots that show interaction are missing. One character in one shot and another in another shot tells a limited story. | Over-the-shoulder and group cuts: the rejection (s3), the host's greeting (s6), seating and serving (s7), the host lunging (s9), the three-way confrontation (s10). |
| The rejection scene needs more of his reaction and the environment: who is rejecting him, the setting, others' reactions. | s3 is now wide gate confrontation → over-the-shoulder group rejection → his calm turn-away, each with bystanders. |
| The face is consistent, which is great, but the headwear changes — different hats, sometimes none. | One identity directive per character (the turban belongs to Gebre Hanna only; the gatekeeper is bare-headed), and headwear written into every prompt and cast portrait. |
| A weird noise at the end of every narration line. | Trailing TTS burst trimmed (`FAILURES.md` F14). |
| Background music. | An original qenet bed, ducked under the voice (`EXPERIMENTS.md` E10). |

## Test 1 — the first cut, played to at least 3 people

- Status: **not done yet.**
- Who (at least three people from the audience — one who knows the tale, one
  who does not): TODO
- Where/when: TODO
- What they said (quote where possible): TODO
- What changed in the storyboard because of this: TODO

## Test 2 — the near-final cut, played to at least 3 people

- Status: **not done yet.**
- Who: TODO
- What they said: TODO
- What changed: TODO

## Per-shot reasons

Required by the schema (`reason` on every shot) — every shot in
`storyboard.json` states why it exists. When a test says a shot is not doing
its job, change the storyboard, don't defend the shot.
