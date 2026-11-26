"""Build the walkthrough video (silent master) and its transcript.

What it makes, in `walkthrough/`:

  slides/NN.png         each screen, 1920x1080, rendered from the real repo
                        (every scene is a still: a pure slide deck)
  stills/*.jpg          one frame from each finished film, for the two film slides
  walkthrough_silent.mp4  the cut, 1080p30, no audio — record your voice over this
                          (every scene is a still: a pure slide deck)
  WALKTHROUGH.srt       one subtitle per scene, timed to the cut
  TRANSCRIPT.md         the narration script, timed, plus how to record and mux

Everything on screen is real: the contract excerpt is read from
storyboard.json, the terminal panels are the captured output of a genuine
one-prompt regeneration, the cost table comes from tools/cost_report.py, and
the two film stills are frames of outputs/film_*.mp4. Nothing here is mocked,
and nothing is a video insert — the deck is all stills.

Requires: chromium (headless screenshots), ffmpeg. Usage:

    python3 tools/make_walkthrough.py [--demo-log PATH] [--demo-shot PATH]

`--demo-log` defaults to walkthrough/terminal_demo.txt (the captured run) and
`--demo-shot` to the regenerated image from that run.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "walkthrough"
W, H, FPS = 1920, 1080, 30
TEAL, INK, GOLD, PAPER = "#0f3b43", "#14100c", "#f5b21c", "#f7eeda"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


# --------------------------------------------------------------------- scenes
# (id, kind, seconds, on-screen heading, narration for the voice-over)
SCENES = [
    ("01_title", "slide", 9,
     "Eat, My Clothes, Eat!",
     "This is a walkthrough of Heritage Short: a pipeline that turns one JSON "
     "storyboard into a finished short film. The film is an Ethiopian folk tale, "
     "narrated in Amharic with English subtitles."),
    ("02_vertical", "slide", 19,
     "9:16 — 1080×1920 · 89.7 s",
     "The film is a motion comic. Generated panels are cut and moved like a comic "
     "page: camera pushes, over-the-shoulder cuts, speech balloons, sound effects, "
     "word-by-word captions. There is no video model and no GPU in this film; the "
     "picture is drawn on the CPU in about four minutes."),
    ("03_landscape", "slide", 17,
     "16:9 — the same timeline, a comic page",
     "The same timeline renders twice. The landscape version is a comic page: the "
     "panel strip stays centred at full height, the spoken Amharic runs down the "
     "left margin, the English down the right. One film data file, one audio "
     "master, two layouts."),
    ("04_contract", "slide", 24,
     "storyboard.json — the contract",
     "Everything starts from storyboard.json: ten beats, each with a duration, an "
     "image prompt, a motion prompt, the narration and its English line, a reason, "
     "and a seed. Beside it, panels.json says how each beat is cut. Every stage "
     "validates this against the schema before it runs, so a broken contract stops "
     "the build before a model is called."),
    ("05_stages", "slide", 22,
     "make short — nine stages, one command",
     "The pipeline is nine stages. Narration records ten lines. Two cast portraits "
     "anchor the characters. Keyframes and sixteen interaction panels are generated "
     "from prompts. The build turns them into a timeline, the score is synthesised "
     "from that timeline, and the picture is rendered in both ratios and muxed with "
     "one audio master."),
    ("06_command", "slide", 20,
     "A clone rebuilds both films with no keys",
     "One command runs all of it. On a fresh clone with no API keys, both films "
     "rebuild from the committed cache: zero model calls, thirty-nine cache hits, "
     "about nine minutes including the Rust build."),
    ("07_decision", "slide", 26,
     "The hard decision: a reference is a composition prior",
     "The hardest problem was keeping a character the same person across twenty-six "
     "cuts without wrecking the shot. A reference portrait holds the face, but it is "
     "also a composition prior: attached to a wide shot it produced a giant head over "
     "a tiny scene. So: anchor the close-ups, and describe the wides in full."),
    ("08_diff", "slide", 14,
     "Change one prompt",
     "Here is the live part. I change one image prompt — one shot, one line of the "
     "storyboard."),
    ("09_run", "slide", 22,
     "Rerun the stage: ten cache hits, one call",
     "Then I rerun the keyframe stage. Ten jobs are served from the cache. One image is "
     "drawn: seventeen point nine seconds, about a third of a cent. The log records "
     "exactly one call, with its seed."),
    ("10_log", "slide", 20,
     "runs.jsonl — one line per call",
     "Every call lands in runs.jsonl with its model, parameters, seed, latency and "
     "cost. The whole project, every iteration included, came to about sixty-five "
     "cents at list prices. The assets in the final film: eleven cents."),
    ("11_limits", "slide", 24,
     "What this is not",
     "What this is not. There is no video model in the film: the clip route is "
     "implemented and untested. There is no music model: the score is a bed my own "
     "code synthesises. And the audience test the brief asks for was not run — that "
     "is written down in DESIGN.md rather than invented."),
    ("12_end", "slide", 12,
     "github.com/mulealem/heritage-short",
     "The repository, both films and this transcript are linked below. Every number "
     "in the documentation can be checked against the run log."),
]

FONT_ET = ROOT / "editor" / "fonts" / "NotoSansEthiopic.ttf"

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"ET";src:url("file://%(FONT)s") format("truetype")}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;overflow:hidden}
body{background:%(TEAL)s;color:%(PAPER)s;
     font:%(FS)spx/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif,"ET";
     padding:64px 88px}
.et{font-family:"ET",system-ui,sans-serif}
pre,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace,"ET"}
     padding:64px 88px}
.kicker{color:%(GOLD)s;font-size:26px;letter-spacing:.16em;text-transform:uppercase;font-weight:700}
h1{font-size:%(H1)dpx;line-height:1.08;margin:18px 0 0;font-weight:800}
h1 .url{color:%(GOLD)s}
.rule{width:240px;height:6px;background:%(GOLD)s;margin:26px 0 30px}
.lead{font-size:34px;color:#cfe3e0;max-width:1500px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace,"ET";
    background:#0a2a30;border:1px solid #1d545c;border-radius:12px;
    padding:26px 30px;font-size:%(PRE)dpx;line-height:1.5;color:#dff3ef;overflow:hidden}
pre .g{color:#7ddba8}.pre .y{color:%(GOLD)s}
.dim{color:#9fc2bd}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:8px}
.step{background:#0b3138;border:1px solid #1d545c;border-top:5px solid %(GOLD)s;
      border-radius:10px;padding:18px 20px}
.step b{font-size:27px;display:block}
.step span{font-size:20px;color:#a9cbc6}
.step i{display:block;font-size:19px;color:%(GOLD)s;font-style:normal;margin-top:6px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:34px;align-items:start}
.two figure{background:#0b3138;border:1px solid #1d545c;border-radius:12px;padding:16px}
.two img{width:100%%;height:560px;object-fit:contain;display:block;background:#08252a;border-radius:8px}
.two figcaption{font-size:24px;color:#cfe3e0;margin-top:12px}
.two figcaption b{color:%(GOLD)s}
.foot{position:absolute;left:88px;bottom:44px;font-size:22px;color:#8fb3ae}
.pill{display:inline-block;background:#0b3138;border:1px solid #1d545c;color:#cfe3e0;
      border-radius:999px;padding:6px 16px;font-size:22px;margin-right:10px}
</style></head><body>%(body)s<div class="foot">%(foot)s</div></body></html>"""

FOOT = "Heritage Short · github.com/mulealem/heritage-short · run log: runs.jsonl"


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.exit("failed: %s\n%s" % (" ".join(map(str, cmd))[:200], (r.stderr or r.stdout)[-800:]))
    return r


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def body_title(o):
    return ('<div class="kicker">B2W0 · AI-Content Generation · The Heritage Short</div>'
            '<h1>%s</h1><div class="rule"></div>'
            '<p class="lead">A storyboard-to-film pipeline: one JSON contract, one command, '
            'two ratios, no GPU.</p>'
            '<p style="margin-top:26px"><span class="pill">9:16</span><span class="pill">16:9</span>'
            '<span class="pill">89.7 s</span><span class="pill">Amharic narration</span>'
            '<span class="pill">English subtitles</span></p>'
            % esc(o["heading"]))


def body_contract(o):
    sb = json.loads((ROOT / "storyboard.json").read_text())
    shot = sb["shots"][4]
    snippet = {
        "id": shot["id"],
        "duration_s": shot["duration_s"],
        "framing": shot.get("framing"),
        "image_prompt": shot["image_prompt"][:84] + " …",
        "narration": {"lang": "am", "text": shot["narration"]["text"][:38] + " …"},
        "reason": shot["reason"][:64] + " …",
        "seed": shot["seed"],
    }
    txt = esc(json.dumps(snippet, ensure_ascii=False, indent=2))
    return ('<div class="kicker">the contract</div><h1>One file, validated before every stage</h1>'
            '<div class="rule"></div><pre>%s</pre>'
            '<p class="lead dim" style="margin-top:22px">+ <span class="mono">comic/panels.json</span>: '
            'how each beat is cut — panels, cut points, balloons, SFX, which portrait anchors a cut.</p>'
            % txt)


def body_vertical(o):
    left = ('<div style="position:absolute;left:88px;top:150px;width:520px">'
            '<div class="kicker">the film</div>'
            '<h1 style="font-size:104px">9:16</h1>'
            '<div class="rule"></div>'
            '<p class="lead" style="font-size:26px">1080×1920 · 24 fps<br>89.7 s</p>'
            '<p style="margin-top:22px"><span class="pill">Amharic</span></p>'
            '<p style="margin-top:8px"><span class="pill">English subtitles</span></p>'
            '</div>')
    right = ('<div style="position:absolute;left:1320px;top:150px;width:510px">'
             '<div class="kicker">on screen</div>'
             '<p class="lead" style="font-size:26px;margin-top:18px">motion comic, not video</p>'
             '<p class="lead" style="font-size:26px;margin-top:14px">26 cuts over 10 beats</p>'
             '<p class="lead" style="font-size:26px;margin-top:14px">balloons · sound effects · captions</p>'
             '<p class="lead" style="font-size:26px;margin-top:14px">drawn on CPU in ~4 min</p>'
             '<p class="lead dim" style="font-size:22px;margin-top:26px">no GPU · no video API</p>'
             '</div>')
    return left + right


def body_film_vertical(o):
    still = OUT / "stills" / "film_9x16.jpg"
    left = ('<div style="position:absolute;left:88px;top:120px;width:430px">'
            '<div class="kicker">the film, as made</div>'
            '<h1 style="font-size:92px">9:16</h1>'
            '<div class="rule"></div>'
            '<p class="lead" style="font-size:24px">1080×1920 · 24 fps · 89.7 s</p>'
            '<p style="margin-top:20px"><span class="pill">Amharic</span></p>'
            '<p style="margin-top:8px"><span class="pill">English subtitles</span></p>'
            '<p class="lead dim" style="font-size:21px;margin-top:26px">one frame of the '
            'finished film: panel, caption, subtitle</p>'
            '</div>')
    img = ('<img src="file://%s" style="position:absolute;left:600px;top:0;height:1080px;'
           'border-left:3px solid %s;border-right:3px solid %s">' % (still, GOLD, GOLD))
    right = ('<div style="position:absolute;left:1300px;top:180px;width:530px">'
             '<div class="kicker">what it is not</div>'
             '<p class="lead" style="font-size:25px;margin-top:16px">not a video model</p>'
             '<p class="lead" style="font-size:25px;margin-top:12px">not a GPU render</p>'
             '<p class="lead dim" style="font-size:22px;margin-top:22px">26 cuts over 10 beats, '
             'drawn on the CPU in about four minutes</p>'
             '</div>')
    return left + img + right


def body_film_landscape(o):
    still = OUT / "stills" / "film_16x9.jpg"
    return ('<div class="kicker">the same timeline, rendered twice</div>'
            '<h1 style="font-size:52px">16:9 — a comic page, not a letterbox</h1>'
            '<div class="rule" style="margin:18px 0 20px"></div>'
            '<img src="file://%s" style="display:block;width:1440px;margin:0 auto;'
            'border:2px solid %s;border-radius:8px">' % (still, GOLD))


def body_stages(o):
    steps = [("1 · validate", "schema check", "storyboard"),
             ("2 · narration", "Gemini TTS", "10 lines"),
             ("3 · cast", "image-01", "2 portraits"),
             ("4 · keyframes", "image-01", "11 stills"),
             ("5 · panels", "image-01", "16 panels"),
             ("6 · build", "stdlib", "film.json"),
             ("7 · score", "own code", "qenet bed"),
             ("8 · render 9:16", "fframes · CPU", "picture"),
             ("9 · render 16:9", "cargo feature wide", "landscape page")]
    cells = "".join('<div class="step"><b>%s</b><span>%s</span><i>%s</i></div>' % s for s in steps)
    return ('<div class="kicker">make short</div><h1>Nine stages, one command</h1>'
            '<div class="rule"></div><div class="grid">%s</div>' % cells)


def body_command(o):
    clone = (OUT / "terminal_clone.txt")
    txt = esc(clone.read_text().strip()) if clone.exists() else ""
    return ('<div class="kicker">reproducibility</div><h1>Clone → both films, no keys</h1>'
            '<div class="rule"></div><pre>%s</pre>'
            '<p class="lead" style="margin-top:26px">Thirty-nine cached artifacts, two CPU '
            'renders, no credentials — the model outputs are committed precisely so this '
            'is possible.</p>' % txt)


def body_decision(o):
    a = ROOT / "outputs" / "keyframes" / "s6_welcome.png"
    b = ROOT / "outputs" / "comic_panels" / "s10_punchline_x1.jpg"
    return ('<div class="kicker">the hard decision</div>'
            '<h1>A reference portrait is a composition prior</h1><div class="rule"></div>'
            '<div class="two">'
            '<figure><img src="file://%s"><figcaption><b>Wide shot</b> — described in full, '
            'no reference attached, so the model composes the scene</figcaption></figure>'
            '<figure><img src="file://%s"><figcaption><b>Close-up</b> — portrait + that '
            "character's identity directive attached</figcaption></figure>"
            '</div>' % (a, b))


def body_diff(o):
    txt = esc((OUT / "terminal_diff.txt").read_text().strip())
    return ('<div class="kicker">the live change</div><h1>One prompt, one line of JSON</h1>'
            '<div class="rule"></div><pre>%s</pre>' % txt)


def body_run(o):
    txt = esc((OUT / "terminal_run.txt").read_text().strip())
    shot = OUT / "regenerated.jpg"
    img = ('<img src="file://%s" style="height:620px;border-radius:10px;border:2px solid #1d545c">'
           % shot) if shot.exists() else ""
    half = (W - 88 * 2 - 60) // 2
    return ('<div class="kicker">rerun the same stage</div>'
            '<h1>Ten cache hits, one model call</h1><div class="rule"></div>'
            '<div style="display:grid;grid-template-columns:%dpx 1fr;gap:44px;align-items:start">'
            '<pre style="font-size:20px">%s</pre><div style="text-align:center">%s'
            '<p class="dim" style="font-size:22px;margin-top:10px">the only image drawn</p></div></div>'
            % (half, txt, img))


def body_log(o):
    txt = esc((OUT / "terminal_log.txt").read_text().strip())
    return ('<div class="kicker">the evidence</div><h1>runs.jsonl — one line per call</h1>'
            '<div class="rule"></div><pre style="font-size:22px">%s</pre>'
            '<p class="lead" style="margin-top:24px">Every number in the documentation — '
            'latency, cost, cache hit — is a line in this file.</p>' % txt)


def body_limits(o):
    items = [("No video model", "the Wan 2.2 clip route is implemented, documented, untested"),
             ("No music model", "the score is a bed synthesised by this repo's code"),
             ("No audience test", "stated in DESIGN.md, not invented"),
             ("0 GPU minutes", "the whole film was drawn on the CPU")]
    cells = "".join('<div class="step"><b>%s</b><span>%s</span></div>' % i for i in items)
    return ('<div class="kicker">limits</div><h1>What this is not</h1>'
            '<div class="rule"></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">%s</div>'
            '<p class="lead dim" style="margin-top:26px">Each of these is a line in FAILURES.md '
            'or DESIGN.md, written before anyone asked.</p>' % cells)


def body_end(o):
    return ('<div class="kicker">walkthrough ends</div>'
            '<h1>github.com/mulealem/<span class="url">heritage-short</span></h1>'
            '<div class="rule"></div>'
            '<p class="lead">Repository · both films in Releases · transcript in '
            '<span class="mono">walkthrough/TRANSCRIPT.md</span></p>'
            '<p class="lead dim" style="margin-top:18px">Make it: <span class="mono">make short</span> '
            '· check it: <span class="mono">make check</span></p>')


BODIES = {"04_contract": body_contract, "05_stages": body_stages, "06_command": body_command,
          "02_vertical": body_film_vertical,
          "03_landscape": body_film_landscape,
          "07_decision": body_decision, "08_diff": body_diff, "09_run": body_run,
          "10_log": body_log, "11_limits": body_limits, "12_end": body_end}


# --------------------------------------------------------------------- render
def chromium():
    for c in ("chromium", "chromium-browser", "google-chrome"):
        if shutil.which(c):
            return shutil.which(c)
    sys.exit("chromium not found — install it, or screenshot the slides by hand")


def still_from_film(src, t, dst):
    """One frame of the finished film, as a still for a slide."""
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", "%.3f" % t,
        "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dst)])
    return dst


def slide(scene):
    sid, _, dur, heading, _n = scene
    body = BODIES.get(sid, body_title)({"heading": heading})
    foot = "" if sid in ("02_vertical", "03_landscape") else FOOT
    html = OUT / "slides" / (sid + ".html")
    html.write_text(PAGE % dict(W=W, H=H, FS=26, H1=66, PRE=25, TEAL=TEAL, GOLD=GOLD,
                                PAPER=PAPER, FONT=FONT_ET, body=body, foot=foot),
                    encoding="utf-8")
    png = OUT / "slides" / (sid + ".png")
    sh([chromium(), "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage",
        "--hide-scrollbars", "--force-device-scale-factor=1",
        "--window-size=%d,%d" % (W, H), "--virtual-time-budget=3000",
        "--screenshot=%s" % png, "file://%s" % html])
    if not png.exists():
        sys.exit("screenshot failed for %s" % sid)
    return png


def video_from_png(png, dur, dst):
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
        "-i", str(png), "-t", "%.3f" % dur, "-vf",
        "scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=%s,format=yuv420p"
        % (W, H, W, H, TEAL),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", str(FPS), str(dst)])


def video_from_clip_framed(bg, src, start, dur, dst):
    """Vertical clip over a designed background: full height, centred, hairline border."""
    strip_w = 608
    x = (W - strip_w) // 2
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-loop", "1", "-framerate", str(FPS), "-i", str(bg),
        "-ss", "%.3f" % start, "-t", "%.3f" % dur, "-i", str(src),
        "-filter_complex",
        "[0:v]scale=%d:%d[bg];[1:v]trim=duration=%.3f,setpts=PTS-STARTPTS,"
        "scale=%d:1080:flags=lanczos[v];[bg][v]overlay=%d:0:shortest=1,"
        "drawbox=x=%d:y=0:w=%d:h=1080:color=%s@0.85:t=3,format=yuv420p"
        % (W, H, dur, strip_w, x, x - 1, strip_w + 2, GOLD),
        "-t", "%.3f" % dur, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
        "-crf", "20", str(dst)])


def video_from_clip(src, start, dur, dst, ratio):
    if ratio == "9x16":
        vf = ("trim=start=%.3f:duration=%.3f,setpts=PTS-STARTPTS,scale=-2:%d,"
              "pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=%s" % (start, dur, H, W, H, TEAL))
    else:
        vf = ("trim=start=%.3f:duration=%.3f,setpts=PTS-STARTPTS,scale=%d:%d"
              % (start, dur, W, H))
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-vf", vf + ",format=yuv420p", "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "20", "-r", str(FPS), "-t", "%.3f" % dur, str(dst)])


def srt_ts(t):
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def wrap(text, width=68):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "slides").mkdir(exist_ok=True)
    (OUT / "clips").mkdir(exist_ok=True)
    (OUT / "stills").mkdir(exist_ok=True)
    still_from_film(ROOT / "outputs" / "film_9x16.mp4", 51.0, OUT / "stills" / "film_9x16.jpg")
    still_from_film(ROOT / "outputs" / "film_16x9.mp4", 50.0, OUT / "stills" / "film_16x9.jpg")

    ws = ROOT / "walkthrough"
    for f in ("terminal_diff.txt", "terminal_run.txt", "terminal_log.txt"):
        if not (ws / f).exists():
            sys.exit("missing %s — capture the demo first" % (ws / f))

    # segments
    parts, t = [], 0.0
    cues = []
    for i, scene in enumerate(SCENES):
        sid, kind, dur, heading, narr = scene
        seg = OUT / "clips" / ("%s.mp4" % sid)
        if kind == "slide":
            video_from_png(slide(scene), dur, seg)
        elif kind == "clip9x16_framed":
            video_from_clip_framed(slide(scene), ROOT / "outputs" / "film_9x16.mp4",
                                   40.0, dur, seg)
        else:
            video_from_clip(ROOT / "outputs" / "film_16x9.mp4", 44.0, dur, seg, "16x9")
        d = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(seg)]).stdout.strip())
        parts.append((seg, d))
        cues.append((t, t + d, narr))
        t += d

    # concat picture
    lst = OUT / "concat.txt"
    # absolute paths: the concat demuxer resolves relative names against nothing useful
    lst.write_text("".join("file '%s'\n" % p.resolve() for p, _ in parts))
    picture = OUT / "picture.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
        "-i", str(lst), "-c", "copy", str(picture)])

    # silent master: a real (silent) stereo track so a voice-over can replace it
    silent = OUT / "walkthrough_silent.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(picture),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(silent)])

    # subtitles (soft) + srt on disk
    srt = OUT / "WALKTHROUGH.srt"
    blocks = []
    for i, (a, b, text) in enumerate(cues, 1):
        blocks.append("%d\n%s --> %s\n%s\n" % (i, srt_ts(a), srt_ts(b), "\n".join(wrap(text))))
    srt.write_text("\n".join(blocks), encoding="utf-8")

    final = OUT / "walkthrough_1080p.mp4"
    sh(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(srt),
        "-map", "0:v", "-map", "0:a", "-map", "1:s", "-c", "copy",
        "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", str(final)])

    total = common_duration(final)
    print("scenes: %d | duration: %.1fs (%.2f min)" % (len(SCENES), total, total / 60))
    if total > 300:
        sys.exit("over the 5-minute limit")
    print("wrote %s  (%.1f MB)" % (final, final.stat().st_size / 1e6))
    write_transcript(cues, total, silent.name)
    print("wrote %s, %s and %s" % (final.name, srt.name, "walkthrough/TRANSCRIPT.md"))


def mmss(t):
    return "%d:%02d" % (int(t) // 60, int(t) % 60)


def write_transcript(cues, total, silent_name):
    """TRANSCRIPT.md: the timed script, and how to record over the silent master."""
    L = []
    L.append("# Walkthrough — transcript and recording sheet")
    L.append("")
    L.append("The video `walkthrough_1080p.mp4` is **silent on purpose**: it is the")
    L.append("picture cut, so a voice can be recorded over it without fighting an")
    L.append("existing narration. This file is the script, timed to the cut, with a")
    L.append("soft English subtitle track already muxed (`WALKTHROUGH.srt`).")
    L.append("")
    L.append("- **Length:** %.1f s (%.2f min) — under the brief's five minutes" % (total, total / 60))
    L.append("- **Picture:** 1920×1080, 30 fps, H.264")
    L.append("- **Audio:** a silent stereo track (48 kHz), ready to be replaced")
    L.append("- **Rebuild it:** `python3 tools/make_walkthrough.py` (needs chromium + ffmpeg)")
    L.append("")
    L.append("## The timed script")
    L.append("")
    L.append("| in | out | on screen | say |")
    L.append("|---|---|---|---|")
    for i, (a, b, text) in enumerate(cues, 1):
        screen = SCENES[i - 1][3].replace("|", "/")
        L.append("| %s | %s | %s | %s |" % (mmss(a), mmss(b), screen, text))
    L.append("")
    L.append("## The words in order")
    L.append("")
    L.append("Read at a normal pace; each block is one scene, and the scene changes on")
    L.append("screen when the block ends. About %d words, roughly %.1f minutes of"
             % (sum(len(t.split()) for _, _, t in cues),
                sum(len(t.split()) for _, _, t in cues) / 150.0))
    L.append("speech at a relaxed 150 words a minute.")
    L.append("")
    for i, (a, b, text) in enumerate(cues, 1):
        L.append("**%s – %s** — %s" % (mmss(a), mmss(b), SCENES[i - 1][3]))
        L.append("")
        for line in wrap(text, 76):
            L.append("> " + line)
        L.append("")
    L.append("## Record it")
    L.append("")
    L.append("Record to a single file, 48 kHz, mono or stereo, WAV. On a phone, a")
    L.append("voice-memo app is fine — export it rather than keeping it in the app.")
    L.append("")
    L.append("```bash")
    L.append("# 1. record (or export) to walkthrough/vo.wav")
    L.append("# 2. replace the silent track and remux, keeping the subtitle stream")
    L.append("ffmpeg -i %s -i vo.wav \\" % silent_name)
    L.append("  -map 0:v -map 1:a -map 0:s -c:v copy -c:a aac -b:a 160k -c:s copy \\")
    L.append("  walkthrough_final.mp4")
    L.append("```")
    L.append("")
    L.append("If your recording runs long or short in one scene, cut or pad that block")
    L.append("rather than speeding the whole track: the picture will not follow a")
    L.append("tempo change.")
    L.append("")
    L.append("## If you would rather not use your own voice")
    L.append("")
    L.append("The brief does not require your voice — it requires that you explain the")
    L.append("architecture, one hard decision, and a live regeneration. A synthetic")
    L.append("voice reading this same script is honest as long as the video says so;")
    L.append("the repository already discloses which models made which asset. What")
    L.append("would not be honest is a walkthrough that claims a demo it does not show.")
    L.append("")
    L.append("## What is on screen, and where it comes from")
    L.append("")
    L.append("| scene | source |")
    L.append("|---|---|")
    L.append("| title, stages, limits, end | HTML slides rendered headlessly from this repository |")
    L.append("| the 9:16 and 16:9 scenes | one still from each film, embedded in the slide |")
    L.append("| the contract | a real excerpt of `storyboard.json` |")
    L.append("| clone, diff, run, log | captured terminal output of the runs described |")
    L.append("| the regenerated image | the actual file those runs produced |")
    L.append("")
    L.append("The video is a slide deck: every scene is a still. No model was called")
    L.append("to make it — the two film stills are frames of the film's own fframes")
    L.append("render, and everything else is text, HTML and FFmpeg.")
    L.append("")
    (OUT / "TRANSCRIPT.md").write_text("\n".join(L), encoding="utf-8")


def common_duration(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=nw=1:nk=1", str(path)]).stdout.strip())


if __name__ == "__main__":
    main()
