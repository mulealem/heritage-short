# Eat, My Clothes, Eat! — every prompt, every line

> Generated from the live contract by `tools/export_prompts.py`; do not hand-edit. Regenerate with `make prompts`.

| | |
|---|---|
| Title | **Eat, My Clothes, Eat!** (ብሉ ልብሶቼ ብሉ) |
| Format | 9:16 and 16:9, 24 fps, 1080×1920 and 1920×1080 (comic renderer) |
| Film duration | 9:16: 89.7 s · 16:9: 89.7 s · 86.4 s of beats + 3.0 s end card |
| Narration language | am (English subtitle track + captions) |
| Image model | `image-01` (minimax), one `subject_reference` portrait per character shot |
| TTS | `gemini-3.8-flash-tts`, voice `Kore` |
| Music | ACE-Step 1.5 on Kaggle (manifest below) |

## The story being told

Aleqa Gebre Hanna, a wise elder scholar, walks to a neighbour's wedding feast in his dusty travelling gabi. Guests whisper as he approaches, and the gatekeeper turns him away at the crowded gate as unfit for honorable guests. He goes home, washes, dresses in his snow-white tibeb-bordered shamma and gold-trimmed velvet kabba, and returns — to bows from the gatekeeper, ililta ululations from bystanders, and a warm embrace from the host who leads him to the seat of honor. When servers set an enormous feast before him, the entire das falls silent. Gebre Hanna scoops red doro wot over his own white shamma, tucks meat in his sleeve, and pours golden tej down his velvet cloak as the host lunges to stop him and guests recoil. "Eat, my clothes, eat!" he says directly to the host and gatekeeper. "I came as myself and you turned me away; my clothes came and you gave them the seat of honor. You invited my clothes — not me!" The whole tent erupts in laughter. Proverb: judge a person by their character, not their cloth.

## Style block (prepended to every image prompt)

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark
```

## Identity directives (character-specific; appended only with that portrait)

### `gebre_hanna`

```text
Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

### `gatekeeper`

```text
Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to the stout bare-headed Gatekeeper (short oiled black hair, short beard, NO turban and NO hat, wearing the dark-teal velvet kabba with gold trim); keep all other characters distinct.
```

> **Rule:** a directive is attached only when that named character's portrait is used. Never attach a `subject_reference` to prop close-ups, food inserts or large crowd shots — the model would clone the lead's face onto bystanders. Every beat must show the environment, multi-character interaction and reaction in context.

## Cast reference portraits

### `gebre_hanna` — gebre_hanna.jpg

- File: `outputs/character_refs/gebre_hanna.jpg`
- Status vs this prompt: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic-style character portrait, front view, head and shoulders, an Ethiopian man in his late fifties with a lean face, salt-and-pepper beard and kind sharp eyes, wearing a cream turban with a gold band and a white shamma with gold-and-red tibeb borders over a dark robe, plain warm grey background
```

Attached as `subject_reference` to every shot whose panel spec names this actor.

### `gatekeeper` — gatekeeper.jpg

- File: `outputs/character_refs/gatekeeper.jpg`
- Status vs this prompt: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic-style character portrait, front view, head and shoulders, a stout proud Ethiopian man of forty with short oiled black hair, bare-headed with no turban and no hat, a neat short beard, wearing an ornate dark-teal velvet kabba with gold trim, plain warm grey background
```

Attached as `subject_reference` to every shot whose panel spec names this actor.

## Narration (spoken Amharic / English subtitles)

| # | Shot | Spoken (Amharic) | Subtitle (English) | Audio |
|---|---|---|---|---|
| 1 | `s1_das` | ከበሮ ይመታል፣ ጠጅ ይቀዳል፣ መላው ዳስ በእስክስታ ደምቋል። | The kebero pounds, the tej flows, and the whole das is alive with eskista. | 5.55s — in sync |
| 2 | `s2_arrival` | አለቃ ገብረ ሃና ከመንገድ በቀጥታ ደረሱ፤ አቧራማ የተጣፈ ጋቢ፣ ያረጀ ጫማ፣ ግን ብልህና አስተዋይ ዓይን። | Aleqa Gebre Hanna arrives straight from the road: dusty patched gabi, worn sandals, and the sharpest eyes in the empire. | 9.48s — in sync |
| 3 | `s3_gatekeeper` | ጠባቂው ከላይ እስከ ታች በንቀት አያቸው። «ይህ ድግስ ለክቡራን እንግዶች ነው፣ አንተ ሽማግሌ! ሂድና የሚገባ ልብስ ለብሰህ ና!» | The gatekeeper looks him up and down with scorn. "This feast is for honorable guests, old man! Go home and dress decently!" | 8.85s — in sync |
| 4 | `s4_change` | አለቃ ገብረ ሃና አልተከራከሩም። ፈገግ ብለው ወደ ቤታቸው ተመለሱ — ትእዛዙን ቃል በቃል ለመፈጸም። | Gebre Hanna does not argue. He smiles and heads home — to obey the order to the letter. | 7.26s — in sync |
| 5 | `s5_dressed` | በረዶ የመሰለ ነጭ ሸማ፣ በወርቅ የተጠለፈ የካቲፋ ካባ፣ የሚያብረቀርቅ ከዘራ። ያው ሰው — ግን ተለውጦ። | Out he steps: a snow-white shamma, a velvet kabba, a polished kezera stick. The same man, transformed. | 10.24s — in sync |
| 6 | `s6_welcome` | ተመለሱ፤ ያው ጠባቂ ተደናግጦ እጅ እስኪነካ ዝቅ ብሎ አጎነበሰ፤ እልልታውም እጥፍ ሆነ። | He returns — and the same gatekeeper gasps, bowing nearly to the ground, while the ululations ring twice as loud. | 8.04s — in sync |
| 7 | `s7_feast` | ባለድግሱ ወደ ክብር መቀመጫው መሯቸው፤ «አለቃ! ብሉ፣ ጠጡ — ሁሉም ለእርስዎ ነው!» | The host leads him to the seat of honor: "Aleqa! Eat, drink — everything here is yours!" | 7.25s — in sync |
| 8 | `s8_deadpan` | ከዚያ ዘፈኑና ከበሮው ጸጥ አለ፤ መላው ዳስም ትንፋሹን ውጦ ጠበቀ። | Then the music falls silent, and the whole das holds its breath. | 4.96s — in sync |
| 9 | `s9_mess` | ቀይ ዶሮ ወጥ ዘግነው በነጩ ሸማቸው ላይ ቀቡት፤ ስጋ በእጅጌው፣ ጠጅ በካባው ላይ አፈሰሱ። ባለድግሱም ደንግጠው ጮኹ። | He scoops red doro wot and smears it across his white shamma — meat in the sleeve, tej poured on the cloak. The host cries out. | 9.19s — in sync |
| 10 | `s10_punchline` | አለቃ ገብረ ሃና በርጋታ አሉ፦ «ብሉ ልብሶቼ፣ ብሉ! እኔ ራሴን ሆኜ ስመጣ አባረራችሁኝ። ልብሶቼ ሲመጡ ግን የክብር መቀመጫ ሰጣችኋቸው። የጠራችሁት ልብሶቼን እንጂ እኔን አይደለም!» | Says Gebre Hanna, calm as Sunday: "Eat, my clothes, eat! I came as myself, and you turned me away. My clothes came, and you gave them the seat of honor. You invited my clothes — not me!" | 13.54s — in sync |

TTS is called with the spoken text only — the style phrase is **not** sent (it used to be read aloud; see FAILURES.md F11). Voice and model above; `TTS_STYLE_PREFIX` is empty.

## Shot by shot

### 1. `s1_das` — extreme_wide

| | |
|---|---|
| Planned duration | 6.2 s |
| Narration audio | 5.55s — in sync |
| Seed | 101 |
| Camera move | push_out |
| Reference | none |
| Keyframe file | `outputs/keyframes/s1_das.png` |
| Status | in sync |

**Why this shot exists:** Opens at full Habesha wedding energy with dancers, musicians, servers and guests filling the das, so the gate's cold snobbery hits by contrast; establishes the feast everyone is here for.

**Narration (Amharic):** ከበሮ ይመታል፣ ጠጅ ይቀዳል፣ መላው ዳስ በእስክስታ ደምቋል።

**Subtitle (English):** The kebero pounds, the tej flows, and the whole das is alive with eskista.

**Keyframe — storyboard prompt:**

```text
comic book establishing panel, low wide angle inside a sprawling Ethiopian wedding das tent draped in woven striped cloth, crowds of men and women in white habesha kemis with colourful tibeb borders dancing eskista with raised shoulders, musicians playing a bowed masinko fiddle and two-headed kebero drum, clay jebena coffee pots steaming on fresh green grass, servers carrying woven baskets through the crowd, warm lantern light
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book establishing panel, low wide angle inside a sprawling Ethiopian wedding das tent draped in woven striped cloth, crowds of men and women in white habesha kemis with colourful tibeb borders dancing eskista with raised shoulders, musicians playing a bowed masinko fiddle and two-headed kebero drum, clay jebena coffee pots steaming on fresh green grass, servers carrying woven baskets through the crowd, warm lantern light
```

**Motion prompt (video route only):** dancers shake their shoulders in eskista rhythm, servers weave between seated elders, drummers pound, steam and dust glow in the lamplight, camera drifts slowly through the crowd

**Comic overlays:** SFX "DUM-TAK!" at 1.3s

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s1_das.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book establishing panel, low wide angle inside a sprawling Ethiopian wedding das tent draped in woven striped cloth, crowds of men and women in white habesha kemis with colourful tibeb borders dancing eskista with raised shoulders, musicians playing a bowed masinko fiddle and two-headed kebero drum, clay jebena coffee pots steaming on fresh green grass, servers carrying woven baskets through the crowd, warm lantern light
```

2. **dancer & bystander interaction** — 42% into the beat → `ins_s1_das_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book panel, medium-wide shot of two Ethiopian wedding guests in white shamma and habesha kemis dancing eskista face to face in a circle of clapping bystanders, an older woman beside them tilting her head back in ululation while neighbours smile and cheer
```

3. **server & guest interaction** — 74% into the beat → `ins_s1_das_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book panel, medium-wide shot of smiling servers in white aprons weaving between seated elders to pour golden honey wine tej from round-bottomed berele glass flasks while another server carries a huge covered woven mesob brimming with steaming injera and red doro wot
```

---

### 2. `s2_arrival` — wide_to_medium

| | |
|---|---|
| Planned duration | 9.3 s |
| Narration audio | 9.48s — in sync |
| Seed | 102 |
| Camera move | push_out |
| Reference | `gebre_hanna` portrait |
| Keyframe file | `outputs/keyframes/s2_arrival.png` |
| Status | in sync |

**Why this shot exists:** Introduces the hero inside the lively approach to the compound — a dusty traveller sharing the road with finely dressed wedding-goers who already look down on him, so the rejection is social from the first step.

**Narration (Amharic):** አለቃ ገብረ ሃና ከመንገድ በቀጥታ ደረሱ፤ አቧራማ የተጣፈ ጋቢ፣ ያረጀ ጫማ፣ ግን ብልህና አስተዋይ ዓይን።

**Subtitle (English):** Aleqa Gebre Hanna arrives straight from the road: dusty patched gabi, worn sandals, and the sharpest eyes in the empire.

**Keyframe — storyboard prompt:**

```text
wide comic book environmental panel, dusty highland road leading up to a festive Ethiopian stone compound entrance glowing with lanterns and striped tent fabric in the background: walking up the road in the foreground, Aleqa Gebre Hanna in a cream turban with a gold band, dusty patched brown gabi, worn leather sandals, and wooden staff, while finely dressed wedding guests in gleaming white shamma stride past him toward the crowded gate without greeting him
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book environmental panel, dusty highland road leading up to a festive Ethiopian stone compound entrance glowing with lanterns and striped tent fabric in the background: walking up the road in the foreground, Aleqa Gebre Hanna in a cream turban with a gold band, dusty patched brown gabi, worn leather sandals, and wooden staff, while finely dressed wedding guests in gleaming white shamma stride past him toward the crowded gate without greeting him Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

**Motion prompt (video route only):** he walks toward the camera, the gabi swaying, finely dressed guests pass without greeting him, dust drifts in the golden backlight, camera pushes in slowly

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s2_arrival.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book environmental panel, dusty highland road leading up to a festive Ethiopian stone compound entrance glowing with lanterns and striped tent fabric in the background: walking up the road in the foreground, Aleqa Gebre Hanna in a cream turban with a gold band, dusty patched brown gabi, worn leather sandals, and wooden staff, while finely dressed wedding guests in gleaming white shamma stride past him toward the crowded gate without greeting him Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

2. **guest-and-traveller road interaction** — 44% into the beat → `ins_s2_arrival_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book panel, medium-wide street interaction beside the stone compound wall: two wealthy wedding guests in crisp white habesha kemis and gold-bordered netela pull their garments aside and whisper behind their hands, glancing down disdainfully at the dusty patched brown gabi and worn leather sandals of the lean bearded elder in a cream turban walking calmly past them, bystanders looking out from the gate
```

3. **medium reaction at the compound threshold** — 74% into the beat → `ins_s2_arrival_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium shot, Aleqa Gebre Hanna in his dusty patched brown gabi and cream turban with a gold band pausing near the festive compound gate, sharp observant eyes gleaming with a warm knowing smile as bustling servers carrying clay pots and laughing guests crowd the bright lantern-lit tent archway behind him Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

---

### 3. `s3_gatekeeper` — wide_to_interaction

| | |
|---|---|
| Planned duration | 8.6 s |
| Narration audio | 8.85s — in sync |
| Seed | 103 |
| Camera move | push_out |
| Reference | none |
| Keyframe file | `outputs/keyframes/s3_gatekeeper.png` |
| Status | in sync |

**Why this shot exists:** Shows the full social theatre of the rejection — the glowing das behind the gatekeeper, guests and servers watching or piling on, and Gebre Hanna's calm, unshaken reaction and departure inside the environment rather than isolated face cutaways.

**Narration (Amharic):** ጠባቂው ከላይ እስከ ታች በንቀት አያቸው። «ይህ ድግስ ለክቡራን እንግዶች ነው፣ አንተ ሽማግሌ! ሂድና የሚገባ ልብስ ለብሰህ ና!»

**Subtitle (English):** The gatekeeper looks him up and down with scorn. "This feast is for honorable guests, old man! Go home and dress decently!"

**Keyframe — storyboard prompt:**

```text
wide comic book environmental panel at the grand wedding compound gate: the stout bare-headed gatekeeper in a dark-teal velvet kabba with gold trim stands squarely in the gateway and thrusts one open palm flat toward the dusty traveller in an unmistakable stop gesture, scowling; facing him in the dusty lane, Aleqa Gebre Hanna in a patched brown gabi and cream turban with a gold band waits calmly on his wooden staff; well-dressed guests file past behind the gatekeeper, staring and whispering, the lantern-lit festive das glowing behind
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book environmental panel at the grand wedding compound gate: the stout bare-headed gatekeeper in a dark-teal velvet kabba with gold trim stands squarely in the gateway and thrusts one open palm flat toward the dusty traveller in an unmistakable stop gesture, scowling; facing him in the dusty lane, Aleqa Gebre Hanna in a patched brown gabi and cream turban with a gold band waits calmly on his wooden staff; well-dressed guests file past behind the gatekeeper, staring and whispering, the lantern-lit festive das glowing behind
```

**Motion prompt (video route only):** the gatekeeper looks the visitor up and down, raises his hand and points him away, guests file past staring and whispering, camera holds wide then pushes toward the pair

**Comic overlays:** balloon "This feast is for honorable guests, old man!" from 2.0s to 7.7s

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s3_gatekeeper.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book environmental panel at the grand wedding compound gate: the stout bare-headed gatekeeper in a dark-teal velvet kabba with gold trim stands squarely in the gateway and thrusts one open palm flat toward the dusty traveller in an unmistakable stop gesture, scowling; facing him in the dusty lane, Aleqa Gebre Hanna in a patched brown gabi and cream turban with a gold band waits calmly on his wooden staff; well-dressed guests file past behind the gatekeeper, staring and whispering, the lantern-lit festive das glowing behind
```

2. **over-the-shoulder group rejection** — 38% into the beat → `ins_s3_gatekeeper_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book over-the-shoulder interaction shot, framed past the dusty brown gabi shoulder and cream turban of Aleqa Gebre Hanna in the foreground toward the stout bare-headed gatekeeper in his dark-teal velvet kabba sneering and pointing sternly down the road; flanking the gatekeeper, two richly dressed guests smirk and shield their faces in disdain while a young server holding a berele tray peeks awkwardly from behind the woven tent curtain and bystanders gather behind the stone wall
```

3. **environmental reaction & turn-away** — 72% into the beat → `ins_s3_gatekeeper_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide environmental reaction shot: in the foreground, Aleqa Gebre Hanna in his dusty patched gabi and cream turban with a gold band turns calmly away toward the dusty road with a small, knowing, slightly dangerous half-smile and steady grip on his staff; behind him at the sunlit compound gate, the stout bare-headed gatekeeper folds his arms smugly, two guests whisper and watch him leave, and a server pauses glancing back over his shoulder Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

---

### 4. `s4_change` — medium_wide

| | |
|---|---|
| Planned duration | 7.2 s |
| Narration audio | 7.26s — in sync |
| Seed | 104 |
| Camera move | pan_r |
| Reference | none |
| Keyframe file | `outputs/keyframes/s4_change.png` |
| Status | in sync |

**Why this shot exists:** The comic hinge: literal obedience is the heart of the satire; showing him physically shed the dusty gabi inside his highland home grounds the transformation in a real place.

**Narration (Amharic):** አለቃ ገብረ ሃና አልተከራከሩም። ፈገግ ብለው ወደ ቤታቸው ተመለሱ — ትእዛዙን ቃል በቃል ለመፈጸም።

**Subtitle (English):** Gebre Hanna does not argue. He smiles and heads home — to obey the order to the letter.

**Keyframe — storyboard prompt:**

```text
comic book wide interior panel inside a traditional Ethiopian highland stone-and-mud house: warm sunlight slanting through an open wooden shuttered window onto a dusty patched brown gabi tossed briskly onto a wooden wall peg with comic speed lines, beside a carved wooden chest propped open showing folded snow-white cloth and gold embroidery, earthen floor and woven reed mats
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide interior panel inside a traditional Ethiopian highland stone-and-mud house: warm sunlight slanting through an open wooden shuttered window onto a dusty patched brown gabi tossed briskly onto a wooden wall peg with comic speed lines, beside a carved wooden chest propped open showing folded snow-white cloth and gold embroidery, earthen floor and woven reed mats
```

**Motion prompt (video route only):** the gabi flies onto its peg, the chest opens, water splashes and droplets scatter, hands move fast through frame, camera pans across the room

**Cuts in this beat (2):**

1. **base keyframe** — 0% into the beat → `panel_s4_change.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide interior panel inside a traditional Ethiopian highland stone-and-mud house: warm sunlight slanting through an open wooden shuttered window onto a dusty patched brown gabi tossed briskly onto a wooden wall peg with comic speed lines, beside a carved wooden chest propped open showing folded snow-white cloth and gold embroidery, earthen floor and woven reed mats
```

2. **courtyard wash & chest preparation** — 55% into the beat → `ins_s4_change_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide panel in a sunlit stone courtyard: Aleqa Gebre Hanna in his cream turban with a gold band splashing cool water from a terracotta clay basin onto his face with sparkling droplets frozen mid-air while glancing knowingly toward a folded royal velvet kabba laid out beside him, a curious neighbour child peeking around the courtyard doorway Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

---

### 5. `s5_dressed` — medium_to_wide

| | |
|---|---|
| Planned duration | 9.3 s |
| Narration audio | 10.24s — in sync |
| Seed | 105 |
| Camera move | pan_r |
| Reference | none |
| Keyframe file | `outputs/keyframes/s5_dressed.png` |
| Status | in sync |

**Why this shot exists:** The transformation shot — the clothes arrive as a character of their own, and the village instantly reads them: neighbours bow, children follow, the same man is suddenly treated as a different man.

**Narration (Amharic):** በረዶ የመሰለ ነጭ ሸማ፣ በወርቅ የተጠለፈ የካቲፋ ካባ፣ የሚያብረቀርቅ ከዘራ። ያው ሰው — ግን ተለውጦ።

**Subtitle (English):** Out he steps: a snow-white shamma, a velvet kabba, a polished kezera stick. The same man, transformed.

**Keyframe — storyboard prompt:**

```text
comic book hero panel, low dramatic angle at the stone doorway: Aleqa Gebre Hanna in his cream turban with a gold band, transformed in a gleaming snow-white cotton shamma with intricate red-and-gold tibeb woven borders and a royal deep-indigo velvet kabba draped cape-like over his shoulders with heavy gold embroidery, planting a polished dark wooden kezera walking stick firmly on the stone step, radiant golden backlight
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book hero panel, low dramatic angle at the stone doorway: Aleqa Gebre Hanna in his cream turban with a gold band, transformed in a gleaming snow-white cotton shamma with intricate red-and-gold tibeb woven borders and a royal deep-indigo velvet kabba draped cape-like over his shoulders with heavy gold embroidery, planting a polished dark wooden kezera walking stick firmly on the stone step, radiant golden backlight
```

**Motion prompt (video route only):** he settles the velvet kabba over his shoulders with one arm, plants the walking stick, chin up, camera rises with him

**Cuts in this beat (2):**

1. **base keyframe** — 0% into the beat → `panel_s5_dressed.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book hero panel, low dramatic angle at the stone doorway: Aleqa Gebre Hanna in his cream turban with a gold band, transformed in a gleaming snow-white cotton shamma with intricate red-and-gold tibeb woven borders and a royal deep-indigo velvet kabba draped cape-like over his shoulders with heavy gold embroidery, planting a polished dark wooden kezera walking stick firmly on the stone step, radiant golden backlight
```

2. **wide street & neighbour interaction** — 55% into the beat → `ins_s5_dressed_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide village street panel: Aleqa Gebre Hanna in his cream turban with a gold band, snow-white tibeb shamma, royal indigo velvet kabba and kezera walking stick striding along the sunlit road toward the distant wedding tents; villagers carrying clay water jars stop to bow respectfully in greeting, neighbours lean over stone walls in awe, and two grinning children trot alongside him
```

---

### 6. `s6_welcome` — wide_interaction

| | |
|---|---|
| Planned duration | 8.1 s |
| Narration audio | 8.04s — in sync |
| Seed | 106 |
| Camera move | pan_r |
| Reference | none |
| Keyframe file | `outputs/keyframes/s6_welcome.png` |
| Status | in sync |

**Why this shot exists:** The satirical reversal: identical man, different cloth, opposite reception — shown through physical interaction with the gatekeeper, bystanders, ululating women and the rushing host together.

**Narration (Amharic):** ተመለሱ፤ ያው ጠባቂ ተደናግጦ እጅ እስኪነካ ዝቅ ብሎ አጎነበሰ፤ እልልታውም እጥፍ ሆነ።

**Subtitle (English):** He returns — and the same gatekeeper gasps, bowing nearly to the ground, while the ululations ring twice as loud.

**Keyframe — storyboard prompt:**

```text
wide comic book panel at the wedding compound gate: the stout bare-headed gatekeeper in his dark-teal velvet kabba with gold trim is bent forward in an exaggerated deep bow, torso nearly parallel to the ground, head lowered, both hands pressed on his knees; Aleqa Gebre Hanna in a cream turban with a gold band, snow-white tibeb shamma and royal indigo velvet kabba walks calmly past him; behind them amazed guests, servers holding trays and women ululating with raised hands fill the sunlit courtyard
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book panel at the wedding compound gate: the stout bare-headed gatekeeper in his dark-teal velvet kabba with gold trim is bent forward in an exaggerated deep bow, torso nearly parallel to the ground, head lowered, both hands pressed on his knees; Aleqa Gebre Hanna in a cream turban with a gold band, snow-white tibeb shamma and royal indigo velvet kabba walks calmly past him; behind them amazed guests, servers holding trays and women ululating with raised hands fill the sunlit courtyard
```

**Motion prompt (video route only):** the gatekeeper folds into a deep bow and holds it, the hero walks past in slow motion, women ululate and guests turn, camera tracks ahead of him

**Comic overlays:** SFX "GASP!" at 1.1s; SFX "ELILILILI!" at 4.9s

**Cuts in this beat (2):**

1. **base keyframe** — 0% into the beat → `panel_s6_welcome.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — wide comic book panel at the wedding compound gate: the stout bare-headed gatekeeper in his dark-teal velvet kabba with gold trim is bent forward in an exaggerated deep bow, torso nearly parallel to the ground, head lowered, both hands pressed on his knees; Aleqa Gebre Hanna in a cream turban with a gold band, snow-white tibeb shamma and royal indigo velvet kabba walks calmly past him; behind them amazed guests, servers holding trays and women ululating with raised hands fill the sunlit courtyard
```

2. **host & Gebre Hanna greeting interaction** — 48% into the beat → `ins_s6_welcome_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide interaction panel inside the das entrance: the older warm-faced Ethiopian host, bare-headed with silver-flecked hair in a crimson velvet kabba with gold embroidery, no eyeglasses, no modern accessories, eagerly clasping both hands and forearms of Aleqa Gebre Hanna (cream turban with gold band, snow-white shamma, indigo velvet kabba) to welcome him warmly inside, while behind them the stout bare-headed gatekeeper hovers nervously wiping his brow, smiling women ululate, and servers hurry to clear the aisle
```

---

### 7. `s7_feast` — wide_to_insert

| | |
|---|---|
| Planned duration | 7.1 s |
| Narration audio | 7.25s — in sync |
| Seed | 107 |
| Camera move | pan_l |
| Reference | none |
| Keyframe file | `outputs/keyframes/s7_feast.png` |
| Status | in sync |

**Why this shot exists:** Shows the full social ceremony of seating the honoured guest — host gesturing, guests making way, servers opening the mesob and pouring tej — before closing on the feast itself.

**Narration (Amharic):** ባለድግሱ ወደ ክብር መቀመጫው መሯቸው፤ «አለቃ! ብሉ፣ ጠጡ — ሁሉም ለእርስዎ ነው!»

**Subtitle (English):** The host leads him to the seat of honor: "Aleqa! Eat, drink — everything here is yours!"

**Keyframe — storyboard prompt:**

```text
comic book wide interior panel inside the bustling das: the crimson-robed Ethiopian host happily guiding Aleqa Gebre Hanna (cream turban with gold band, snow-white shamma, indigo velvet kabba) by the arm to an ornate cushioned seat of honor at the centre of the tent, while a ring of seated guests lean forward smiling and applauding, musicians play nearby, and smiling servers carry covered woven mesobs and berele flasks toward them
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide interior panel inside the bustling das: the crimson-robed Ethiopian host happily guiding Aleqa Gebre Hanna (cream turban with gold band, snow-white shamma, indigo velvet kabba) by the arm to an ornate cushioned seat of honor at the centre of the tent, while a ring of seated guests lean forward smiling and applauding, musicians play nearby, and smiling servers carry covered woven mesobs and berele flasks toward them
```

**Motion prompt (video route only):** the host guides him by the arm through the applauding ring, servers set down the covered mesob and pour tej, steam rises, camera glides along the procession

**Comic overlays:** balloon "Aleqa! Eat, drink — everything is yours!" from 2.2s to 6.7s

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s7_feast.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide interior panel inside the bustling das: the crimson-robed Ethiopian host happily guiding Aleqa Gebre Hanna (cream turban with gold band, snow-white shamma, indigo velvet kabba) by the arm to an ornate cushioned seat of honor at the centre of the tent, while a ring of seated guests lean forward smiling and applauding, musicians play nearby, and smiling servers carry covered woven mesobs and berele flasks toward them
```

2. **host, servers & seated guest table interaction** — 45% into the beat → `ins_s7_feast_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide interaction panel around the seat of honor: Aleqa Gebre Hanna seated serenely on cushioned carpets as the crimson-robed host leans in gesturing grandly toward a huge open woven mesob, one smiling server lifting off the conical woven lid as steam rises and another server pouring golden tej into a glass berele beside his elbow, nearby guests leaning in eagerly waiting for him to eat
```

3. **food insert** — 76% into the beat → `ins_s7_feast_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book food close-up panel, glistening macro of rich crimson-red Ethiopian doro wot with whole boiled egg and chicken drumstick piled over spongy injera inside a woven mesob, curls of hot steam rising, and amber-golden tej sparkling in a round-bottomed berele glass flask
```

---

### 8. `s8_deadpan` — wide_to_close

| | |
|---|---|
| Planned duration | 6.0 s |
| Narration audio | 4.96s — in sync |
| Seed | 108 |
| Camera move | push_in |
| Reference | none |
| Keyframe file | `outputs/keyframes/s8_deadpan.png` |
| Status | in sync |

**Why this shot exists:** The comic pause — the entire room (musicians, servers, host, guests) freezes in breathless silence around Gebre Hanna before the twist drops.

**Narration (Amharic):** ከዚያ ዘፈኑና ከበሮው ጸጥ አለ፤ መላው ዳስም ትንፋሹን ውጦ ጠበቀ።

**Subtitle (English):** Then the music falls silent, and the whole das holds its breath.

**Keyframe — storyboard prompt:**

```text
comic book wide atmospheric panel inside the hushed das tent: seated motionless at the centre behind the steaming mesob, Aleqa Gebre Hanna in his cream turban with a gold band and royal velvet kabba gazes quietly from the food to the ring of faces; all around him the tent is frozen in suspense — kebero drummers hold their hands raised mid-beat, masinko bows hang still, servers pause holding berele flasks, and the crimson-robed host and dozens of guests lean forward wide-eyed in dead silence
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide atmospheric panel inside the hushed das tent: seated motionless at the centre behind the steaming mesob, Aleqa Gebre Hanna in his cream turban with a gold band and royal velvet kabba gazes quietly from the food to the ring of faces; all around him the tent is frozen in suspense — kebero drummers hold their hands raised mid-beat, masinko bows hang still, servers pause holding berele flasks, and the crimson-robed host and dozens of guests lean forward wide-eyed in dead silence
```

**Motion prompt (video route only):** the whole room holds still, only his eyes move from the food to the host, a single drumstick trembles, camera creeps in

**Cuts in this beat (2):**

1. **base keyframe** — 0% into the beat → `panel_s8_deadpan.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide atmospheric panel inside the hushed das tent: seated motionless at the centre behind the steaming mesob, Aleqa Gebre Hanna in his cream turban with a gold band and royal velvet kabba gazes quietly from the food to the ring of faces; all around him the tent is frozen in suspense — kebero drummers hold their hands raised mid-beat, masinko bows hang still, servers pause holding berele flasks, and the crimson-robed host and dozens of guests lean forward wide-eyed in dead silence
```

2. **medium close-up in context** — 55% into the beat → `ins_s8_deadpan_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book dramatic medium close-up panel, Aleqa Gebre Hanna in his cream turban with a gold band, face completely calm and unreadable as one eyebrow subtly lifts and his dark eyes glint with quiet mischief above the steaming mesob; framed over his shoulders in soft focus, the eager expectant faces of the crimson-robed host and watching guests lean in waiting for his first bite Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

---

### 9. `s9_mess` — wide_interaction

| | |
|---|---|
| Planned duration | 8.8 s |
| Narration audio | 9.19s — in sync |
| Seed | 109 |
| Camera move | pan_r |
| Reference | none |
| Keyframe file | `outputs/keyframes/s9_mess.png` |
| Status | in sync |

**Why this shot exists:** Shows the full environmental shock across the das first, then the physical confrontation between the host and Gebre Hanna with servers and guests reacting beside them, and a quick stain-on-mat beat.

**Narration (Amharic):** ቀይ ዶሮ ወጥ ዘግነው በነጩ ሸማቸው ላይ ቀቡት፤ ስጋ በእጅጌው፣ ጠጅ በካባው ላይ አፈሰሱ። ባለድግሱም ደንግጠው ጮኹ።

**Subtitle (English):** He scoops red doro wot and smears it across his white shamma — meat in the sleeve, tej poured on the cloak. The host cries out.

**Keyframe — storyboard prompt:**

```text
comic book wide environmental panel inside a low Ethiopian wedding das tent lined with woven striped cloth, guests seated on reed mats around a woven mesob: Aleqa Gebre Hanna, fully dressed in his snow-white tibeb shamma and cream turban with a gold band, wipes a thick fistful of chunky orange-red doro wot stew with visible shredded chicken and boiled egg down the front panel of his shamma, which stays wrapped closed; the stain is clearly food; beside him the crimson-robed host leaps upright in horror, a woman guest recoils with hands over her mouth, and a server freezes holding a berele flask
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide environmental panel inside a low Ethiopian wedding das tent lined with woven striped cloth, guests seated on reed mats around a woven mesob: Aleqa Gebre Hanna, fully dressed in his snow-white tibeb shamma and cream turban with a gold band, wipes a thick fistful of chunky orange-red doro wot stew with visible shredded chicken and boiled egg down the front panel of his shamma, which stays wrapped closed; the stain is clearly food; beside him the crimson-robed host leaps upright in horror, a woman guest recoils with hands over her mouth, and a server freezes holding a berele flask
```

**Motion prompt (video route only):** his hand smears the stew deliberately across the white cloth, the host lunges toward his arm, tej pours down the velvet shoulder, guests recoil, camera shakes with the shock

**Comic overlays:** SFX "SQUELCH!" at 1.8s; SFX "POUR!" at 4.7s

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s9_mess.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide environmental panel inside a low Ethiopian wedding das tent lined with woven striped cloth, guests seated on reed mats around a woven mesob: Aleqa Gebre Hanna, fully dressed in his snow-white tibeb shamma and cream turban with a gold band, wipes a thick fistful of chunky orange-red doro wot stew with visible shredded chicken and boiled egg down the front panel of his shamma, which stays wrapped closed; the stain is clearly food; beside him the crimson-robed host leaps upright in horror, a woman guest recoils with hands over her mouth, and a server freezes holding a berele flask
```

2. **host & Gebre Hanna physical confrontation** — 42% into the beat → `ins_s9_mess_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide confrontation interaction panel: Aleqa Gebre Hanna (cream turban with gold band, meat tucked into his red-stained white shamma sleeve) calmly tilts a glass berele flask pouring sparkling amber-golden tej straight down the front of his royal indigo velvet kabba, while right beside him the horrified older host in his crimson kabba lunges forward with wide eyes reaching both hands toward Gebre Hanna's arm to stop him, as two stunned servers and gasping guests lean back in disbelief
```

3. **sauce & tej splash insert** — 74% into the beat → `ins_s9_mess_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book tight dynamic insert, thick chunky orange-red doro wot with visible shredded chicken soaking into intricate gold-and-red tibeb embroidery on a white cotton shamma hem while golden tej splashes down onto woven reed floor mats beside the base of a woven mesob and stunned guests' sandals, droplets frozen mid-air
```

---

### 10. `s10_punchline` — interaction_to_wide

| | |
|---|---|
| Planned duration | 15.8 s |
| Narration audio | 13.54s — in sync |
| Seed | 110 |
| Camera move | push_out |
| Reference | none |
| Keyframe file | `outputs/keyframes/s10_punchline.png` |
| Status | in sync |

**Why this shot exists:** Delivers the famous line as a direct exchange with the host, gatekeeper, servers and guests watching, before cutting wide to the entire das erupting in laughter and shame-faced reckoning after his final word lands.

**Narration (Amharic):** አለቃ ገብረ ሃና በርጋታ አሉ፦ «ብሉ ልብሶቼ፣ ብሉ! እኔ ራሴን ሆኜ ስመጣ አባረራችሁኝ። ልብሶቼ ሲመጡ ግን የክብር መቀመጫ ሰጣችኋቸው። የጠራችሁት ልብሶቼን እንጂ እኔን አይደለም!»

**Subtitle (English):** Says Gebre Hanna, calm as Sunday: "Eat, my clothes, eat! I came as myself, and you turned me away. My clothes came, and you gave them the seat of honor. You invited my clothes — not me!"

**Keyframe — storyboard prompt:**

```text
comic book medium-wide confrontation shot inside the quiet das: on the left, Aleqa Gebre Hanna, fully dressed in a cream turban with a gold band, a snow-white tibeb shamma whose front panel is smeared with thick chunky orange-red doro wot stew with visible pieces of chicken and egg, and a velvet kabba glistening with golden tej, stands calm as Sunday wiping his fingers with a cloth and gesturing at the stained front of his shamma, looking directly at the stunned crimson-robed host and the wide-eyed bare-headed dark-teal gatekeeper opposite him, silent servers and leaning guests framing them
```

**Keyframe — exact prompt sent to `image-01`:**

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide confrontation shot inside the quiet das: on the left, Aleqa Gebre Hanna, fully dressed in a cream turban with a gold band, a snow-white tibeb shamma whose front panel is smeared with thick chunky orange-red doro wot stew with visible pieces of chicken and egg, and a velvet kabba glistening with golden tej, stands calm as Sunday wiping his fingers with a cloth and gesturing at the stained front of his shamma, looking directly at the stunned crimson-robed host and the wide-eyed bare-headed dark-teal gatekeeper opposite him, silent servers and leaning guests framing them
```

**Motion prompt (video route only):** he wipes his fingers calmly, gestures at his stained chest, speaks directly to the host and gatekeeper, the room cracks into laughter only after his last word, camera pushes slowly out

**Comic overlays:** balloon "Eat, my clothes, eat!" from 2.3s to 6.5s; SFX "HA HA HA!" at 13.8s

**Cuts in this beat (3):**

1. **base keyframe** — 0% into the beat → `panel_s10_punchline.png`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book medium-wide confrontation shot inside the quiet das: on the left, Aleqa Gebre Hanna, fully dressed in a cream turban with a gold band, a snow-white tibeb shamma whose front panel is smeared with thick chunky orange-red doro wot stew with visible pieces of chicken and egg, and a velvet kabba glistening with golden tej, stands calm as Sunday wiping his fingers with a cloth and gesturing at the stained front of his shamma, looking directly at the stunned crimson-robed host and the wide-eyed bare-headed dark-teal gatekeeper opposite him, silent servers and leaning guests framing them
```

2. **hero delivery with reacting crowd** — 50% into the beat → `ins_s10_punchline_x1.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book dramatic medium shot, low angle on Aleqa Gebre Hanna in his cream turban with a gold band, chin lifted in composed triumphant wit in his doro-wot-stained white tibeb shamma and velvet kabba, the thick orange-red stew stain visible with pieces of chicken and egg, speaking calmly to the room as guests and servers behind him exchange sudden wide-eyed looks of dawning realization, golden rim light Redraw the referenced person as a flat-colour comic-book illustration: bold black ink contours, flat saturated colour, halftone dot shading, no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna (the lean elder with salt-and-pepper beard, sharp eyes, and cream turban with a gold band); keep all other guests, hosts, servers, and bystanders with distinct different faces and no turban.
```

3. **wide full-das eruption** — 84% into the beat → `ins_s10_punchline_x2.jpg`

Status: in sync

```text
single comic-book panel, vibrant graphic-novel animation still, bold black ink contours, flat saturated colour blocking with halftone dot shading, dramatic foreshortened angles, glowing golden rim light against deep teal shadows, subtle chromatic offset, kinetic comic composition, rich Ethiopian palette of gold, crimson and indigo, no text, no lettering, no speech balloons, no watermark — comic book wide celebratory finale inside the Ethiopian wedding das: the entire tent erupts in roaring laughter and applause — guests slapping their knees and clapping, smiling servers grinning behind berele trays, women raising ililta ululations, the crimson-robed host laughing sheepishly with one hand on his forehead, Aleqa Gebre Hanna smiling warmly at centre in his stained finery, and in the foreground corner the bare-headed gatekeeper in his dark-teal kabba staring down sheepishly at his own sandals, joyful golden energy lines
```

---

## End card

- Title: **Eat, My Clothes, Eat!** (ብሉ ልብሶቼ ብሉ)
- Proverb (Amharic): ሰውን በልብሱ ሳይሆን በስብዕናው መዝኑት።
- Proverb (English): Judge a person by their character, not their cloth.
- Subtitle: a folk tale of Aleqa Gebre Hanna — made with AI
- Duration: 3.0 s

## Music prompt (ACE-Step 1.5, Kaggle)

| Field | Value |
|---|---|
| Caption | playful theatrical Ethiopian comic-book score in traditional pentatonic qenet (Ambassel and Bati feel), expressive bowed masinko fiddle dancing over bouncy two-headed kebero drums and washint bamboo flute flourishes, comic brass-like stingers, sudden dead-air silences for punchlines, satirical swagger, joyous Habesha wedding energy |
| BPM | 118 |
| Key | A minor (pentatonic qenet feel) |
| Instrumental | True |
| Candidates | 3 |
| Seeds | [42, 43, 44] |
| Lyrics | (none) |

This prompt is the storyboard's `music` block. The Kaggle manifest (`kaggle/manifest_music.json`) is regenerated by `make music`.

**Score on disk:** `qenet-bed-v1` — a deterministic, hand-synthesized qenet bed (`tools/make_qenet_bed.py`), mixed at −24 LUFS and ducked under the voice. The ACE-Step prompt above remains the upgrade path; replace `score_final.wav` and re-render to use it.

## How these were produced

- Images: `python3 -m pipeline.keyframes` (keyframes) and `python3 tools/comic_panels.py` (inserts/extras); every call is logged in `runs.jsonl` with model, latency and estimated cost.
- Cast anchors: `python3 tools/comic_cast.py`.
- Narration: `make narration` (Gemini TTS, paced to the free-tier 3 requests/minute; cached per line).
- Edit and regenerate single assets: `make editor` (or `bash tools/serve_public.sh` for a tunnel).
- Regenerate this document: `make prompts`.

**Status honesty:** `in sync` means the file on disk was generated from *this exact prompt* (cache sidecar matches). `stale` means the prompt has been edited since that image was drawn — press Regenerate for that asset when the image quota allows (see FAILURES.md F12).
