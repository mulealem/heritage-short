"""Local web editor for the film: edit the contract, regenerate one asset.

Stdlib only. Serves editor/index.html and a small JSON API:

    GET  /api/state                     storyboard, panels, file lists, durations
    POST /api/save                      {storyboard, panels} -> validates + writes
    POST /api/regen/keyframe            {shot_id}         -> one base keyframe
    POST /api/regen/panel               {shot_id, kind, index} -> insert/extra
    POST /api/regen/narration           {shot_id}         -> one TTS line
    POST /api/render                    starts `python3 -m pipeline.short` (both films)
    GET  /api/render/status             running/exit/log tail
    GET  /files/<path>                  outputs/ media (keyframes, panels, wavs, film)

Every regeneration writes the same sidecar the pipeline uses, so `make comic`
reuses the new asset instead of re-calling the model.

Usage: python3 tools/editor_server.py [--host 127.0.0.1] [--port 8765]
Paid API calls happen only when you press a regenerate button.
"""
import argparse
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common
from pipeline.jsonschema_lite import validate

ROOT = common.ROOT
EDITOR = ROOT / "editor"
MEDIA_DIRS = {
    "keyframes": common.OUT / "keyframes",
    "panels": common.OUT / "comic_panels",
    "narration": common.OUT / "narration",
}

from pipeline.prompting import DIRECTIVES, compose, directive_for  # noqa: E402

TOKEN = ""  # set from --token / EDITOR_TOKEN; empty disables auth (localhost only)

RENDER = {"running": False, "exit": None, "log": [], "started": None}
RENDER_LOCK = threading.Lock()


# ---------------------------------------------------------------- model calls

def _panels():
    p = ROOT / "comic" / "panels.json"
    return json.loads(p.read_text()) if p.exists() else {"shots": {}}


def _provider():
    return common.image_provider()


def _ref_for(actor):
    if not actor:
        return None
    ref = common.OUT / "character_refs" / ("%s.jpg" % actor)
    return ref if ref.exists() else None


def _image(prompt, seed):
    """Returns (bytes, model, latency_ms, cost)."""
    provider = _provider()
    if provider == "minimax":
        from pipeline.minimax_image import minimax_image
        data, model, ms = minimax_image(prompt, "9:16")
        cost = common.est_cost("minimax-image-01-per-image", 1)
    else:
        from pipeline.keyframes import cf_flux
        data, model, ms = cf_flux(prompt, 720, 1280, int(seed or 0))
        cost = common.est_cost("flux-klein-4b-per-image", 1)
    return data, model, ms, cost


def _image_with_ref(prompt, ref, seed):
    """Send an already-composed prompt (style + subject + that actor's directive)."""
    provider = _provider()
    if provider == "minimax":
        from pipeline.minimax_image import minimax_image
        data, model, ms = minimax_image(prompt, "9:16", ref_path=ref)
        cost = common.est_cost("minimax-image-01-per-image", 1)
    else:
        from pipeline.keyframes import cf_flux
        data, model, ms = cf_flux(prompt, 720, 1280, int(seed or 0))
        cost = common.est_cost("flux-klein-4b-per-image", 1)
    return data, model, ms, cost


def regen_keyframe(shot_id):
    sb = common.load_storyboard()
    shot = next(s for s in sb["shots"] if s["id"] == shot_id)
    style = sb["meta"]["style_block"]
    spec = _panels()["shots"].get(shot_id, {})
    actor = spec.get("actor")
    ref = _ref_for(actor)
    directive = directive_for(actor) if _provider() == "minimax" else ""
    prompt = style + " — " + shot["image_prompt"] + directive
    t0 = time.time()
    data, model, _ms, cost = _image_with_ref(prompt, ref, shot.get("seed", 0))
    out = common.OUT / "keyframes" / ("%s.png" % shot_id)
    out.write_bytes(data)
    key = common.hash_key(_provider(), actor or "-", common.image_cache_model(_provider()),
                          prompt, 720, 1280, shot.get("seed", 0), "flux-v6")
    (out.with_suffix(".json")).write_text(json.dumps({"key": key}))
    common.log_call(stage="editor", model=model, seed=shot.get("seed"),
                    latency_ms=int((time.time() - t0) * 1000), status="ok",
                    output=str(out), cost_usd_est=cost,
                    params={"shot": shot_id, "kind": "keyframe", "ref": actor})
    return {"ok": True, "url": "/files/keyframes/%s.png" % shot_id,
            "mtime": out.stat().st_mtime, "model": model, "cost": cost}


def regen_panel(shot_id, kind, index=0):
    sb = common.load_storyboard()
    style = sb["meta"]["style_block"]
    spec = _panels()["shots"].get(shot_id, {})
    if kind == "insert":
        prompt = spec.get("insert")
        fname = "%s.jpg" % shot_id
        actor = spec.get("actor")
    else:
        ex = spec.get("extras", [])[int(index)]
        prompt = ex.get("prompt")
        fname = "%s_x%d.jpg" % (shot_id, int(index) + 1)
        actor = ex["actor"] if "actor" in ex else spec.get("actor")
    if not prompt:
        raise RuntimeError("no prompt defined for this panel")
    ref = _ref_for(actor)
    full = compose(style, prompt, actor)
    t0 = time.time()
    data, model, _ms, cost = _image_with_ref(full, ref, 0)
    out = MEDIA_DIRS["panels"] / fname
    out.write_bytes(data)
    key = common.hash_key(_provider(), actor or "-", full, "9:16", "insert-v4")
    out.with_suffix(".json").write_text(json.dumps({"key": key}))
    common.log_call(stage="editor", model=model, latency_ms=int((time.time() - t0) * 1000),
                    status="ok", output=str(out), cost_usd_est=cost,
                    params={"shot": shot_id, "kind": kind, "ref": actor})
    return {"ok": True, "url": "/files/panels/%s" % fname,
            "mtime": out.stat().st_mtime, "model": model, "cost": cost}


def regen_narration(shot_id):
    from pipeline import narration as narr
    sb = common.load_storyboard()
    shot = next(s for s in sb["shots"] if s["id"] == shot_id)
    text = shot["narration"]["text"]
    lang = shot["narration"].get("lang", "am")
    style = sb["meta"].get("narrator_style", "")
    voice = common.env_key("TTS_VOICE") or "Kore"
    t0 = time.time()
    pcm, model = narr.gemini_tts(text, style, voice)
    out = common.OUT / "narration" / ("%s.wav" % shot_id)
    narr.pcm_to_wav(pcm, out)
    trimmed = narr.trim_terminal_burst(out)
    d = common.probe_duration(out)
    key = common.hash_key(text, lang, style, voice,
                          common.env_key("TTS_CACHE_VERSION") or "tts-v2")
    narr.cache_put(out, key, {"seconds": d})
    dur_file = common.OUT / "narration" / "durations.json"
    durs = json.loads(dur_file.read_text()) if dur_file.exists() else {}
    durs[shot_id] = d
    dur_file.write_text(json.dumps(durs, indent=1, sort_keys=True))
    cost = common.est_cost("gemini-tts-per-1k-chars", len(text) / 1000.0)
    common.log_call(stage="editor", model=model, seed=voice,
                    latency_ms=int((time.time() - t0) * 1000), status="ok",
                    output=str(out), cost_usd_est=cost,
                    params={"shot": shot_id, "kind": "narration", "chars": len(text)})
    return {"ok": True, "url": "/files/narration/%s.wav" % shot_id,
            "seconds": d, "model": model, "cost": cost}


# ---------------------------------------------------------------- http layer

def composed_prompt(sb, spec, which, index=0):
    style = sb["meta"]["style_block"]
    if which == "keyframe":
        shot = next(s for s in sb["shots"] if s["id"] == spec["id"])
        return compose(style, shot["image_prompt"], spec.get("actor"))
    elif which == "insert":
        return compose(style, spec.get("insert") or "", spec.get("actor"))
    ex = (spec.get("extras") or [])[int(index)]
    actor = ex["actor"] if "actor" in ex else spec.get("actor")
    return compose(style, ex.get("prompt") or "", actor)


def _narration_state(sb, shot):
    """Whether the WAV on disk was recorded from this exact line."""
    out = common.OUT / "narration" / ("%s.wav" % shot["id"])
    if not out.exists():
        return "missing"
    style = sb["meta"].get("narrator_style", "calm, warm, unhurried")
    voice = common.env_key("TTS_VOICE") or "Kore"
    key = common.hash_key(shot["narration"]["text"],
                          shot["narration"].get("lang", "am"),
                          style, voice,
                          common.env_key("TTS_CACHE_VERSION") or "tts-v2")
    meta = out.with_suffix(".json")
    if not meta.exists():
        return "unverified"
    return "in sync" if json.loads(meta.read_text()).get("key") == key else "stale"


def state():
    sb = common.load_storyboard()
    panels = _panels()
    durs = {}
    df = common.OUT / "narration" / "durations.json"
    if df.exists():
        durs = json.loads(df.read_text())
    keyfiles = sorted(p.name for p in MEDIA_DIRS["keyframes"].glob("*.png"))
    panel_files = sorted(p.name for p in MEDIA_DIRS["panels"].glob("*.jpg"))
    nar_files = sorted(p.name for p in MEDIA_DIRS["narration"].glob("*.wav"))
    shots = []
    for shot in sb["shots"]:
        sid = shot["id"]
        spec = dict(panels["shots"].get(sid, {}))
        spec["id"] = sid
        kf = common.OUT / "keyframes" / ("%s.png" % sid)
        shots.append({
            **shot,
            "panels_spec": spec,
            "keyframe_url": "/files/keyframes/%s.png" % sid if kf.exists() else None,
            "keyframe_mtime": kf.stat().st_mtime if kf.exists() else 0,
            "narration_url": "/files/narration/%s.wav" % sid
            if (common.OUT / "narration" / ("%s.wav" % sid)).exists() else None,
            "narration_seconds": durs.get(sid),
            "narration_state": _narration_state(sb, shot),
            "composed_prompt": composed_prompt(sb, spec, "keyframe"),
        })
    films = []
    for name in ("film_9x16.mp4", "film_16x9.mp4"):
        f = common.OUT / name
        if f.exists():
            films.append({"url": "/files/%s" % name, "mtime": f.stat().st_mtime})
    return {
        "storyboard": sb,
        "panels": panels,
        "shots": shots,
        "files": {"keyframes": keyfiles, "panels": panel_files, "narration": nar_files},
        "films": films,
        "render": dict(RENDER),
        "env": {"provider": _provider(),
                "tts": common.env_key("GEMINI_TTS_MODEL"),
                "voice": common.env_key("TTS_VOICE"),
                "style_block": sb["meta"]["style_block"],
                "directives": DIRECTIVES},
    }


def save(body):
    sb = body.get("storyboard")
    panels = body.get("panels")
    schema = json.loads(common.SCHEMA_PATH.read_text())
    errors = validate(sb, schema)
    if errors:
        return {"ok": False, "errors": errors[:20]}
    if not isinstance(panels, dict) or "shots" not in panels:
        return {"ok": False, "errors": ["panels.json must contain a shots object"]}
    for spec in panels["shots"].values():
        spec.pop("id", None)
    (ROOT / "storyboard.json").write_text(
        json.dumps(sb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "comic" / "panels.json").write_text(
        json.dumps(panels, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True}


def start_render():
    with RENDER_LOCK:
        if RENDER["running"]:
            return {"ok": False, "error": "a render is already running"}
        RENDER.update({"running": True, "exit": None, "log": [],
                       "started": time.strftime("%H:%M:%S")})

    env = dict(os.environ)
    env["PATH"] = str(Path.home() / ".cargo" / "bin") + ":" + env.get("PATH", "")

    def run():
        p = subprocess.Popen([sys.executable, "-m", "pipeline.short"],
                             cwd=str(ROOT), env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            with RENDER_LOCK:
                RENDER["log"].append(line.rstrip())
                RENDER["log"] = RENDER["log"][-200:]
        p.wait()
        with RENDER_LOCK:
            RENDER["running"] = False
            RENDER["exit"] = p.returncode

    threading.Thread(target=run, daemon=True).start()
    return {"ok": True}


class Handler(BaseHTTPRequestHandler):
    server_version = "HeritageEditor/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _gate(self):
        """True when the request may proceed; sets the cookie on a valid ?k="""
        if not TOKEN:
            return True
        q = parse_qs(urlparse(self.path).query)
        cookie = self.headers.get("Cookie") or ""
        got_cookie = "editor_token=" + TOKEN in cookie
        if q.get("k", [""])[0] == TOKEN or got_cookie:
            return True
        self._send(401, {"error": "access token required: reopen the link with ?k=<token>"})
        return False

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, rel):
        rel = unquote(rel)
        if rel.startswith("film_") and rel.endswith(".mp4"):
            path = common.OUT / Path(rel).name
            if not path.exists():
                return self._send(404, {"error": "not found"})
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return self.wfile.write(data)
        parts = rel.split("/", 1)
        if len(parts) != 2:
            return self._send(404, {"error": "bad path"})
        kind, name = parts
        base = MEDIA_DIRS.get(kind)
        if kind == "film_9x16.mp4":
            path = common.OUT / "film_9x16.mp4"
        elif base:
            path = base / Path(name).name
        else:
            return self._send(404, {"error": "unknown media"})
        if not path.exists():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._gate():
            return
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            page = (EDITOR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.send_header("Cache-Control", "no-store")
            if TOKEN:
                self.send_header("Set-Cookie",
                                 "editor_token=%s; Path=/; HttpOnly; SameSite=Lax" % TOKEN)
            self.end_headers()
            return self.wfile.write(page)
        if url.path.startswith("/editor/assets/"):
            asset = EDITOR / "fonts" / Path(url.path[len("/editor/assets/"):]).name
            if not asset.exists():
                return self._send(404, {"error": "not found"})
            data = asset.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "font/ttf")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return self.wfile.write(data)
        if url.path == "/STORY.md":
            st = ROOT / "STORY.md"
            if not st.exists():
                return self._send(404, {"error": "STORY.md missing"})
            return self._send(200, st.read_bytes(), "text/markdown; charset=utf-8")
        if url.path == "/PROMPTS.md":
            md = ROOT / "PROMPTS.md"
            if not md.exists():
                return self._send(404, {"error": "run: make prompts"})
            return self._send(200, md.read_bytes(), "text/markdown; charset=utf-8")
        if url.path == "/api/state":
            try:
                return self._send(200, state())
            except Exception as e:
                return self._send(500, {"error": str(e)})
        if url.path == "/api/render/status":
            with RENDER_LOCK:
                return self._send(200, dict(RENDER))
        if url.path.startswith("/archives/"):
            name = Path(url.path[len("/archives/"):]).name
            arc = ROOT / "archives" / name
            if not arc.exists() or arc.suffix not in (".zip", ".mp4", ".srt", ".wav",
                                                       ".pdf", ".pptx"):
                return self._send(404, {"error": "not found"})
            size = arc.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type",
                             "video/mp4" if arc.suffix == ".mp4" else
                             "application/pdf" if arc.suffix == ".pdf" else
                             "application/vnd.openxmlformats-officedocument."
                             "presentationml.presentation" if arc.suffix == ".pptx" else
                             "application/zip")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition",
                             'attachment; filename="%s"' % name)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with arc.open("rb") as fh:
                shutil.copyfileobj(fh, self.wfile, length=1024 * 256)
            return
        if url.path.startswith("/files/"):
            return self._file(url.path[len("/files/"):])
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self._gate():
            return
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._send(400, {"ok": False, "error": "invalid JSON"})
        try:
            if url.path == "/api/save":
                return self._send(200, save(body))
            if url.path == "/api/regen/keyframe":
                return self._send(200, regen_keyframe(body["shot_id"]))
            if url.path == "/api/regen/panel":
                return self._send(200, regen_panel(body["shot_id"], body.get("kind", "insert"),
                                                   body.get("index", 0)))
            if url.path == "/api/regen/narration":
                return self._send(200, regen_narration(body["shot_id"]))
            if url.path == "/api/render":
                return self._send(200, start_render())
        except Exception as e:
            traceback.print_exc()
            msg = str(e)
            hint = ""
            if "2056" in msg or "usage limit" in msg:
                hint = (" — the image plan's usage cap is reached; wait for the plan "
                        "window or add credits (FAILURES.md F12)")
            elif "429" in msg or "quota" in msg.lower():
                hint = (" — the TTS daily/per-minute quota is reached; wait or use "
                        "paid tier (FAILURES.md F3/F10)")
            return self._send(200, {"ok": False, "error": msg + hint})
        self._send(404, {"ok": False, "error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--token", default=os.environ.get("EDITOR_TOKEN", ""),
                    help="require ?k=<token> / cookie; use for tunnels")
    args = ap.parse_args()
    global TOKEN
    TOKEN = args.token
    if not (EDITOR / "index.html").exists():
        sys.exit("editor/index.html missing")
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print("film editor: http://%s:%d  (Ctrl-C to stop)" % (args.host, args.port))
    if TOKEN:
        print("token gate: on (open the URL with ?k=<token>)")
    if args.host not in ("127.0.0.1", "localhost", "::1"):
        print("! bound to %s — anyone who can reach this port can spend your API "
              "quota; put it behind a tunnel/auth" % args.host)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
