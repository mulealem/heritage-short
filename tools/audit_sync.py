"""Audit: is every asset on disk the one the contract asks for?

Recomputes every cache key from the live contract (storyboard.json,
comic/panels.json, the cast prompts) and compares it with the sidecar stored
next to each asset. An asset is `in sync` when it was generated from exactly
the prompt the contract holds now, `stale` when that prompt changed after it
was made, and `missing` when it does not exist.

This is the repository's self-consistency check: a clone that claims to
rebuild the film from its cache must pass it, or `make short` would quietly
redraw something. Exit status is non-zero if anything is stale or missing.

Usage: python3 tools/audit_sync.py        (also: make check)
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline import common
from pipeline.prompting import directive_for


def load_exporter():
    spec = importlib.util.spec_from_file_location(
        "export_prompts", ROOT / "tools" / "export_prompts.py")
    mod = importlib.util.module_from_spec(spec)
    sys.argv = sys.argv[:1]  # the module only defines main(); do not run it
    spec.loader.exec_module(mod)
    return mod


def main():
    sb = common.load_storyboard()          # validates the contract first
    ex = load_exporter()
    panels = json_load(ROOT / "comic" / "panels.json")["shots"]
    provider = common.image_provider()
    model = common.image_cache_model(provider)
    style = sb["meta"]["style_block"]
    W, H = int(sb["meta"]["image_width"]), int(sb["meta"]["image_height"])
    voice = common.env_key("TTS_VOICE") or "Kore"
    narrator_style = sb["meta"].get("narrator_style", "")

    rows = []   # (kind, name, state)

    # cast portraits
    for actor, desc in ex.load_cast().items():
        rows.append(("cast", actor, ex.status(
            common.hash_key("cast-v2", style, desc),
            common.OUT / "character_refs" / ("%s.jpg" % actor))))

    # keyframes: the cast sheet and one still per shot
    sheet = style + " — " + sb["character_sheet"]["prompt"]
    rows.append(("keyframe", "character_sheet", ex.status(
        ex.key_for_keyframe(provider, None, model, sheet, 0, W, H),
        common.OUT / "keyframes" / "character_sheet.png")))
    for shot in sb["shots"]:
        actor = panels.get(shot["id"], {}).get("actor")
        sent = (style + " — " + shot["image_prompt"]
                + (directive_for(actor) if provider == "minimax" else ""))
        rows.append(("keyframe", shot["id"], ex.status(
            ex.key_for_keyframe(provider, actor, model, sent, shot.get("seed", 0), W, H),
            common.OUT / "keyframes" / ("%s.png" % shot["id"]))))

    # the panels cut into each beat
    for shot in sb["shots"]:
        spec = panels.get(shot["id"], {})
        actor = spec.get("actor")
        for i, extra in enumerate(spec.get("extras", []), 1):
            ref = extra["actor"] if "actor" in extra else actor
            full = ex.compose(style, extra.get("prompt", ""), ref)
            rows.append(("panel", "%s_x%d" % (shot["id"], i), ex.status(
                ex.key_for_panel(provider, ref, full),
                common.OUT / "comic_panels" / ("%s_x%d.jpg" % (shot["id"], i)))))

    # narration lines
    for shot in sb["shots"]:
        wav = common.OUT / "narration" / ("%s.wav" % shot["id"])
        state = ex.narration_state(shot, wav, narrator_style, voice)
        rows.append(("narration", shot["id"], "in sync" if state == "in sync" else state))

    # score
    score = common.OUT / "music" / "score_final.wav"
    src = common.OUT / "music" / "score_source.txt"
    rows.append(("score", "score_final.wav",
                 ("in sync (%s)" % src.read_text().strip()) if score.exists() and src.exists()
                 else ("unrecorded source" if score.exists() else "missing")))

    # report
    bad = 0
    by_kind = {}
    for kind, name, state in rows:
        ok = state.startswith("in sync")
        by_kind.setdefault(kind, [0, 0])[0 if ok else 1] += 1
        if not ok:
            bad += 1
            print("  %-9s %-22s %s" % (kind, name, state.replace("**", "")))
    print("asset audit:")
    for kind, (ok, not_ok) in sorted(by_kind.items()):
        print("  %-10s %2d in sync, %d stale or missing" % (kind, ok, not_ok))
    if bad:
        sys.exit("FAIL: %d asset(s) do not match the contract — run: make short"
                 " (only those are regenerated)" % bad)
    print("PASS: %d of %d assets were made from the contract as it stands"
          % (len(rows), len(rows)))


def json_load(path):
    import json
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
