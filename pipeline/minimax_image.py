"""MiniMax image-01 provider: one image per prompt, returned as JPEG/PNG bytes.

Used by the keyframes stage when IMAGE_PROVIDER=minimax. Real model only —
the M-plan key is entitled for image-01 (verified live, Nov 2026), unlike
its video models (see FAILURES.md F6).

API: POST https://api.minimax.io/v1/image_generation with a Bearer key;
response carries base64 images under data.image_base64[].
"""
import base64
import json
from pathlib import Path

from pipeline import common, net


def minimax_image(prompt, aspect_ratio="9:16", n=1, ref_path=None):
    """Returns (image_bytes, model, latency_ms). Raises RuntimeError on failure.

    ref_path: optional portrait file. image-01 accepts one subject_reference
    per request (type "character"), which preserves the face across shots.
    """
    key = common.env_key("MINIMAX_API_KEY")
    model = common.env_key("MINIMAX_IMAGE_MODEL") or "image-01"
    url = "https://api.minimax.io/v1/image_generation"
    payload = {"model": model, "prompt": prompt, "aspect_ratio": aspect_ratio,
               "n": n, "response_format": "base64"}
    if ref_path:
        raw = Path(ref_path).read_bytes()
        ext = "png" if raw[:8] == b"\x89PNG\r\n\x1a\n" else "jpeg"
        data_url = "data:image/%s;base64,%s" % (ext, base64.b64encode(raw).decode())
        payload["subject_reference"] = [{"type": "character", "image_file": data_url}]
    body, _, ms = net.http_json(url, payload,
                                headers={"Authorization": "Bearer " + key},
                                timeout=300)
    base = body.get("base_resp", {})
    if base.get("status_code") not in (0, None):
        raise RuntimeError("MiniMax error: %s" % json.dumps(base)[:300])
    images = (body.get("data") or {}).get("image_base64") or []
    if not images:
        raise RuntimeError("no image in response: %s" % json.dumps(body)[:300])
    return base64.b64decode(images[0]), model, ms
