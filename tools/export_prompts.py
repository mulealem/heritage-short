"""Export every prompt and line of the film to one markdown document.

Reads the live contract (storyboard.json, comic/panels.json, comic/film.json,
kaggle/manifest_music.json), the cast prompts, and the cache sidecars, and
writes PROMPTS.md:

  - the story and its narration (Amharic + English)
  - the style block and the identity directive
  - per shot: reason, timings, seed, reference, camera move, balloons/SFX
  - the exact composed prompt sent to the image model for the keyframe and for
    every panel cut, plus whether the image on disk was generated from that
    exact prompt (in sync) or predates it (stale)

Usage: python3 tools/export_prompts.py [out.md]
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common
from pipeline.prompting import DIRECTIVES, compose, directive_for

ROOT = common.ROOT
OUT_DEFAULT = ROOT / "PROMPTS.md"


def load_cast():
    spec = importlib.util.spec_from_file_location("comic_cast", ROOT / "tools" / "comic_cast.py")
    mod = importlib.util.module_from_spec(spec)
    sys.argv = sys.argv[:1]  # module only defines main(); do not run it
    spec.loader.exec_module(mod)
    return mod.CAST


def key_for_keyframe(provider, actor, model, full, seed, W, H):
    return common.hash_key(provider, actor or "-", model, full, W, H, seed, "flux-v6")


def key_for_panel(provider, actor, full):
    return common.hash_key(provider, actor or "-", full, "9:16", "insert-v4")


def sidecar_key(path):
    meta = path.with_suffix(".json")
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text()).get("key")
    except ValueError:
        return None


def status(expected, path):
    if not path.exists():
        return "**missing**"
    got = sidecar_key(path)
    if got is None:
        return "**unverified** — no cache sidecar (image predates prompt tracking); regenerate to lock it"
    return "in sync" if got == expected else "**stale** (prompt changed since generation)"


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def fence(text):
    return "```text\n" + text.strip() + "\n```"


def narration_state(shot, wav, style, voice):
    """Whether the WAV on disk was recorded from this exact line."""
    if not wav.exists():
        return "missing — run `make narration`"
    key = common.hash_key(shot["narration"]["text"],
                          shot["narration"].get("lang", "am"),
                          style, voice,
                          common.env_key("TTS_CACHE_VERSION") or "tts-v2")
    meta = wav.with_suffix(".json")
    if not meta.exists():
        return "**unverified** — no cache sidecar"
    return ("in sync" if json.loads(meta.read_text()).get("key") == key
            else "**stale audio** — the line changed; run `make narration`")


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT_DEFAULT
    sb = common.load_storyboard()
    panels = json.loads((ROOT / "comic" / "panels.json").read_text())
    film = json.loads((ROOT / "comic" / "film.json").read_text()) \
        if (ROOT / "comic" / "film.json").exists() else None
    music = json.loads((ROOT / "kaggle" / "manifest_music.json").read_text()) \
        if (ROOT / "kaggle" / "manifest_music.json").exists() else None
    durs = {}
    df = common.OUT / "narration" / "durations.json"
    if df.exists():
        durs = json.loads(df.read_text())

    provider = common.env_key("IMAGE_PROVIDER") or "minimax"
    image_model = (common.env_key("MINIMAX_IMAGE_MODEL") or "image-01") \
        if provider == "minimax" else (common.env_key("CF_FLUX_MODEL") or "flux-2-klein-4b")
    cache_model = common.image_cache_model(provider)
    tts_model = common.env_key("GEMINI_TTS_MODEL") or "?"
    voice = common.env_key("TTS_VOICE") or "Kore"
    style = sb["meta"]["style_block"]
    cast = load_cast()
    film_by_id = {s["id"]: s for s in (film or {}).get("shots", [])}

    L = []
    L.append("# %s — every prompt, every line" % sb["meta"]["title"])
    L.append("")
    L.append("> Generated from the live contract by `tools/export_prompts.py`; "
             "do not hand-edit. Regenerate with `make prompts`.")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append("| Title | **%s** (%s) |" % (sb["meta"]["title"], sb["meta"].get("title_local", "")))
    L.append("| Format | %s, 24 fps, 1080×1920 and 1920×1080 (comic renderer) |"
             % " and ".join(sb["meta"]["aspect_ratios"]))
    planned = sum(float(s["duration_s"]) for s in sb["shots"])
    rendered = []
    for r in sb["meta"]["aspect_ratios"]:
        f = common.OUT / ("film_%s.mp4" % r.replace(":", "x"))
        if f.exists():
            rendered.append("%s: %.1f s" % (r, common.probe_duration(f) or 0))
    L.append("| Film duration | %s · %.1f s of beats + %.1f s end card |"
             % (" · ".join(rendered) or "not rendered", planned,
                float(sb["end_card"].get("seconds", 3.0))))
    L.append("| Narration language | %s (English subtitle track + captions) |"
             % sb["meta"]["narration_language"])
    L.append("| Image model | `%s` (%s), one `subject_reference` portrait per character shot |"
             % (image_model, provider))
    L.append("| TTS | `%s`, voice `%s` |" % (tts_model, voice))
    L.append("| Music | ACE-Step 1.5 on Kaggle (manifest below) |")
    L.append("")

    L.append("## The story being told")
    L.append("")
    L.append("Aleqa Gebre Hanna, a wise elder scholar, walks to a neighbour's wedding "
             "feast in his dusty travelling gabi. Guests whisper as he approaches, and "
             "the gatekeeper turns him away at the crowded gate as unfit for honorable "
             "guests. He goes home, washes, dresses in his snow-white tibeb-bordered "
             "shamma and gold-trimmed velvet kabba, and returns — to bows from the "
             "gatekeeper, ililta ululations from bystanders, and a warm embrace from the "
             "host who leads him to the seat of honor. When servers set an enormous feast "
             "before him, the entire das falls silent. Gebre Hanna scoops red doro wot "
             "over his own white shamma, tucks meat in his sleeve, and pours golden tej "
             "down his velvet cloak as the host lunges to stop him and guests recoil. "
             "\"Eat, my clothes, eat!\" he says directly to the host and gatekeeper. \"I "
             "came as myself and you turned me away; my clothes came and you gave them "
             "the seat of honor. You invited my clothes — not me!\" The whole tent erupts "
             "in laughter. Proverb: judge a person by their character, not their cloth.")
    L.append("")

    L.append("## Style block (prepended to every image prompt)")
    L.append("")
    L.append(fence(style))
    L.append("")
    L.append("## Identity directives (character-specific; appended only with that portrait)")
    L.append("")
    for actor, directive in DIRECTIVES.items():
        L.append("### `%s`" % actor)
        L.append("")
        L.append(fence(directive))
        L.append("")
    L.append("> **Rule:** a directive is attached only when that named character's "
             "portrait is used. Never attach a `subject_reference` to prop close-ups, "
             "food inserts or large crowd shots — the model would clone the lead's face "
             "onto bystanders. Every beat must show the environment, multi-character "
             "interaction and reaction in context.")
    L.append("")

    L.append("## Cast reference portraits")
    L.append("")
    for actor, desc in cast.items():
        ref = common.OUT / "character_refs" / ("%s.jpg" % actor)
        prompt = compose(style, desc, has_reference=False)
        expected = common.hash_key("cast-v2", style, desc)
        L.append("### `%s` — %s" % (actor, ref.name if ref.exists() else "(not generated)"))
        L.append("")
        L.append("- File: `%s`" % rel(ref))
        L.append("- Status vs this prompt: %s"
                 % ("in sync" if sidecar_key(ref) == expected
                    else "**stale** — regenerate with `make cast`"))
        L.append("")
        L.append(fence(prompt))
        L.append("")
        L.append("Attached as `subject_reference` to every shot whose panel spec names "
                 "this actor.")
        L.append("")

    L.append("## Narration (spoken Amharic / English subtitles)")
    L.append("")
    L.append("| # | Shot | Spoken (Amharic) | Subtitle (English) | Audio |")
    L.append("|---|---|---|---|---|")
    for i, shot in enumerate(sb["shots"], 1):
        n = shot["narration"]
        audio = common.OUT / "narration" / ("%s.wav" % shot["id"])
        state = narration_state(shot, audio, sb["meta"].get("narrator_style", ""), voice)
        L.append("| %d | `%s` | %s | %s | %s |"
                 % (i, shot["id"], n["text"].replace("|", "\\|"),
                    (n.get("en") or "").replace("|", "\\|"),
                    ("%.2fs — %s" % (durs.get(shot["id"], 0), state))
                    if audio.exists() else state))
    L.append("")
    L.append("TTS is called with the spoken text only — the style phrase is **not** sent "
             "(it used to be read aloud; see FAILURES.md F11). Voice and model above; "
             "`TTS_STYLE_PREFIX` is empty.")
    L.append("")

    L.append("## Shot by shot")
    L.append("")
    for i, shot in enumerate(sb["shots"], 1):
        sid = shot["id"]
        spec = panels["shots"].get(sid, {})
        fshot = film_by_id.get(sid, {})
        kf = common.OUT / "keyframes" / ("%s.png" % sid)
        actor = spec.get("actor")
        kf_prompt = compose(style, shot["image_prompt"], actor)
        # exactly what the stage sends and hashes: the directive rides along
        # only when a reference portrait is attached (MiniMax path)
        sent = (style + " — " + shot["image_prompt"]
                + (directive_for(actor) if provider == "minimax" else ""))
        expected = key_for_keyframe(provider, actor, cache_model, sent,
                                    shot.get("seed", 0),
                                    int(sb["meta"]["image_width"]), int(sb["meta"]["image_height"]))

        L.append("### %d. `%s` — %s" % (i, sid, shot.get("framing") or shot["shot_size"]))
        L.append("")
        L.append("| | |")
        L.append("|---|---|")
        L.append("| Planned duration | %s s |" % shot["duration_s"])
        wav = common.OUT / "narration" / ("%s.wav" % sid)
        L.append("| Narration audio | %s |"
                 % (("%.2fs — %s" % (durs[sid], narration_state(
                        shot, wav, sb["meta"].get("narrator_style", ""), voice)))
                    if sid in durs else "missing"))
        L.append("| Seed | %s |" % shot.get("seed"))
        L.append("| Camera move | %s |" % fshot.get("mv", "—"))
        L.append("| Reference | %s |" % ("`%s` portrait" % actor if actor else "none"))
        L.append("| Keyframe file | `%s` |" % rel(kf))
        L.append("| Status | %s |" % status(expected, kf))
        L.append("")
        L.append("**Why this shot exists:** %s" % shot["reason"])
        L.append("")
        L.append("**Narration (Amharic):** %s" % shot["narration"]["text"])
        L.append("")
        L.append("**Subtitle (English):** %s" % (shot["narration"].get("en") or ""))
        L.append("")
        L.append("**Keyframe — storyboard prompt:**")
        L.append("")
        L.append(fence(shot["image_prompt"]))
        L.append("")
        L.append("**Keyframe — exact prompt sent to `%s`:**" % image_model)
        L.append("")
        L.append(fence(kf_prompt))
        L.append("")
        if shot.get("motion_prompt"):
            L.append("**Motion prompt (video route only):** %s" % shot["motion_prompt"])
            L.append("")

        balloon = spec.get("balloon")
        sfx = spec.get("sfx") or []
        if isinstance(sfx, dict):
            sfx = [sfx]
        if balloon or sfx:
            L.append("**Comic overlays:** " + "; ".join(filter(None, [
                "balloon \"%s\" from %.1fs to %.1fs" % (balloon["text"], balloon["start"], balloon["end"])
                if balloon else "",
            ] + ["SFX \"%s\" at %.1fs" % (s["text"], s["t"]) for s in sfx])))
            L.append("")

        # Planned cuts come from panels.json so the ledger lists every prompt
        # even when the image has not been generated yet. film.json only
        # supplies the camera move of the last render.
        cuts = [{"img": "panel_%s.png" % sid, "at": float(spec.get("base_at", 0.0))}]
        if spec.get("insert"):
            cuts.append({"img": "ins_%s.jpg" % sid, "at": 0.55})
        for j, ex in enumerate(spec.get("extras", []), 1):
            cuts.append({"img": "ins_%s_x%d.jpg" % (sid, j),
                         "at": float(ex.get("at", 0.5))})
        cuts.sort(key=lambda c: c["at"])
        L.append("**Cuts in this beat (%d):**" % len(cuts))
        L.append("")
        for j, cut in enumerate(cuts, 1):
            img, at = cut["img"], cut["at"]
            label, prompt_body, ref_tag, src, extra = "", "", None, None, ""
            if img == "panel_%s.png" % sid:
                label = "base keyframe"
                prompt_body = shot["image_prompt"]
                ref_tag = actor
                src = kf
            elif img.startswith("re_"):
                n = int(img[len("re_"):].rsplit("_", 1)[1].split(".")[0]) - 1
                reuse = spec.get("reuse", [])
                source = reuse[n]["img"] if n < len(reuse) else "?"
                label = "reused panel"
                prompt_body = "(editorial reuse of the existing panel %s)" % source
                src = common.OUT / "comic_panels" / source
                extra = " — source: `%s`" % source
            elif img.startswith("ins_"):
                name = img[len("ins_"):]
                if name.startswith(sid + "_x"):
                    idx = int(name.split("_x")[1].split(".")[0]) - 1
                    ex = spec.get("extras", [])[idx]
                    prompt_body = ex.get("prompt", "")
                    ref_tag = ex["actor"] if "actor" in ex else actor
                    label = ex.get("role") or ("extra %d" % (idx + 1))
                    src = common.OUT / "comic_panels" / name
                else:
                    prompt_body = spec.get("insert") or ""
                    ref_tag = actor
                    label = "insert"
                    src = common.OUT / "comic_panels" / ("%s.jpg" % sid)
            else:
                label = "unknown cut"

            L.append("%d. **%s** — %d%% into the beat → `%s`%s"
                     % (j, label, round(at * 100), img, extra))
            L.append("")
            if prompt_body:
                composed = compose(style, prompt_body, ref_tag)
                if src is not None:
                    if img.startswith("re_"):
                        state = ("reused — source exists (no generation for this cut)"
                                 if src.exists() else "**missing**")
                    else:
                        if img == "panel_%s.png" % sid:
                            exp = key_for_keyframe(provider, ref_tag, cache_model,
                                                   composed, shot.get("seed", 0),
                                                   int(sb["meta"]["image_width"]),
                                                   int(sb["meta"]["image_height"]))
                        else:
                            exp = key_for_panel(provider, ref_tag, composed)
                        state = status(exp, src)
                    L.append("Status: %s" % state)
                    L.append("")
                L.append(fence(composed))
                L.append("")
            else:
                L.append("_(no prompt recorded for this cut)_")
                L.append("")
        L.append("---")
        L.append("")

    end = sb["end_card"]
    L.append("## End card")
    L.append("")
    L.append("- Title: **%s** (%s)" % (sb["meta"]["title"], sb["meta"].get("title_local", "")))
    if end.get("text_am"):
        L.append("- Proverb (Amharic): %s" % end["text_am"])
    L.append("- Proverb (English): %s" % end["text"])
    L.append("- Subtitle: %s" % end.get("subtitle", ""))
    L.append("- Duration: %.1f s" % float(end.get("seconds", 3.0)))
    L.append("")

    if music:
        L.append("## Music prompt (ACE-Step 1.5, Kaggle)")
        L.append("")
        L.append("| Field | Value |")
        L.append("|---|---|")
        mus = sb["music"]
        L.append("| Caption | %s |" % mus["caption"].replace("|", "\\|"))
        L.append("| BPM | %s |" % mus.get("bpm"))
        L.append("| Key | %s |" % mus.get("key"))
        L.append("| Instrumental | %s |" % mus.get("instrumental"))
        L.append("| Candidates | %s |" % mus.get("candidates", 3))
        L.append("| Seeds | %s |"
                 % [int(mus.get("seed", 42)) + i for i in range(mus.get("candidates", 3))])
        L.append("| Lyrics | %s |" % (mus.get("lyrics") or "(none)"))
        L.append("")
        fdur = (film or {}).get("duration", 0)
        mdur = float(music.get("seconds") or 0)
        L.append("This prompt is the storyboard's `music` block. The Kaggle manifest "
                 "(`kaggle/manifest_music.json`) is regenerated by `make music`.")
        score_src = common.OUT / "music" / "score_source.txt"
        if score_src.exists():
            L.append("")
            L.append("**Score on disk:** `%s` — a deterministic, hand-synthesized "
                     "qenet bed (`tools/make_qenet_bed.py`), mixed at −24 LUFS and "
                     "ducked under the voice. The ACE-Step prompt above remains the "
                     "upgrade path; replace `score_final.wav` and re-render to use it."
                     % score_src.read_text().strip())
        if fdur and abs(fdur - mdur) > 3:
            L.append("")
            L.append("**Stale manifest on disk:** sized to %.1f s, current cut is %.1f s — "
                     "run `make music` before submitting the notebook."
                     % (mdur, fdur))
        L.append("")

    L.append("## How these were produced")
    L.append("")
    L.append("- Images: `python3 -m pipeline.keyframes` (keyframes) and "
             "`python3 tools/comic_panels.py` (inserts/extras); every call is logged in "
             "`runs.jsonl` with model, latency and estimated cost.")
    L.append("- Cast anchors: `python3 tools/comic_cast.py`.")
    L.append("- Narration: `make narration` (Gemini TTS, paced to the free-tier "
             "3 requests/minute; cached per line).")
    L.append("- Edit and regenerate single assets: `make editor` "
             "(or `bash tools/serve_public.sh` for a tunnel).")
    L.append("- Regenerate this document: `make prompts`.")
    L.append("")
    L.append("**Status honesty:** `in sync` means the file on disk was generated from "
             "*this exact prompt* (cache sidecar matches). `stale` means the prompt has "
             "been edited since that image was drawn — press Regenerate for that asset "
             "when the image quota allows (see FAILURES.md F12).")
    L.append("")

    out_path.write_text("\n".join(L), encoding="utf-8")
    print("wrote %s (%d lines, %d KB)" % (out_path, len(L), out_path.stat().st_size // 1024))


if __name__ == "__main__":
    main()
