"""Stage: script — draft storyboard.json with Gemini (optional), else print guidance.

The storyboard is the human-authored contract, so this stage assists rather than
replaces: it reads story_brief.md (your notes about the story, audience, intent)
and proposes a storyboard that must still validate against the schema and be
reviewed by you before anything is generated.

Usage: python3 -m pipeline.script [story_brief.md]
"""
import json
import shutil
import sys
import time
from pathlib import Path

from pipeline import common, net
from pipeline.jsonschema_lite import validate

PROMPT = """You are drafting a machine-readable storyboard for a 60-90 second
short film about a family story. Return ONLY valid JSON matching this shape:
{{"meta": {{"title", "status":"draft", "narration_language", "aspect_ratios":["9:16","16:9"],
"audience", "intent", "narrator_style", "style_block", "image_width", "image_height"}},
"character_sheet": {{"prompt"}}, "music": {{"caption", "bpm", "key", "instrumental": true, "candidates": 3}},
"end_card": {{"text", "subtitle", "seconds": 2.5}},
"shots": [8 to 12 objects: {{"id", "duration_s" (3-12), "shot_size" (extreme_wide|wide|medium|medium_close|close_up|extreme_close|insert),
"image_prompt", "motion_prompt" (ONLY motion and camera, never re-describe the subject), "narration": {{"lang", "text", "en"}},
"reason" (why this shot exists), "seed", "music_cue"}}]}}
Narration total must be 130-220 words at ~2.3 words/second. Vary shot sizes.
Style block describes look qualities (light, palette, medium), never a living artist.

STORY BRIEF:
{brief}
"""


def draft_with_gemini(brief_text):
    key = common.env_key("GEMINI_API_KEY")
    model = common.env_key("GEMINI_TEXT_MODEL") or "gemini-2.5-flash"
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           "%s:generateContent?key=%s" % (model, key))
    payload = {"contents": [{"parts": [{"text": PROMPT.format(brief=brief_text)}]}],
               "generationConfig": {"responseMimeType": "application/json",
                                    "temperature": 0.8}}
    body, _, ms = net.http_json(url, payload, headers={"x-goog-api-key": key})
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text), model, ms


def main():
    brief_path = Path(sys.argv[1]) if len(sys.argv) > 1 else common.ROOT / "story_brief.md"
    if not brief_path.exists():
        sys.exit("Write your notes in story_brief.md first (story, audience, intent, "
                 "language), then rerun: python3 -m pipeline.script story_brief.md\n"
                 "Or hand-write storyboard.json directly — it is just JSON.")
    brief_text = brief_path.read_text(encoding="utf-8")

    if not (common.has_key("GEMINI_API_KEY") and not common.force_mock()):
        print("No GEMINI_API_KEY — draft storyboard.json by hand against "
              "schema/storyboard.schema.json, then: make validate")
        return

    t0 = time.time()
    sb, model, ms = draft_with_gemini(brief_text)
    errors = validate(sb, json.loads(common.SCHEMA_PATH.read_text()))
    if errors:
        common.log_call(stage="script", model=model, latency_ms=ms, status="error",
                        note="draft failed schema: %s" % errors[0])
        sys.exit("Draft did not validate:\n  - " + "\n  - ".join(errors[:10]))

    backup = common.STORYBOARD_PATH.with_suffix(".backup.json")
    if common.STORYBOARD_PATH.exists():
        shutil.copy(common.STORYBOARD_PATH, backup)
    common.STORYBOARD_PATH.write_text(json.dumps(sb, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    common.log_call(stage="script", model=model, latency_ms=int((time.time() - t0) * 1000),
                    status="ok", output="storyboard.json",
                    params={"brief": brief_path.name, "shots": len(sb["shots"])},
                    note="review and edit before generating!")
    print("storyboard.json drafted (previous copy -> %s). REVIEW IT, then: make validate"
          % backup.name)


if __name__ == "__main__":
    main()
