"""HTTP JSON / multipart helpers with retries + exponential backoff. Stdlib only."""
import json
import time
import urllib.error
import urllib.request
import uuid

RETRYABLE = {429, 500, 502, 503, 504}


def _send(req, retries, timeout):
    """Shared retry loop. Returns (parsed_body, status_code, latency_ms)."""
    last_err = None
    for attempt in range(1, retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                ms = int((time.time() - t0) * 1000)
                try:
                    parsed = json.loads(body)
                except (ValueError, TypeError):
                    parsed = body
                return parsed, r.status, ms
        except urllib.error.HTTPError as e:
            ms = int((time.time() - t0) * 1000)
            body = b""
            try:
                body = e.read()[:600]
            except Exception:
                pass
            last_err = "HTTP %s: %s" % (e.code, body.decode("utf-8", "replace"))
            if e.code in RETRYABLE and attempt < retries:
                time.sleep(min(2 ** attempt, 30))
                continue
            raise RuntimeError(last_err)
        except Exception as e:  # URLError, timeout, etc.
            last_err = "%s: %s" % (type(e).__name__, e)
            if attempt < retries:
                time.sleep(min(2 ** attempt, 30))
                continue
            raise RuntimeError(last_err)
    raise RuntimeError(last_err or "request failed")


def http_json(url, payload=None, headers=None, retries=3, timeout=180):
    """POST (or GET without payload) JSON; returns (parsed_body, status, latency_ms).

    Raises RuntimeError with the last error body after retries are exhausted.
    """
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    hdrs = {"Content-Type": "application/json"}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=hdrs,
                                 method="POST" if data else "GET")
    return _send(req, retries, timeout)


def http_multipart(url, fields, headers=None, retries=3, timeout=180):
    """POST multipart/form-data (string values); returns (parsed_body, status, latency_ms).

    Some Workers AI models (the FLUX-2 family) accept multipart only.
    """
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += ('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                 % (boundary, k, v)).encode("utf-8")
    body += ("--%s--\r\n" % boundary).encode("utf-8")
    hdrs = {"Content-Type": "multipart/form-data; boundary=" + boundary}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    return _send(req, retries, timeout)
