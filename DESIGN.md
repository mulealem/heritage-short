# Design: audience, intent, and what review changed

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

## Owner's review notes — the tests that were actually run

These are the real review notes taken during production, in the owner's words,
with what changed in the storyboard because of each. They are review sessions
between the owner (the narrator, who is also the audience this film was made
for) and the build, one person with the film in front of them, repeated over
two days. They are not the three-person audience test the brief asks for, and
they are not presented as one.

| # | Note | What changed |
|---|---|---|
| 1 | Too many shots sit too close to the subject — in the mess scene they are close-ups. Wider shots would give context: the environment, how other characters react (guests, servers, bystanders). | Every beat rebuilt around a wide establishing cut; s9 opens on the whole feast table reacting before the smear. |
| 2 | Shots that show interaction are missing. One character in one shot and another in another shot tells a limited story. | Over-the-shoulder and group cuts added: the rejection (s3), the host's greeting (s6), seating and serving (s7), the host lunging (s9), the three-way confrontation (s10). |
| 3 | The rejection scene needs more of his reaction and the environment: who is rejecting him, the setting, others' reactions. | s3 became three cuts: wide gate confrontation → over-the-shoulder group rejection → his calm turn-away, each with bystanders in frame. |
| 4 | The face is consistent, which is great, but the headwear changes — different hats, sometimes none. | One identity directive per character (the turban belongs to Gebre Hanna only; the gatekeeper is bare-headed), and headwear written into every prompt and into both cast portraits. |
| 5 | A weird noise at the end of every narration line. | The TTS terminal burst is trimmed (`FAILURES.md` F14). |
| 6 | Background music. | An original qenet bed, ducked under the voice (`EXPERIMENTS.md` E10). |
| 7 | The story itself: the family-memory draft was set aside in favour of the folk tale, because a story the audience already half-knows makes the re-telling a shared joke rather than information. | `storyboard.json` rewritten around the Gebre Hanna tale (`storyboard.english.json` keeps an English-voiced variant). |

Note 7 is the largest decision in the project, and it came from the audience
reasoning rather than from a test: the first draft asked a stranger to care
about a family they had never met, while the tale asks them to enjoy a punchline
they already know.

## What was not done, and what it cost

**No three-person external test was run before the deadline.** The film was
reviewed repeatedly by one person — the owner, who is inside the intended
audience (a Habesha household, Amharic-speaking, raised on these tales) but is
also the author, which is the worst possible position for finding what does not
land. That is a real gap, and it is recorded here rather than filled with
invented reactions.

What the gap cost, concretely:

- Nothing here can claim that a specific joke, cut or line worked. The
  evidence in this file is what changed, not what a room full of people said.
- The three things a test would most likely have caught were instead caught
  late, by the owner and by measurement: the too-tight framing (note 1), the
  headwear drift (note 4), and the trailing audio noise (note 5) — all of which
  a first-time viewer would have reported in one sentence.
- The film is 89.7 s against a 60–90 s brief because the narration was written
  for a slower read than the one it got; a test at the radio-cut stage would
  have caught that before any picture was drawn (`EXPERIMENTS.md` E11 is the
  bill for skipping it).

## The test that would run next, in twenty minutes

Written down so it can be run and appended here with real answers. Three
people, no more than that per round, one at a time, phone in hand.

1. Play the 9:16 film once, without saying what it is. Say nothing during it.
2. Ask, in this order, and write the answers down verbatim:
   - *What happened in that story?* (tests whether the plot read without
     subtitles)
   - *What was the funniest moment?* (tests whether the punchline landed, and
     where)
   - *Was there a moment you looked away or got lost?* (tests pacing and the
     cuts)
   - *Who would you send this to?* (tests whether the audience assumption is
     right)
3. Then, and only then, say it was made with AI, and ask whether that changed
   anything they thought.
4. Record: their answer to each question, roughly where in the film they
   laughed or frowned, and one thing they would change.

A second round on the near-final cut repeats steps 1–2 with the changes from
round one in place. What is written into this file afterwards is the answers,
not a summary of them.

## Per-shot reasons

Required by the schema (`reason` on every shot) — every shot in
`storyboard.json` states why it exists. When a reviewer says a shot is not
doing its job, change the storyboard, don't defend the shot. All ten reasons
are visible in `PROMPTS.md` next to the prompt each one justifies.
