// Build walkthrough/deck/deck.pptx — 12 native slides, transcript in the notes.
// Run: node tools/make_deck_pptx.js
const pptxgen = require("/usr/lib/node_modules/pptxgenjs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "walkthrough", "deck", "deck.pptx");

// palette, taken from the film's own design
const BG = "0F3B43", CARD = "0B3138", GOLD = "F5B21C", PAPER = "F7EEDA";
const MUTED = "9FC2BD", DIM = "6E8F8B";
const W = 13.33, H = 7.5, M = 0.7;
const SANS = "Segoe UI", MONO = "Consolas";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.33 x 7.5
pres.author = "mulealem";
pres.title = "Eat, My Clothes, Eat! — walkthrough";
pres.subject = "B2W0 AI-Content Generation — The Heritage Short";

// ---------------------------------------------------------------- helpers
const slide = () => {
  const s = pres.addSlide();
  s.background = { color: BG };
  return s;
};

const kicker = (s, text, y = 0.55) =>
  s.addText(text.toUpperCase(), {
    x: M, y, w: W - 2 * M, h: 0.32, margin: 0, fontFace: SANS, fontSize: 12,
    bold: true, color: GOLD, charSpacing: 2,
  });

const title = (s, text, y = 0.9, size = 40, w = W - 2 * M) =>
  s.addText(text, {
    x: M, y, w, h: size / 72 * 1.35, margin: 0, fontFace: SANS, fontSize: size,
    bold: true, color: PAPER,
  });

// a terminal / code block: mono text on a darker card, no border stripe
const block = (s, lines, x, y, w, h, size = 13) =>
  s.addText(lines.map((ln) => ({ text: ln, options: { breakLine: true } })), {
    x, y, w, h, margin: 0.16, fontFace: MONO, fontSize: size, color: "DFF3EF",
    fill: { color: CARD }, valign: "top", paraSpaceAfter: 2,
  });

const foot = (s) =>
  s.addText("Heritage Short · github.com/mulealem/heritage-short · every figure traces to runs.jsonl", {
    x: M, y: H - 0.5, w: W - 2 * M, h: 0.26, margin: 0, fontFace: SANS,
    fontSize: 10, color: DIM,
  });

const notes = (s, say, hint) => s.addNotes(hint ? `${say}\n\n— ${hint}` : say);

// ---------------------------------------------------------------- 1 title
{
  const s = slide();
  kicker(s, "B2W0 · AI-Content Generation · The Heritage Short");
  title(s, "Eat, My Clothes, Eat!", 1.15, 54);
  s.addText("A storyboard-to-film pipeline: one JSON contract, one command, two ratios, no GPU.", {
    x: M, y: 2.55, w: 10.6, h: 0.5, margin: 0, fontFace: SANS, fontSize: 20, color: MUTED,
  });
  const pills = ["9:16", "16:9", "89.7 s", "Amharic narration", "English subtitles"];
  let px = M;
  pills.forEach((p) => {
    const pw = 0.42 + p.length * 0.115;
    s.addText(p, {
      shape: pres.ShapeType.roundRect, rectRadius: 0.18, x: px, y: 3.35, w: pw, h: 0.42,
      margin: 0, align: "center", valign: "middle", fontFace: SANS, fontSize: 13,
      color: "CFE3E0", fill: { color: CARD }, line: { color: "1D545C", width: 1 },
    });
    px += pw + 0.16;
  });
  const promise = [
    ["the architecture", "one contract, nine stages, one command"],
    ["one hard decision", "a reference portrait is a composition prior"],
    ["one live regeneration", "change a prompt, one model call"],
  ];
  promise.forEach((r, i) => {
    const y = 4.55 + i * 0.78;
    s.addText([
      { text: r[0] + "   ", options: { bold: true, color: PAPER, fontSize: 15 } },
      { text: r[1], options: { color: MUTED, fontSize: 14 } },
    ], { x: M, y, w: 9.6, h: 0.4, margin: 0, fontFace: SANS, valign: "middle" });
    s.addShape(pres.ShapeType.line, { x: M, y: y + 0.62, w: 9.6, h: 0,
                                      line: { color: "1D545C", width: 1 } });
  });
  foot(s);
  notes(s,
    "This is a walkthrough of Heritage Short: a pipeline that turns one JSON storyboard into a finished short film. The film is an Ethiopian folk tale, narrated in Amharic with English subtitles.",
    "Say your name and the three things you will show: the architecture, one hard decision, one live regeneration.");
}

// ---------------------------------------------------------------- 2 the film 9:16
{
  const s = slide();
  kicker(s, "the film, as made");
  title(s, "9:16", 0.85, 60, 3.2);
  s.addText("1080×1920 · 24 fps · 89.7 s", {
    x: M, y: 2.25, w: 3.6, h: 0.34, margin: 0, fontFace: SANS, fontSize: 15, color: MUTED,
  });
  ["Amharic voice", "English subtitles", "26 cuts over 10 beats", "drawn on CPU, ~4 min"].forEach((t, i) => {
    s.addText(t, {
      x: M, y: 2.85 + i * 0.42, w: 3.6, h: 0.34, margin: 0, fontFace: SANS, fontSize: 14,
      color: i === 3 ? MUTED : "CFE3E0",
    });
  });
  s.addImage({ path: path.join(ROOT, "walkthrough", "stills", "film_9x16.jpg"),
               x: 4.55, y: 0, w: 4.22, h: H });
  s.addText("one frame of the finished film", {
    x: 9.1, y: 3.1, w: 3.5, h: 0.8, margin: 0, fontFace: SANS, fontSize: 14, color: MUTED,
  });
  s.addText("not a video model\nnot a GPU render", {
    x: 9.1, y: 3.85, w: 3.5, h: 0.9, margin: 0, fontFace: SANS, fontSize: 17, color: PAPER,
    lineSpacingMultiple: 1.3,
  });
  notes(s,
    "The film is a motion comic. Generated panels are cut and moved like a comic page: camera pushes, over-the-shoulder cuts, speech balloons, sound effects, word-by-word captions. There is no video model and no GPU in this film; the picture is drawn on the CPU in about four minutes.",
    "The still on the right is a real frame — panel, English caption, subtitle.");
}

// ---------------------------------------------------------------- 3 16:9
{
  const s = slide();
  kicker(s, "the same timeline, rendered twice");
  title(s, "16:9 — a comic page, not a letterbox", 0.85, 30);
  const availH = H - 1.62 - 0.62;            // title above, caption below
  const imgH = availH, imgW = imgH * 16 / 9;  // 16:9, never stretched
  s.addImage({ path: path.join(ROOT, "walkthrough", "stills", "film_16x9.jpg"),
               x: (W - imgW) / 2, y: 1.62, w: imgW, h: imgH });
  s.addText("the panel strip at full height · Amharic in the left margin · English in the right", {
    x: M, y: 1.62 + imgH + 0.12, w: W - 2 * M, h: 0.3, margin: 0, fontFace: SANS,
    fontSize: 13, color: MUTED, align: "center",
  });
  notes(s,
    "The same timeline renders twice. The landscape version is a comic page: the panel strip stays centred at full height, the spoken Amharic runs down the left margin, the English down the right. One film data file, one audio master, two layouts.",
    "Both ratios come from one film.json and one audio master; the renderer is compiled once per layout.");
}

// ---------------------------------------------------------------- 4 the contract
{
  const s = slide();
  kicker(s, "the contract");
  title(s, "One file, validated before every stage", 0.85, 32);
  block(s, [
    "{",
    '  "id": "s5_dressed",',
    '  "duration_s": 9.3,',
    '  "framing": "medium_to_wide",',
    '  "image_prompt": "comic book hero panel, low dramatic angle at the stone doorway: …",',
    '  "narration": { "lang": "am", "text": "በረዶ የመሰለ ነጭ ሸማ፣ …" },',
    '  "reason": "The transformation shot — the clothes arrive as a character of their own, …",',
    '  "seed": 105',
    "}",
  ], M, 1.5, 11.9, 3.05, 12);
  s.addText([
    { text: "+ comic/panels.json", options: { bold: true, color: PAPER } },
    { text: "  how each beat is cut: panels, cut points, balloons, SFX, which portrait anchors a cut", options: { color: MUTED } },
  ], { x: M, y: 5.75, w: 11.9, h: 0.4, margin: 0, fontFace: SANS, fontSize: 14 });
  s.addText("Every stage validates this against the schema before it runs — a broken contract stops the build before a model is called.", {
    x: M, y: 6.25, w: 11.9, h: 0.6, margin: 0, fontFace: SANS, fontSize: 14, color: MUTED,
  });
  notes(s,
    "Everything starts from storyboard.json: ten beats, each with a duration, an image prompt, a motion prompt, the narration and its English line, a reason, and a seed. Beside it, panels.json says how each beat is cut. Every stage validates this against the schema before it runs, so a broken contract stops the build before a model is called.",
    "Ten beats, ten reasons: the reason is what the shot is for, and it is in the contract, not in my head.");
}

// ---------------------------------------------------------------- 5 nine stages
{
  const s = slide();
  kicker(s, "make short");
  title(s, "Nine stages, one command", 0.85, 32);
  const stages = [
    ["1  validate", "schema check", "storyboard"],
    ["2  narration", "Gemini 3.8 TTS", "10 lines"],
    ["3  cast", "image-01", "2 portraits"],
    ["4  keyframes", "image-01", "11 stills"],
    ["5  panels", "image-01", "16 panels"],
    ["6  build", "stdlib", "film.json"],
    ["7  score", "own code", "qenet bed"],
    ["8  render 9:16", "fframes · CPU", "picture"],
    ["9  render 16:9", "cargo feature wide", "landscape page"],
  ];
  const cw = (W - 2 * M - 2 * 0.28) / 3, ch = 0.92;
  stages.forEach((st, i) => {
    const x = M + (i % 3) * (cw + 0.28), y = 1.68 + Math.floor(i / 3) * (ch + 0.34);
    s.addText([
      { text: st[0], options: { fontSize: 17, bold: true, color: PAPER, breakLine: true } },
      { text: st[1], options: { fontSize: 12.5, color: MUTED, breakLine: true } },
      { text: st[2], options: { fontSize: 12.5, color: GOLD } },
    ], { x, y, w: cw, h: ch, margin: 0.16, fontFace: SANS, fill: { color: CARD }, valign: "top" });
  });
  foot(s);
  notes(s,
    "The pipeline is nine stages. Narration records ten lines. Two cast portraits anchor the characters. Keyframes and sixteen interaction panels are generated from prompts. The build turns them into a timeline, the score is synthesised from that timeline, and the picture is rendered in both ratios and muxed with one audio master.",
    "Stage 6 is pure stdlib; stages 7–9 run on this machine, which is why the film costs nothing to re-render.");
}

// ---------------------------------------------------------------- 6 clone
{
  const s = slide();
  kicker(s, "reproducibility");
  title(s, "Clone → both films, no keys", 0.85, 34);
  block(s, [
    "$ git clone … && make short      # no .env, no API keys",
    "DONE film_9x16.mp4: 89.7s, 81.6 MB",
    "DONE film_16x9.mp4: 89.7s, 65.7 MB",
    "",
    "this run: 0 real model call(s), 39 cache hit(s), 0 error(s)",
    "real\t9m16.878s      # Rust build included",
  ], M, 1.62, 11.4, 2.55, 13.5);
  s.addText("Thirty-nine cached artifacts, two CPU renders, no credentials — the model outputs are committed precisely so this is possible.", {
    x: M, y: 4.45, w: 10.4, h: 0.9, margin: 0, fontFace: SANS, fontSize: 17, color: MUTED,
  });
  foot(s);
  notes(s,
    "One command runs all of it. On a fresh clone with no API keys, both films rebuild from the committed cache: zero model calls, thirty-nine cache hits, about nine minutes including the Rust build.",
    "If asked why outputs/ is committed: it is the cache and the evidence. Without it a clone needs a key and quota; with it, the film is reproducible for free.");
}

// ---------------------------------------------------------------- 7 hard decision
{
  const s = slide();
  kicker(s, "the hard decision");
  title(s, "A reference portrait is a composition prior", 0.85, 32);
  const ih = 3.85, iw = ih * 9 / 16;   // 9:16 exactly
  s.addImage({ path: path.join(ROOT, "outputs", "keyframes", "s6_welcome.png"),
               x: M, y: 1.55, w: iw, h: ih });
  s.addImage({ path: path.join(ROOT, "outputs", "comic_panels", "s10_punchline_x1.jpg"),
               x: M + iw + 0.45, y: 1.55, w: iw, h: ih });
  s.addText([
    { text: "Wide shot\n", options: { bold: true, color: GOLD, fontSize: 15, breakLine: true } },
    { text: "described in full, no portrait attached, so the model composes the scene", options: { color: MUTED, fontSize: 13 } },
  ], { x: M, y: 5.55, w: iw + 0.55, h: 1.1, margin: 0, fontFace: SANS, lineSpacingMultiple: 1.15 });
  s.addText([
    { text: "Close-up\n", options: { bold: true, color: GOLD, fontSize: 15, breakLine: true } },
    { text: "portrait + that character's identity directive attached", options: { color: MUTED, fontSize: 13 } },
  ], { x: M + iw + 0.45, y: 5.55, w: iw + 0.55, h: 1.1, margin: 0, fontFace: SANS, lineSpacingMultiple: 1.15 });
  s.addText([
    { text: "What went wrong\n", options: { bold: true, color: PAPER, fontSize: 15, breakLine: true } },
    { text: "Attached to a wide prompt, the portrait produced a giant head over a tiny scene — a composition prior, not just an identity prior. One directive written for the hero also leaked his turban onto the bare-headed gatekeeper.", options: { color: MUTED, fontSize: 13 } },
  ], { x: 6.55, y: 1.55, w: 6.05, h: 3.3, margin: 0, fontFace: SANS, lineSpacingMultiple: 1.25 });
  s.addText("Rule that survived: anchor the close-ups, describe the wides.", {
    x: 6.55, y: 4.95, w: 6.05, h: 0.6, margin: 0, fontFace: SANS, fontSize: 16, bold: true, color: GOLD,
  });
  foot(s);
  notes(s,
    "The hardest problem was keeping a character the same person across twenty-six cuts without wrecking the shot. A reference portrait holds the face, but it is also a composition prior: attached to a wide shot it produced a giant head over a tiny scene. So: anchor the close-ups, and describe the wides in full.",
    "FAILURES.md F13 and EXPERIMENTS.md E9 have the before/after; this cost a full regeneration of the anchored keyframes to learn.");
}

// ---------------------------------------------------------------- 8 the change
{
  const s = slide();
  kicker(s, "the live change");
  title(s, "One prompt, one line of JSON", 0.85, 34);
  block(s, [
    "$ git diff storyboard.json",
    "  s5_dressed — one shot of ten, one field of eight",
    "",
    "-  … kezera walking stick firmly on the stone step, radiant golden backlight",
    "+  … stick firmly on the stone step, red leather slippers, radiant golden backlight",
    "",
    "1 file changed, 1 insertion(+), 1 deletion(-)",
  ], M, 1.75, 11.9, 3.2, 14);
  s.addText("Nothing else in the storyboard changed. Same seed, same size, same reference.", {
    x: M, y: 5.35, w: 11.4, h: 0.4, margin: 0, fontFace: SANS, fontSize: 15, color: MUTED,
  });
  s.addText("Next slide: the rerun.", {
    x: M, y: 5.85, w: 11.4, h: 0.4, margin: 0, fontFace: SANS, fontSize: 15, bold: true, color: GOLD,
  });
  foot(s);
  notes(s,
    "Here is the live part. I change one image prompt — one shot, one line of the storyboard.",
    "If you demo live instead of showing this slide, change exactly this field and run `python3 -m pipeline.keyframes`.");
}

// ---------------------------------------------------------------- 9 the rerun
{
  const s = slide();
  kicker(s, "rerun the same stage");
  title(s, "Ten cache hits, one model call", 0.85, 32);
  block(s, [
    "$ python3 -m pipeline.keyframes",
    "  s5_dressed: ok",
    "  … and 10 other jobs: cache hit",
    "",
    "  cache hits 10   model calls 1",
    "  keyframes done -> outputs/keyframes",
  ], M, 1.62, 6.9, 2.3, 14);
  s.addText([
    { text: "1 call · 17.9 s · $0.0035\n", options: { bold: true, color: GOLD, fontSize: 15, breakLine: true } },
    { text: "seed 105 — recorded in runs.jsonl", options: { color: MUTED, fontSize: 13 } },
  ], { x: M, y: 4.65, w: 6.6, h: 0.9, margin: 0, fontFace: SANS, lineSpacingMultiple: 1.2 });
  const rih = 4.2, riw = rih * 9 / 16;
  s.addImage({ path: path.join(ROOT, "walkthrough", "regenerated.jpg"),
               x: 9.1, y: 1.62, w: riw, h: rih });
  s.addText("the only image drawn", {
    x: 8.6, y: 5.95, w: riw + 1.0, w: 2.25, h: 0.3, margin: 0, fontFace: SANS, fontSize: 12, color: MUTED, align: "center",
  });
  foot(s);
  notes(s,
    "Then I rerun the keyframe stage. Ten jobs are served from the cache. One image is drawn: seventeen point nine seconds, about a third of a cent. The log records exactly one call, with its seed.",
    "This is the demo the brief asks for: change one prompt, rerun, and only that shot regenerates.");
}

// ---------------------------------------------------------------- 10 the log
{
  const s = slide();
  kicker(s, "the evidence");
  title(s, "runs.jsonl — one line per call", 0.85, 32);
  block(s, [
    '{"stage": "keyframes", "model": "flux", "seed": 110, "latency_ms": null,',
    ' "status": "cache", "cost_usd_est": null}',
    '{"stage": "keyframes", "model": "image-01", "seed": 105, "latency_ms": 17879,',
    ' "status": "ok", "cost_usd_est": 0.0035}',
    "",
    "# whole project, every iteration:",
    "  image-01   $0.4760 (136)     FLUX draft $0.1164 (97)",
    "  Gemini TTS $0.0614  (52)     TOTAL      $0.6538",
  ], M, 1.58, 11.9, 2.35, 12.5);
  s.addText("Every number in the documentation — latency, cost, cache hit — is a line in this file. The assets in the final film: eleven cents.", {
    x: M, y: 4.15, w: 11.6, h: 0.6, margin: 0, fontFace: SANS, fontSize: 15, color: MUTED,
  });
  const stats = [["$0.65", "whole project"], ["$0.11", "the final film"], ["0", "GPU minutes"]];
  stats.forEach((st, i) => {
    const x = M + i * 4.0;
    s.addText([
      { text: st[0] + "\n", options: { fontSize: 34, bold: true, color: GOLD, breakLine: true } },
      { text: st[1], options: { fontSize: 14, color: MUTED } },
    ], { x, y: 5.0, w: 3.4, h: 1.15, margin: 0, fontFace: SANS, valign: "top" });
  });
  foot(s);
  notes(s,
    "Every call lands in runs.jsonl with its model, parameters, seed, latency and cost. The whole project, every iteration included, came to about sixty-five cents at list prices. The assets in the final film: eleven cents.",
    "COSTS.md is generated from this log by tools/cost_report.py — no figure is remembered.");
}

// ---------------------------------------------------------------- 11 limits
{
  const s = slide();
  kicker(s, "limits");
  title(s, "What this is not", 0.85, 34);
  const rows = [
    ["No video model", "the Wan 2.2 clip route is implemented, documented, and untested"],
    ["No music model", "the score is a bed this repository's own code synthesises"],
    ["No audience test", "stated in DESIGN.md, not invented — the protocol is written down instead"],
    ["0 GPU minutes", "the whole film was drawn on this machine's CPU"],
  ];
  rows.forEach((r, i) => {
    const y = 1.75 + i * 1.15;
    s.addText([
      { text: r[0], options: { bold: true, fontSize: 18, color: PAPER, breakLine: true } },
      { text: r[1], options: { fontSize: 13.5, color: MUTED } },
    ], { x: M, y, w: 11.6, h: 0.9, margin: 0, fontFace: SANS, valign: "top",
         paraSpaceAfter: 4 });
    if (i < rows.length - 1) {
      s.addShape(pres.ShapeType.line, {
        x: M, y: y + 1.02, w: 11.6, h: 0, line: { color: "1D545C", width: 1 },
      });
    }
  });
  foot(s);
  notes(s,
    "What this is not. There is no video model in the film: the clip route is implemented and untested. There is no music model: the score is a bed my own code synthesises. And the audience test the brief asks for was not run — that is written down in DESIGN.md rather than invented.",
    "Saying this plainly is deliberate: FAILURES.md F1–F19 are the same habit.");
}

// ---------------------------------------------------------------- 12 end
{
  const s = slide();
  kicker(s, "walkthrough ends");
  s.addText([
    { text: "github.com/mulealem/", options: { color: PAPER } },
    { text: "heritage-short", options: { color: GOLD } },
  ], { x: M, y: 1.5, w: 11.9, h: 0.9, margin: 0, fontFace: SANS, fontSize: 40, bold: true });
  s.addText("Repository · both films in Releases · this deck and its notes in walkthrough/deck/", {
    x: M, y: 2.75, w: 11.5, h: 0.5, margin: 0, fontFace: SANS, fontSize: 17, color: MUTED,
  });
  s.addText("make short   ·   make check   ·   make verify", {
    x: M, y: 3.4, w: 11.5, h: 0.4, margin: 0, fontFace: MONO, fontSize: 15, color: "CFE3E0",
  });
  s.addText([
    { text: "the films\n", options: { bold: true, color: GOLD, fontSize: 13, breakLine: true } },
    { text: "github.com/mulealem/heritage-short/releases/download/release/film_9x16.mp4\n", options: { fontSize: 11, color: MUTED, breakLine: true } },
    { text: "github.com/mulealem/heritage-short/releases/download/release/film_16x9.mp4", options: { fontSize: 11, color: MUTED } },
  ], { x: M, y: 4.35, w: 11.5, h: 1.2, margin: 0, fontFace: MONO, lineSpacingMultiple: 1.3 });
  notes(s,
    "The repository, both films and this transcript are linked below. Every number in the documentation can be checked against the run log.",
    "Stop talking here; let the slide sit for a beat before you cut.");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("wrote " + OUT));
