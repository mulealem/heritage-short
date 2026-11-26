"""Generate the comic cast reference portraits (one per character).

MiniMax image-01 supports one `subject_reference` per request — a front-facing
portrait that preserves identity across later generations. These two files are
that anchor: every shot (and insert) that shows a character is generated with
its portrait attached. Real model only; cached by prompt.

Output: outputs/character_refs/<actor>.jpg
"""
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common

OUT = common.OUT / "character_refs"

CAST = {
    "gebre_hanna": (
        "comic-style character portrait, front view, head and shoulders, "
        "an Ethiopian man in his late fifties with a lean face, salt-and-pepper "
        "beard and kind sharp eyes, wearing a cream turban with a gold band and a "
        "white shamma with gold-and-red tibeb borders over a dark robe, plain warm "
        "grey background"
    ),
    "gatekeeper": (
        "comic-style character portrait, front view, head and shoulders, "
        "a stout proud Ethiopian man of forty with short oiled black hair, "
        "bare-headed with no turban and no hat, a neat short beard, wearing an "
        "ornate dark-teal velvet kabba with gold trim, plain warm grey background"
    ),
}


def main():
    from pipeline.minimax_image import minimax_image
    OUT.mkdir(parents=True, exist_ok=True)
    style = common.load_storyboard()["meta"]["style_block"]
    for actor, desc in CAST.items():
        out = OUT / ("%s.jpg" % actor)
        key = common.hash_key("cast-v2", style, desc)
        side = OUT / ("%s.json" % actor)
        if out.exists() and side.exists() and json.loads(side.read_text()).get("key") == key:
            print("  %s: cache hit" % actor)
            continue
        t0 = time.time()
        data, model, _ = minimax_image(style + " — " + desc, "1:1")
        out.write_bytes(data)
        side.write_text(json.dumps({"key": key}))
        common.log_call(stage="cast", model=model, latency_ms=int((time.time() - t0) * 1000),
                        status="ok", params={"actor": actor}, output=str(out),
                        cost_usd_est=common.est_cost("minimax-image-01-per-image", 1),
                        note="cast reference portrait")
        print("  %s: ok" % actor)


if __name__ == "__main__":
    main()
