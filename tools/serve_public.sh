#!/usr/bin/env bash
# Serve the film editor through a Cloudflare quick tunnel and print the URL.
# Quick tunnels are ephemeral: the URL changes every run and dies with this script.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f editor.token ]; then TOKEN=$(cat editor.token); else
  TOKEN=$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))' | tee editor.token)
fi

if ! curl -sf -o /dev/null http://127.0.0.1:8765/api/state?k="$TOKEN" 2>/dev/null; then
  echo "starting editor…"
  EDITOR_TOKEN="$TOKEN" nohup python3 tools/editor_server.py --port 8765 \
    > /tmp/editor.log 2>&1 &
  sleep 2
fi

LOG=$(mktemp /tmp/cf-tunnel.XXXX.log)
cloudflared tunnel --url http://127.0.0.1:8765 --no-autoupdate > "$LOG" 2>&1 &
CF=$!
URL=""
for _ in $(seq 1 30); do
  URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG" | head -1 || true)
  [ -n "$URL" ] && break
  sleep 1
done
if [ -z "$URL" ]; then echo "tunnel failed; see $LOG"; exit 1; fi

echo
echo "  Editor:  $URL/?k=$TOKEN"
echo "  Token:   $TOKEN"
echo
echo "  Ctrl-C stops the tunnel (the local editor keeps running)."
exec tail -f "$LOG" >/dev/null & wait "$CF"
