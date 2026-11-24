"""Validate storyboard.json against schema/storyboard.schema.json.

Usage: python3 -m pipeline.validate_sb [path-to-storyboard.json]
"""
import json
import sys
from pathlib import Path

from pipeline import common
from pipeline.jsonschema_lite import validate


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else common.STORYBOARD_PATH
    if not path.exists():
        sys.exit("not found: %s" % path)
    sb = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(common.SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = validate(sb, schema)
    if errors:
        print("INVALID storyboard (%d errors):" % len(errors))
        for e in errors:
            print("  -", e)
        sys.exit(1)
    total = sum(s["duration_s"] for s in sb["shots"])
    words = sum(len(s["narration"]["text"].split()) for s in sb["shots"])
    print("VALID: %s" % path.name)
    print("  shots=%d  planned film=%ds  narration words=%d  language=%s"
          % (len(sb["shots"]), total, words, sb["meta"]["narration_language"]))
    common.log_call(stage="validate", model="jsonschema-lite",
                    params={"file": path.name, "errors": 0}, status="ok",
                    note="storyboard valid")


if __name__ == "__main__":
    main()
