PY = python3

.PHONY: help check short film comic cast panels score editor prompts verify preflight validate narration keyframes shots music assemble serve clean

# Self-consistency: the contract validates, every committed asset was made
# from the contract as it stands (tools/audit_sync.py), and both finished
# films meet the brief (tools/verify_film.py). Non-zero if anything is off.
check:
	$(PY) -m pipeline.validate_sb storyboard.json
	$(PY) tools/audit_sync.py
	$(PY) tools/verify_film.py outputs/film_9x16.mp4 outputs/film_16x9.mp4

# Every target, with one line each.
help:
	@echo "make check      schema + every asset in sync with the contract + both films vs the brief"
	@echo "make short      THE ONE COMMAND: storyboard.json -> film_9x16.mp4 + film_16x9.mp4"
	@echo "make verify     check both films against the brief (streams, resolution, 60-90 s, subtitles)"
	@echo "make validate   validate storyboard.json against the schema"
	@echo "make editor     local web editor: edit any field, regenerate one asset, render"
	@echo "make prompts    regenerate PROMPTS.md (every prompt + sync status)"
	@echo "make preflight  one real call per provider (run after changing keys)"
	@echo "make cast | panels | keyframes | narration   one stage on its own"
	@echo "make score      keep a chosen score, or build the qenet bed"
	@echo "make music      music-model route: needs a chosen score (ACE-Step, see kaggle/README.md)"
	@echo "make comic      build + render the 9:16 film only"
	@echo "make film       video-clip route (Wan 2.2 on Kaggle) - not the submitted film"
	@echo "make serve      docs/ on http://127.0.0.1:8123 (architecture.html)"
	@echo "make clean      remove render intermediates (cached model outputs stay)"

# THE ONE COMMAND: storyboard.json -> outputs/film_9x16.mp4 + outputs/film_16x9.mp4
#   validate, narration, cast, keyframes, panels, comic build, score, render 9:16, render 16:9
# Every stage validates the contract, works from the content-hash cache and
# stops with instructions if something it needs is missing. A clone that keeps
# outputs/ needs no API keys: keys are only asked for on a real cache miss.
short:
	$(PY) -m pipeline.short

# The video-clip route (Wan 2.2 on Kaggle -> real moving shots): stops at
# `shots` until the Kaggle clips are in outputs/shots/. The submitted film was
# made with `make short` (motion comic), not this target.
film:
	$(PY) -m pipeline.run_all

# Motion-comic render (fframes, CPU): panels + balloons + kinetic captions.
# Written by pipeline/comic.py; ~5 min CPU for the whole film.
comic:
	$(PY) -m pipeline.comic all

# Comic art: cast reference portraits, then extra insert panels.
cast:
	$(PY) tools/comic_cast.py

panels:
	$(PY) tools/comic_panels.py

# Local web editor: edit prompts/narration, regenerate one asset, render.
# Binds 127.0.0.1:8765 — put a tunnel in front if you need remote access.
editor:
	$(PY) tools/editor_server.py --host 127.0.0.1 --port 8765

# Export every prompt + line of the film to PROMPTS.md.
prompts:
	$(PY) tools/export_prompts.py

# Check the finished films: streams, specs, 60-90 s, loudness, subtitles.
verify:
	$(PY) tools/verify_film.py outputs/film_9x16.mp4 outputs/film_16x9.mp4

# Real one-call check per provider (Gemini text, Gemini TTS, CF FLUX).
# Run this first whenever .env changes.
preflight:
	$(PY) tools/smoke_test.py

validate:
	$(PY) -m pipeline.validate_sb storyboard.json

narration:
	$(PY) -m pipeline.narration

keyframes:
	$(PY) -m pipeline.keyframes

shots:
	$(PY) -m pipeline.shots

# Music-model route: needs a chosen score (an ACE-Step candidate copied to
# outputs/music/score_final.wav) and refuses to guess between candidates.
music:
	$(PY) -m pipeline.music

# The score slot as the one command uses it: keep a chosen score, otherwise
# build the deterministic qenet bed; then log it and refresh the manifest.
score:
	$(PY) -m pipeline.score

assemble:
	$(PY) -m pipeline.assemble

# Serve the architecture graph locally: http://127.0.0.1:8123/architecture.html
# Expose it externally with a quick tunnel:
#   cloudflared tunnel --url http://127.0.0.1:8123 --no-autoupdate
serve:
	$(PY) -m http.server 8123 --bind 127.0.0.1 --directory docs

# Remove what is rebuilt on every run (render intermediates and the media
# copies). The cached model outputs in outputs/ stay: they are the evidence.
clean:
	rm -rf outputs/comic comic/media/panel_* comic/media/ins_* comic/media/re_* comic/film.json
