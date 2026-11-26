# Eat, My Clothes, Eat! — the story

*A traditional Ethiopian folk tale of Aleqa Gebre Hanna, retold as a 90-second
motion comic in 9:16 and 16:9 — Amharic narration, English subtitles.*

---

## What this project is trying to do

Put a real Ethiopian folk tale on screen in a form that travels: vertical 9:16,
Amharic voice, English subtitles, drawn like a modern comic (bold ink, halftone,
gold-and-teal), animated with camera moves, speech balloons, starburst sound
effects and word-by-word captions — with no video model and no GPU. One
`storyboard.json` is the contract; every image prompt, narration line, timing,
balloon and cut derives from it; every model call is logged with latency and
cost. The choice that shapes it:

- **Amharic spoken, English read.** The narration is in idiomatic Ethiopian
  Amharic (Gemini TTS, voice Kore); the subtitles and on-screen captions are
  English, with bilingual punchlines on key beats so a Habesha family audience
  enjoys both the language and the delivery.
- **Ensemble comic storytelling, not isolated portraits.** Every key beat pairs
  wide environmental framing (the *das*, gate, servers, musicians, neighbours,
  and guests) with multi-character interaction shots so relationships, social
  hypocrisy, and crowd reactions read visually in every cut.
- **Comic, not fake film.** Still panels are cut and moved like a comic page
  (wide establishing shot → two-shot → reaction close), rendered deterministically
  by an fframes (Rust, CPU) scene in ~5 minutes.
- **Real only.** No placeholder audio or images: a missing key or quota stops the
  pipeline with instructions instead of faking output.
- **Iterate in a browser.** A local editor exposes every prompt and line, with
  per-asset regenerate and a Render button.

---

## Logline

A proud gatekeeper turns away a dusty scholar at a crowded wedding gate because
of his clothes — so the scholar comes back dressed like a king, and feeds the
feast to his garments in front of the stunned guests, servers, and host.

---

## The full story

The kebero drums had been sounding since morning. Inside the great *das* — the
long feasting tent draped in woven cloth — the whole neighbourhood was dancing
eskista, shoulders shaking, women raising *ililta* ululations, clay jebenas
steaming, servers weaving with *mesobs*, and golden *tej* poured from berele to
berele until the air itself smelled sweet.

Aleqa Gebre Hanna came up the dusty road in the clothes he had travelled in: a
patched *gabi* pulled around his shoulders, worn leather sandals, a wooden staff
in his hand. Guests in gleaming white walked past him toward the gate, glancing
sideways and whispering behind their hands. He had the sharpest eyes in the
empire and a salt-and-pepper beard beneath a cream *t'emtam* turban, and he was
smiling, because he loved a wedding.

At the glowing gate, as fine guests filed past and servers carried trays inside,
the host's gatekeeper barred his way and looked him up and down with scorn. The
man was stout and proud in an ornate dark-teal velvet *kabba* with gold trim,
and beside him two guests smirked as bystanders stopped to watch.

"This feast is for honorable guests, old man," he said, raising one hand.
"Go home and dress decently before you embarrass us."

A server peeking from the tent curtain froze. The guests behind the gatekeeper
turned away whispering. Gebre Hanna did not argue. He did not raise his staff
or his voice. He smiled — a small, knowing, slightly dangerous smile — and
calmly turned back down the dusty road while the gatekeeper folded his arms
smugly and the bystanders stared.

Inside his stone house he tossed the dusty gabi onto its peg and washed his
face in the clay basin. Then, piece by piece, he dressed: a *shamma* of
snow-white cotton woven with gold-and-red *tibeb* borders; a royal indigo
velvet *kabba* over his shoulders; a polished *kezera* walking stick in place of
the old staff. As he stepped back onto the village path, neighbours bowed in
greeting and children ran beside him in awe. The same man. Entirely transformed.

He walked back to the feast.

This time the gatekeeper saw him from a distance and gasped. He bent double,
bowing so low his hands nearly touched the ground, while bystanders gaped and
the *ililta* ululations rang out twice as loud. The host came running in his
crimson kabba, clasping Gebre Hanna warmly by both hands to usher him inside,
while the sweating gatekeeper hovered nervously behind them.

"Aleqa! Welcome, honored guest!" the host cried, leading him past bowing guests
to the cushioned seat of honor at the very centre of the das. "Eat, drink —
everything here is yours!"

Servers set down a woven *mesob* piled high with steaming injera and rich red
*doro wot*, prime cuts of meat, and poured golden *tej* into a berele flask at
his elbow. The guests leaned in, smiling, waiting for him to lift the first
bite.

Gebre Hanna looked at the food. Then at the host. Then, slowly, around the ring
of shining faces.

The kebero drummers froze mid-beat, the masinko bows halted, servers stopped
mid-pour, and the whole das held its breath.

He scooped up a great handful of red doro wot — and smeared it, deliberately,
across the chest of his snow-white shamma. Around the table, guests recoiled
with hands over their mouths and servers froze with their berele flasks. He
tucked meat into his sleeve, lifted the berele, and poured golden tej straight
down his velvet kabba as the horrified host lunged forward to grab his arm.

"Aleqa! Have you lost your mind? You are ruining your finest clothes!"

Gebre Hanna wiped his hands, calm as Sunday, pointed straight to his stained
shamma, and looked the host and the gatekeeper dead in the eye while the whole
tent listened.

"Eat, my clothes, eat! — ብሉ ልብሶቼ፣ ብሉ!

"When I arrived as myself, you turned me away. But when my clothes arrived, you
gave them the seat of honor. Clearly it was not me you invited. You invited my
clothes — not me!"

For one long heartbeat the das was silent. Then the entire tent broke — guests
slapping their knees and laughing, servers grinning over their trays, women
ululating, the host laughing and ashamed at once, and the gatekeeper in the
corner studying his own sandals.

And that is why, at every wedding where the story is told, someone looks around
the room and asks, grinning:

*"What are you wearing — or who are you?"*

The proverb that ends it: **judge a person by their character, not their cloth.**
*(ሰውን በልብሱ ሳይሆን በስብዕናው መዝኑት።)*

---

## Scene by scene (spoken Amharic / English subtitle)

| # | Shot | Spoken narration (Amharic) | English subtitle | Beat in the cut | Audio as recorded | Audio in the cut |
|---|---|---|---|---|---|---|---|
| 1 | `s1_das` | ከበሮ ይመታል፣ ጠጅ ይቀዳል፣ መላው ዳስ በእስክስታ ደምቋል። | The kebero pounds, the tej flows, and the whole das is alive with eskista. | 6.2 s | 5.55 s | 5.12 s |
| 2 | `s2_arrival` | አለቃ ገብረ ሃና ከመንገድ በቀጥታ ደረሱ፤ አቧራማ የተጣፈ ጋቢ፣ ያረጀ ጫማ፣ ግን ብልህና አስተዋይ ዓይን። | Aleqa Gebre Hanna arrives straight from the road: dusty patched gabi, worn sandals, and the sharpest eyes in the empire. | 9.3 s | 9.48 s | 8.87 s |
| 3 | `s3_gatekeeper` | ጠባቂው ከላይ እስከ ታች በንቀት አያቸው። «ይህ ድግስ ለክቡራን እንግዶች ነው፣ አንተ ሽማግሌ! ሂድና የሚገባ ልብስ ለብሰህ ና!» | The gatekeeper looks him up and down with scorn. "This feast is for honorable guests, old man! Go home and dress decently!" | 8.6 s | 8.85 s | 8.11 s |
| 4 | `s4_change` | አለቃ ገብረ ሃና አልተከራከሩም። ፈገግ ብለው ወደ ቤታቸው ተመለሱ — ትእዛዙን ቃል በቃል ለመፈጸም። | Gebre Hanna does not argue. He smiles and heads home — to obey the order to the letter. | 7.2 s | 7.26 s | 6.79 s |
| 5 | `s5_dressed` | በረዶ የመሰለ ነጭ ሸማ፣ በወርቅ የተጠለፈ የካቲፋ ካባ፣ የሚያብረቀርቅ ከዘራ። ያው ሰው — ግን ተለውጦ። | Out he steps: a snow-white shamma, a velvet kabba, a polished kezera stick. The same man, transformed. | 9.3 s | 10.24 s | 8.84 s |
| 6 | `s6_welcome` | ተመለሱ፤ ያው ጠባቂ ተደናግጦ እጅ እስኪነካ ዝቅ ብሎ አጎነበሰ፤ እልልታውም እጥፍ ሆነ። | He returns — and the same gatekeeper gasps, bowing nearly to the ground, while the ululations ring twice as loud. | 8.1 s | 8.04 s | 7.61 s |
| 7 | `s7_feast` | ባለድግሱ ወደ ክብር መቀመጫው መሯቸው፤ «አለቃ! ብሉ፣ ጠጡ — ሁሉም ለእርስዎ ነው!» | The host leads him to the seat of honor: "Aleqa! Eat, drink — everything here is yours!" | 7.1 s | 7.25 s | 6.61 s |
| 8 | `s8_deadpan` | ከዚያ ዘፈኑና ከበሮው ጸጥ አለ፤ መላው ዳስም ትንፋሹን ውጦ ጠበቀ። | Then the music falls silent, and the whole das holds its breath. | 6.0 s | 4.96 s | 4.64 s |
| 9 | `s9_mess` | ቀይ ዶሮ ወጥ ዘግነው በነጩ ሸማቸው ላይ ቀቡት፤ ስጋ በእጅጌው፣ ጠጅ በካባው ላይ አፈሰሱ። ባለድግሱም ደንግጠው ጮኹ። | He scoops red doro wot and smears it across his white shamma — meat in the sleeve, tej poured on the cloak. The host cries out. | 8.8 s | 9.19 s | 8.34 s |
| 10 | `s10_punchline` | አለቃ ገብረ ሃና በርጋታ አሉ፦ «ብሉ ልብሶቼ፣ ብሉ! እኔ ራሴን ሆኜ ስመጣ አባረራችሁኝ። ልብሶቼ ሲመጡ ግን የክብር መቀመጫ ሰጣችኋቸው። የጠራችሁት ልብሶቼን እንጂ እኔን አይደለም!» | Says Gebre Hanna, calm as Sunday: "Eat, my clothes, eat! I came as myself, and you turned me away. My clothes came, and you gave them the seat of honor. You invited my clothes — not me!" | 15.8 s | 13.54 s | 12.91 s |

**End card (4.0 s):**

- *ሰውን በልብሱ ሳይሆን በስብዕናው መዝኑት።*
- *Judge a person by their character, not their cloth.*
- — a folk tale of Aleqa Gebre Hanna — made with AI

---

## Subtitles only (as burned into the film)

```
1. The kebero pounds, the tej flows, and the whole das is alive with eskista.
2. Aleqa Gebre Hanna arrives straight from the road: dusty patched gabi,
   worn sandals, and the sharpest eyes in the empire.
3. The gatekeeper looks him up and down with scorn. "This feast is for
   honorable guests, old man! Go home and dress decently!"
4. Gebre Hanna does not argue. He smiles and heads home — to obey the order
   to the letter.
5. Out he steps: a snow-white shamma, a velvet kabba, a polished kezera
   stick. The same man, transformed.
6. He returns — and the same gatekeeper gasps, bowing nearly to the ground,
   while the ululations ring twice as loud.
7. The host leads him to the seat of honor: "Aleqa! Eat, drink — everything
   here is yours!"
8. Then the music falls silent, and the whole das holds its breath.
9. He scoops red doro wot and smears it across his white shamma — meat in
   the sleeve, tej poured on the cloak. The host cries out.
10. Says Gebre Hanna, calm as Sunday: "Eat, my clothes, eat! I came as
    myself, and you turned me away. My clothes came, and you gave them the
    seat of honor. You invited my clothes — not me!"

END CARD: ሰውን በልብሱ ሳይሆን በስብዕናው መዝኑት።
Judge a person by their character, not their cloth.
```

---

## Notes

- For the exact image prompts, cast anchors, panel cuts, and sync status, see
  [`PROMPTS.md`](PROMPTS.md).
- **The cut is 89.7 s** in both 9:16 and 16:9, at 24 fps, with an English
  subtitle track. The narration is 84.4 s as recorded; the storyboard's
  `meta.timing` edits it to 77.8 s without re-recording — internal pauses held
  to 0.40 s and a 5 % pitch-preserving tempo — which leaves room for the held
  beats (the deadpan, the laughing crowd after the punchline) and a 3 s end
  card. The table carries all three numbers per line.
- All ten lines were recorded from this script with `gemini-3.8-flash-tts`,
  voice Kore; every cache sidecar is in sync. No style prefix is sent, so no
  English is read before the Amharic; the TTS terminal noise burst is trimmed
  (`FAILURES.md` F14).
- The 16:9 version is a landscape comic page: the same panel strip centred,
  with the Amharic text in the left margin and the English in the right.
- The tale is retold, not quoted from a copyrighted text; the cast is invented
  and the art is synthetic (see `ETHICS.md`).
