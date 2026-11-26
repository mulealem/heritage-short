# Ethics: consent, licences, labelling

## Consent for likeness and voice

GATE: if a real person appears or is voiced without a consent record here,
the film scores zero.

- Current status: **the cast is fictional.** Aleqa Gebre Hanna is a
  nineteenth-century folk-tale figure and the Gatekeeper is an invented
  character; both portraits are synthetic (MiniMax image-01) from no real
  person's likeness. The narration is synthetic TTS reading the narrator's own
  words, not a recording of a family member.
- Family story: the earlier draft ("What Are You Seeing?") was built from a
  real family memory. It was replaced by this folk tale before any film was
  published, so no real likeness or voice is used in the finished piece.
  The family had approved that earlier draft's text; the decision to move to
  the folk tale was the narrator's.
- If a real person is ever added: record who, what was agreed (face / voice /
  words), how consent was recorded, and the date — before generating.

## Model licences

| Model / asset | Used for | Licence | Output terms |
|---|---|---|---|
| Gemini 3.8 Flash TTS | narration (10 lines, voice Kore) | Google API terms | **TO CONFIRM before publishing** (generative AI output terms) |
| MiniMax image-01 | 11 keyframes, 16 panels, 2 cast portraits | MiniMax platform terms (M plan) | **TO CONFIRM before publishing** |
| FLUX-2 klein 4B (Cloudflare) | draft keyframes, comparison only | Apache 2.0 (4B weights) via Workers AI | per Workers AI terms |
| Wan 2.2 TI2V-5B | not used in this film | Apache 2.0 | usable commercially |
| ACE-Step 1.5 | not used in this film | MIT | outputs usable commercially |
| qenet bed | the score | original: synthesised by `tools/make_qenet_bed.py` in this repository | ours; no third-party rights |
| fframes 1.4.2-rc.11 | renderer (tool) | MIT (crate manifest) | n/a |
| FFmpeg, x264 build 163 | mix, mux, encode (tools) | LGPL / GPL | n/a — linked into the renderer binary, not into the film |
| DM Sans, Bangers, Noto Sans Ethiopic | captions, balloons, Amharic text | SIL Open Font Licence 1.1 | embeddable |

Tool and font licences were read from the crate manifests and font files on
this machine (Nov 2026). The two paid/API model terms are the owner's to
confirm on the day of publishing; nothing else in the film comes from a
third party.

## Repository licence

- The **code** — the pipeline, tools, editor, schemas, the renderer's Rust
  source and the documentation — is **MIT** (`LICENSE`).
- The **generated film and artwork** are not relicensed by that MIT licence:
  their terms come from the models above. `LICENSE` says so in its last
  section, so a reader is not misled into thinking the images were made MIT.
- The **retelling** in `storyboard.json`, `STORY.md` and the film is the
  author's; the underlying tale is traditional.

## Labelling plan

- The film ends with a visible "made with AI" end card (in the storyboard):
  title, the proverb in Amharic and English, and the line "a folk tale of
  Aleqa Gebre Hanna — made with AI", in both aspect ratios.
- The narration and the whole picture are synthetic; the story is a
  traditional folk tale, retold.
- **What the source files carry.** The MiniMax images embed an AIGC label in
  their EXIF (`ContentProducer: MiniMax`, found in the files). They are kept
  unmodified in `outputs/`.
- **What the films carry — stated plainly.** The MP4s are a re-render: the
  panels are redrawn by the comic renderer and the audio re-mixed, so no
  provider provenance metadata survives into them. The mux therefore writes its
  own disclosure into the container: `title` and a `comment` field reading
  "AI-generated film. Synthetic images (MiniMax image-01), synthetic narration
  (Gemini TTS), a score synthesised by code…" (`ffprobe` shows it). The comic
  camera moves crop a few percent of each panel edge; no blur or patch is
  applied to any watermark.
- Platform disclosure (YouTube / TikTok / Meta "AI content" label) switched ON
  when posting — TODO: platform + date + link.

## Private data

- Prompts sent to hosted models contain only the storyboard text: a public
  folk tale, no addresses, no family names, no private dates.
- `.env` (API keys) is gitignored and never logged; `runs.jsonl` records
  prompts, seeds, latencies and costs, not credentials. The working tree and
  the git history were scanned for every key value before the repository was
  published (none found).
- The earlier family-memory draft was **never committed**: its storyboard
  (`storyboard.backup.json`) is local-only and gitignored, and no image or
  audio from it is in `outputs/`. What the published log does contain is 29
  `runs.jsonl` lines from that draft, and they carry no text — only a shot id
  (`s1_street` …), a character count, a size and a seed. `runs.jsonl` records
  no prompt or narration text for any stage, which is why it can be published
  at all; the prompts themselves live in `storyboard.json` and
  `comic/panels.json` only.
- That draft's prompts were sent to Gemini TTS and Cloudflare Workers AI,
  whose free endpoints may retain inputs; they contained a family memory, no
  names, addresses or dates. The decision to set it aside and tell a
  traditional tale was the narrator's.
