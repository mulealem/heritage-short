"""Generate real moving clips with MiniMax Hailuo (I2V) from the shots manifest.

Reads kaggle/manifest_shots.json (written by `make shots`) plus the storyboard
for per-shot durations, submits one image-to-video task per shot — the shot's
keyframe as the first frame and its motion prompt as the prompt — polls until
done, and downloads outputs/shots/<id>.mp4. Needs MINIMAX_API_KEY in .env.

Usage:
    python3 tools/minimax_clips.py            # every missing clip
    python3 tools/minimax_clips.py s1_das ... # only these shots

Resume-safe: clips that already exist are skipped, so a dead run picks up
where it stopped. Clip length = shot duration + 1s margin, clamped to the
API's 4-15s; resolution from MINIMAX_VIDEO_RESOLUTION (default 768P).
"""
import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common

BASE = "https://api.minimax.io"
POLL_S = 15
TIMEOUT_S = 30 * 60
KEY = "MINIMAX_API_KEY"
SETUP = "MiniMax API platform key (platform.minimax.io -> API keys)"


def api(path, payload=None):
    key = common.env_key(KEY)
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main():
    common.require_key(KEY, SETUP)
    sb = common.load_storyboard()
    manifest = json.loads((common.ROOT / "kaggle" / "manifest_shots.json").read_text())
    frames = {s["id"]: s["image"] for s in manifest["shots"]}
    model = common.env_key("MINIMAX_VIDEO_MODEL") or "MiniMax-H3"
    resolution = common.env_key("MINIMAX_VIDEO_RESOLUTION") or "768P"
    durations = {s["id"]: s["duration_s"] for s in sb["shots"]}

    wanted = sys.argv[1:] or [s["id"] for s in sb["shots"]]
    out_dir = common.stage_dir("shots")

    for shot_id in wanted:
        clip = out_dir / ("%s.mp4" % shot_id)
        if clip.exists():
            common.log_call(stage="shots", model=model, params={"shot": shot_id},
                            status="cache", output=str(clip), note="clip present; skipped")
            continue
        frame = common.ROOT / "outputs" / "keyframes" / Path(frames[shot_id]).name
        if not frame.exists():
            sys.exit("missing keyframe %s for %s — run: make keyframes" % (frame, shot_id))
        prompt = next(s["prompt"] for s in manifest["shots"] if s["id"] == shot_id)
        duration = int(max(4, min(15, round(durations[shot_id] + 1))))

        data_uri = "data:image/png;base64," + base64.b64encode(frame.read_bytes()).decode()
        t0 = time.time()
        try:
            resp = api("/v2/video_generation", {
                "model": model,
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}, "role": "first_frame"},
                ],
                "duration": duration,
                "resolution": resolution,
                "generate_audio": False,
            })
        except urllib.error.HTTPError as e:
            body = e.read()[:300].decode("utf-8", "replace")
            common.log_call(stage="shots", model=model, status="error",
                            params={"shot": shot_id, "duration": duration}, note=body)
            hint = ""
            if "2068" in body or "2069" in body or "2056" in body or e.code == 402:
                hint = ("\nthis plan does not include video generation — buy video "
                        "credits on platform.minimax.io (H3 is ~$0.07-0.12/s), or "
                        "use the free Kaggle worker (kaggle/README.md) instead.")
            sys.exit("task submit failed for %s: HTTP %s %s%s"
                     % (shot_id, e.code, body, hint))

        task_id = resp.get("task_id")
        if not task_id:
            common.log_call(stage="shots", model=model, status="error",
                            params={"shot": shot_id}, note=json.dumps(resp)[:300])
            sys.exit("no task_id for %s: %s" % (shot_id, json.dumps(resp)[:200]))
        common.log_call(stage="shots", model=model, seed=None,
                        params={"shot": shot_id, "duration": duration,
                                "resolution": resolution, "task": task_id},
                        status="ok", note="task submitted")

        deadline = time.time() + TIMEOUT_S
        while True:
            time.sleep(POLL_S)
            status = api("/v2/query/video_generation/%s" % task_id)
            st = status.get("status")
            if st == "succeeded":
                url = status["content"]["url"]
                urllib.request.urlretrieve(url, clip)
                ms = int((time.time() - t0) * 1000)
                d = common.probe_duration(clip)
                cost = common.est_cost("minimax-h3-per-second", (d or duration))
                common.log_call(stage="shots", model=model, latency_ms=ms,
                                params={"shot": shot_id, "duration": duration},
                                status="ok", output=str(clip), cost_usd_est=cost,
                                note="clip downloaded (%.1fs)" % (d or 0))
                print("  %s: ok (%.1fs clip)" % (shot_id, d or 0))
                break
            if st in ("failed", "cancelled"):
                common.log_call(stage="shots", model=model, status="error",
                                params={"shot": shot_id, "task": task_id},
                                note=json.dumps(status)[:300])
                sys.exit("task %s for %s: %s" % (task_id, shot_id, json.dumps(status)[:200]))
            if time.time() > deadline:
                sys.exit("timeout waiting for %s (task %s still running — rerun "
                         "later, finished clips are skipped)" % (shot_id, task_id))
            print("  %s: %s..." % (shot_id, st or "pending"))


if __name__ == "__main__":
    main()
