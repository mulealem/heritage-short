"""Smoke test: one real call per configured provider, latency logged to runs.jsonl.

Run before anything else on a new machine or after any key change:
    python3 tools/smoke_test.py

Checks connectivity, key validity, and model names early — the failure journal
(FAILURES.md) should start with whatever breaks here.
"""
import base64
import sys
import time

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from pipeline import common, net  # noqa: E402


def check_gemini_text():
    key = common.env_key("GEMINI_API_KEY")
    model = common.env_key("GEMINI_TEXT_MODEL") or "gemini-2.5-flash"
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "%s:generateContent?key=%s" % (model, key))
    body, status, ms = net.http_json(
        url, {"contents": [{"parts": [{"text": "Reply with the single word: ok"}]}]},
        headers={"x-goog-api-key": key})
    text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
    common.log_call(stage="smoke", model=model, latency_ms=ms,
                    params={"kind": "text"}, status="ok", note=text[:40])
    print("gemini text   : OK   (%d ms) -> %s" % (ms, text[:40]))


def check_gemini_tts():
    key = common.env_key("GEMINI_API_KEY")
    model = common.env_key("GEMINI_TTS_MODEL") or "gemini-2.5-flash-preview-tts"
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "%s:generateContent?key=%s" % (model, key))
    body, status, ms = net.http_json(url, {
        "contents": [{"parts": [{"text": "calm, warm: Hello."}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Kore"}}}},
    }, headers={"x-goog-api-key": key})
    audio = body["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    n = len(base64.b64decode(audio))
    common.log_call(stage="smoke", model=model, latency_ms=ms,
                    params={"kind": "tts", "bytes": n}, status="ok")
    print("gemini tts    : OK   (%d ms, %d bytes of PCM)" % (ms, n))


def check_cloudflare_flux():
    acct = common.env_key("CF_ACCOUNT_ID")
    token = common.env_key("CF_API_TOKEN")
    model = common.env_key("CF_FLUX_MODEL") or "@cf/black-forest-labs/flux-schnell"
    url = "https://api.cloudflare.com/client/v4/accounts/%s/ai/run/%s" % (acct, model)
    body, status, ms = net.http_json(url, {"prompt": "a red apple on a wooden table",
                                           "steps": 4, "width": 512, "height": 512},
                                     headers={"Authorization": "Bearer " + token},
                                     timeout=300)
    img = body.get("result", {}).get("image")
    if not img:
        raise RuntimeError("no image: %s" % str(body)[:200])
    n = len(base64.b64decode(img))
    common.log_call(stage="smoke", model=model, latency_ms=ms,
                    params={"kind": "image", "bytes": n}, status="ok")
    print("cloudflare flux: OK  (%d ms, %d bytes png)" % (ms, n))


CHECKS = {
    "gemini_text": (lambda: common.has_key("GEMINI_API_KEY"), check_gemini_text),
    "gemini_tts": (lambda: common.has_key("GEMINI_API_KEY"), check_gemini_tts),
    "cloudflare_flux": (lambda: common.has_key("CF_ACCOUNT_ID") and common.has_key("CF_API_TOKEN"),
                        check_cloudflare_flux),
}


def main():
    print("smoke test — one call per configured provider\n")
    results = {}
    for name, (configured, fn) in CHECKS.items():
        if not configured():
            results[name] = "skipped (no key)"
            print("%-16s: SKIP  (key missing — add it to .env)" % name)
            continue
        try:
            fn()
            results[name] = "ok"
        except Exception as e:
            results[name] = "FAILED: %s" % str(e)[:160]
            common.log_call(stage="smoke", model=name, status="error", note=str(e)[:200])
            print("%-16s: FAIL  %s" % (name, str(e)[:160]))
    bad = [k for k, v in results.items() if "FAIL" in str(v)]
    print("\n%d ok, %d failed, rest skipped" % (len(results) - len(bad) - sum(1 for v in results.values() if "SKIP" in v), len(bad)))
    print("note: kaggle (wan2.2 video, ace-step music) has no API smoke test — "
          "verify by running kaggle/README.md steps once")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
