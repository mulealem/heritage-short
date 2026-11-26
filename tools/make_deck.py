"""Build a narrated-slide deck (PDF, PPTX, PNGs) of the walkthrough.

Same twelve scenes as the timed video, at the same 16:9 1080p design, but with
no timings baked in: you advance the slides and talk at your own pace, then
record your screen. `walkthrough/deck/DECK_NOTES.md` has the speaker notes and
a suggested (not required) duration per slide.

Output, in walkthrough/deck/:
  slide_01.png … slide_12.png   1920×1080, one per scene
  deck.pdf                      one page per slide, 16:9, for presenting
  (no .pptx: LibreOffice cannot export PDF to PPTX; the PNGs drop into
   PowerPoint or Slides one per page if you want an editable deck)
  DECK_NOTES.md                 what to say on each slide, and how to record

Rebuild:  python3 tools/make_deck.py
Needs:    chromium (slide rendering), LibreOffice (pptx), ffmpeg (stills)
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DECK = ROOT / "walkthrough" / "deck"


def load_walkthrough():
    spec = importlib.util.spec_from_file_location(
        "make_walkthrough", ROOT / "tools" / "make_walkthrough.py")
    mod = importlib.util.module_from_spec(spec)
    sys.argv = sys.argv[:1]          # the module only defines main()
    spec.loader.exec_module(mod)
    return mod


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("failed: %s\n%s" % (" ".join(map(str, cmd))[:180], (r.stderr or r.stdout)[-600:]))
    return r


def main():
    wk = load_walkthrough()
    DECK.mkdir(parents=True, exist_ok=True)
    wk.OUT = ROOT / "walkthrough"          # slides, stills and captures live here
    (wk.OUT / "slides").mkdir(exist_ok=True)
    (wk.OUT / "stills").mkdir(exist_ok=True)
    (wk.OUT / "clips").mkdir(exist_ok=True)

    wk.still_from_film(ROOT / "outputs" / "film_9x16.mp4", 51.0,
                       wk.OUT / "stills" / "film_9x16.jpg")
    wk.still_from_film(ROOT / "outputs" / "film_16x9.mp4", 50.0,
                       wk.OUT / "stills" / "film_16x9.jpg")

    pages = []
    for i, scene in enumerate(wk.SCENES, 1):
        png = wk.slide(scene)
        dst = DECK / ("slide_%02d.png" % i)
        shutil.copyfile(png, dst)
        pages.append(dst)
        print("  slide %02d  %s" % (i, dst.name))

    # --- PDF: one page per slide, 16:9, image at full page
    html = DECK / "print.html"
    html.write_text(
        '<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        '@page{size:1920px 1080px;margin:0}'
        '*{margin:0;padding:0}body{background:#0f3b43}'
        '.p{width:1920px;height:1080px;page-break-after:always;overflow:hidden}'
        '.p:last-child{page-break-after:auto}'
        'img{width:1920px;height:1080px;display:block}'
        '</style></head><body>'
        + "".join('<div class="p"><img src="file://%s"></div>' % p for p in pages)
        + "</body></html>", encoding="utf-8")
    pdf = DECK / "deck.pdf"
    run([wk.chromium(), "--headless=new", "--no-sandbox", "--disable-gpu",
         "--disable-dev-shm-usage", "--no-pdf-header-footer",
         "--print-to-pdf=%s" % pdf, "file://%s" % html])
    if not pdf.exists():
        sys.exit("PDF was not written")

    # No PPTX: LibreOffice has no PDF->PPTX export filter, and a hand-built
    # OOXML deck risks PowerPoint's "repair this file" prompt. A PDF of 16:9
    # pages presents perfectly well, and the PNGs drop into any slide tool.
    print("  deck.pdf written; for the editable deck run: node tools/make_deck_pptx.js")

    write_notes(wk, len(pages))
    print("deck: %d slides -> %s" % (len(pages), DECK))


def write_notes(wk, n):
    """DECK_NOTES.md: speaker notes, no timings enforced."""
    L = []
    L.append("# Walkthrough deck — speaker notes")
    L.append("")
    L.append("Twelve slides, 16:9. Present `deck.pdf` full-screen,")
    L.append("talk at your own pace, and record your screen with your voice. There is")
    L.append("no timing to hit: the suggested seconds below are what the same script")
    L.append("takes when read calmly, and nothing breaks if you take twice as long.")
    L.append("")
    L.append("The brief wants three things: the architecture, one hard decision, and")
    L.append("one change to the storyboard followed by a rerun that regenerates only")
    L.append("that shot. Slides 4–6 and 9–11 carry those; do not skip 9.")
    L.append("")
    L.append("## Recording")
    L.append("")
    L.append("1. Open `deck.pdf`, press full-screen, and share that window (not the")
    L.append("   whole desktop — it keeps the aspect tidy).")
    L.append("2. Record with OBS, QuickTime, Game Bar or your phone pointed at the")
    L.append("   screen. Voice and screen together is fine; a separate voice file")
    L.append("   also works.")
    L.append("3. Advance on the sentence, not on a clock. You may pause, backtrack or")
    L.append("   repeat a slide.")
    L.append("4. Keep it under five minutes. If you overshoot, the slide to cut is 2")
    L.append("   or 12 — 9, 10 and 11 must stay.")
    L.append("")
    L.append("## The slides")
    L.append("")
    total = 0
    for i, scene in enumerate(wk.SCENES, 1):
        _sid, _kind, dur, heading, narr = scene
        total += dur
        L.append("### %d. %s  ·  about %d s" % (i, heading, dur))
        L.append("")
        L.append("**Say:**")
        L.append("")
        for line in wk.wrap(narr, 76):
            L.append("> " + line)
        L.append("")
        L.append("**Slide:** `slide_%02d.png`" % i)
        L.append("")
    L.append("---")
    L.append("")
    L.append("Read end to end the same script runs %d seconds. The five-minute limit"
             % total)
    L.append("is not close, so there is room to slow down, or to add one sentence of")
    L.append("your own about why this story matters — that is the part a viewer")
    L.append("remembers, and the part no script can write for you.")
    L.append("")
    L.append("## PowerPoint")
    L.append("")
    L.append("`deck.pptx` is a native, editable deck: twelve 16:9 slides with real")
    L.append("text boxes, the film stills as images, and **this script in each")
    L.append("slide's speaker notes** — open Presenter View and the words are in")
    L.append("front of you while the audience sees the slide. It is generated by")
    L.append("`node tools/make_deck_pptx.js`, not converted from the PDF.")
    L.append("")
    L.append("Use `deck.pptx` if you want to present in PowerPoint, Keynote or")
    L.append("Google Slides; use `deck.pdf` if you only need something that opens")
    L.append("anywhere with the layout guaranteed. Both carry the same twelve")
    L.append("slides, and the notes file here is the same script.")
    L.append("")
    L.append("## If you would rather present the HTML")
    L.append("")
    L.append("The same slides exist as HTML under `walkthrough/slides/`; open any of")
    L.append("them in a browser and go full-screen. The PNGs in this folder are")
    L.append("identical, and are what the PDF and PPTX contain.")
    L.append("")
    (DECK / "DECK_NOTES.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
