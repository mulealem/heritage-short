PY = python3

.PHONY: film mock validate smoke narration keyframes shots music assemble serve clean

# The one documented command: runs the whole pipeline end to end.
film:
	$(PY) -m pipeline.run_all

# Full pipeline in offline mock mode (no API keys, no GPU): placeholder
# narration, keyframes and score so you can inspect the finished edit shape.
mock:
	FORCE_MOCK=1 $(PY) -m pipeline.run_all

validate:
	$(PY) -m pipeline.validate_sb storyboard.json

smoke:
	$(PY) tools/smoke_test.py

narration:
	$(PY) -m pipeline.narration

keyframes:
	$(PY) -m pipeline.keyframes

shots:
	$(PY) -m pipeline.shots

music:
	$(PY) -m pipeline.music

assemble:
	$(PY) -m pipeline.assemble

# Serve the architecture graph locally: http://127.0.0.1:8123/architecture.html
# Expose it externally with a quick tunnel:
#   cloudflared tunnel --url http://127.0.0.1:8123 --no-autoupdate
serve:
	$(PY) -m http.server 8123 --bind 127.0.0.1 --directory docs

clean:
	rm -rf outputs
