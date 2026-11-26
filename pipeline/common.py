"""Shared helpers: paths, env loading, hashing, ffmpeg wrappers, runs.jsonl logging.

Stdlib only (no pip installs needed). Python 3.8+.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORYBOARD_PATH = ROOT / "storyboard.json"
SCHEMA_PATH = ROOT / "schema" / "storyboard.schema.json"
RUNS_LOG = ROOT / "runs.jsonl"
OUT = ROOT / "outputs"

RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

# Approximate list prices (USD) for the "list-price equivalent" in COSTS.md.
# These are estimates, not quotes; update them when you check current pricing.
# flux-klein-4b-per-image: Workers AI tiles pricing (~3.5 output 512x512 tiles
# at 720x1280, Nov 2026 price sheet) — about $0.0012 per portrait image.
LIST_PRICES = {
    "gemini-tts-per-1k-chars": 0.010,
    "gemini-text-per-1k-chars": 0.001,
    "flux-klein-4b-per-image": 0.0012,
    "cloudflare-flux-2-klein-4b-per-image": 0.0012,
    # nano banana 2K, approximate list price per image (paid tier)
    "gemini-nano-banana-2.1-per-2k-image": 0.03,
    "wan22-per-5s-720p-clip": 0.50,
        "minimax-h3-per-second": 0.08,
    "minimax-image-01-per-image": 0.0035,
"ace-step-per-track": 0.30,
}


def stage_dir(name):
    p = OUT / name
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_env():
    """Parse .env into os.environ without overriding existing values."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()


def env_key(name):
    return os.environ.get(name, "").strip()


def has_key(name):
    return bool(env_key(name))


def require_key(name, setup_hint):
    """Real-only pipeline: a missing key is a hard stop with instructions."""
    if not has_key(name):
        sys.exit("missing %s in .env — %s" % (name, setup_hint))


def log_call(stage, model, params=None, latency_ms=None, status="ok",
             output=None, seed=None, cost_usd_est=None, note=None):
    """Append one line to runs.jsonl — one line per model call (or notable op)."""
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "run_id": RUN_ID,
        "stage": stage,
        "model": model,
        "params": params or {},
        "seed": seed,
        "latency_ms": latency_ms,
        "status": status,
        "output": str(output) if output else None,
        "cost_usd_est": cost_usd_est,
    }
    if note:
        rec["note"] = str(note)[:400]
    with RUNS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    flag = {"ok": "+", "cache": "=", "mock": "m", "error": "!", "skip": "-"}.get(status, "?")
    print("  [%s] %-10s %-28s %s" % (flag, stage, model, note or output or ""))


def hash_key(*objs):
    """Stable cache key from any JSON-able inputs."""
    blob = json.dumps(list(objs), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def image_provider():
    """Which image model draws keyframes and panels (minimax | cloudflare)."""
    return env_key("IMAGE_PROVIDER") or "minimax"


def image_cache_model(provider=None):
    """The model token used in image cache keys.

    Kept in one place: the stage, the editor and the prompt ledger must hash the
    exact same string, or a freshly generated image falsely reads as stale. It
    depends only on the provider, not on unrelated settings, so a clean clone
    with no `.env` still recognises the committed cache.
    """
    provider = provider or image_provider()
    if provider == "minimax":
        return env_key("MINIMAX_IMAGE_MODEL") or "image-01"
    return env_key("CF_FLUX_MODEL") or "flux-2-klein-4b"


def load_storyboard():
    """The contract. Every stage goes through here, so every run validates first."""
    if not STORYBOARD_PATH.exists():
        sys.exit("storyboard.json not found at %s" % STORYBOARD_PATH)
    sb = json.loads(STORYBOARD_PATH.read_text(encoding="utf-8"))
    from pipeline.jsonschema_lite import validate
    errors = validate(sb, json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    if errors:
        sys.exit("storyboard.json does not match %s (%d error%s):\n  %s"
                 % (SCHEMA_PATH.name, len(errors), "" if len(errors) == 1 else "s",
                    "\n  ".join(str(e) for e in errors[:10])))
    return sb


def film_duration(sb):
    return sum(s["duration_s"] for s in sb["shots"])


def find_font():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def _ffmpeg_bin():
    bin_ = shutil.which("ffmpeg")
    if not bin_:
        sys.exit("ffmpeg not found on PATH — install it (sudo apt install ffmpeg)")
    return bin_


def run_ffmpeg(args, stage="assemble", note=None, check=True, cwd=None):
    """Run ffmpeg with quiet logging; log the op to runs.jsonl; return stderr.

    cwd: working directory for the ffmpeg process — pass the stage work dir
    when using stage-relative paths (also sidesteps drawtext/subtitles escaping).
    """
    t0 = time.time()
    cmd = [_ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y"] + [str(a) for a in args]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd) if cwd else None)
    ms = int((time.time() - t0) * 1000)
    status = "ok" if p.returncode == 0 else "error"
    n = note if p.returncode == 0 else (p.stderr or "unknown ffmpeg error")[-380:]
    log_call(stage=stage, model="ffmpeg", params={"args": _short_args(args)},
             latency_ms=ms, status=status, note=n)
    if p.returncode != 0 and check:
        sys.exit("ffmpeg failed:\n%s" % (p.stderr or "")[-1500:])
    return p.stderr


def _short_args(args, limit=8):
    s = " ".join(str(a) for a in args)
    return s[:160] + ("…" if len(s) > 160 else "")


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def image_ext(data):
    """File extension for image bytes: .jpg for JPEG, .png otherwise."""
    return (".jpg", "jpeg") if data[:2] == b"\xff\xd8" else (".png", "png")


def est_cost(kind, units):
    """List-price equivalent, clearly an estimate."""
    return round(LIST_PRICES[kind] * units, 6)
