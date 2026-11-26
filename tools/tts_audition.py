"""TTS audition: short Amharic sample per voice/style, for a listening test.

The storyboard narrator style is fixed; this tool tries alternatives so the
next full narration pass is recorded with the right voice, not by trial.

Usage:
    python3 tools/tts_audition.py            # all candidates
    python3 tools/tts_audition.py Kore Puck  # only these voices

Writes outputs/auditions/<voice>__<slug>.wav and logs each call to runs.jsonl.
Costs one TTS request per candidate from the daily quota.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common
from pipeline import narration as narr

OUT = common.OUT / "auditions"

SAMPLE = ("ከበሮ ይመታል፣ ጠጅ ይፈሳል፣ መላው ዳስ ይደንሳል። አለቃ ገብረ ሃና "
          "ከመንገድ በቀጥታ ደረሱ፤ የተቧጨረ ጋቢ፣ ያረጀ ጫማ።")

STYLES = {
    "folk": "a warm Amharic folk storyteller, playful and theatrical",
    "brisk": "a lively, brisk Amharic storyteller, quick and clear",
}


def main():
    wanted = sys.argv[1:] or ["Kore", "Puck", "Charon"]
    OUT.mkdir(parents=True, exist_ok=True)
    common.require_key("GEMINI_API_KEY", "narration key")
    for voice in wanted:
        for slug, style in STYLES.items():
            path = OUT / ("%s__%s.wav" % (voice, slug))
            if path.exists():
                print("  %s: exists" % path.name)
                continue
            pcm, model = narr.gemini_tts(SAMPLE, style, voice)
            narr.pcm_to_wav(pcm, path)
            d = common.probe_duration(path)
            common.log_call(stage="audition", model=model, seed=voice,
                            params={"voice": voice, "style": slug, "lang": "am"},
                            status="ok", output=str(path), note="%.1fs sample" % (d or 0))
            print("  %s: %.1fs" % (path.name, d or 0))
            print("  ... pacing 21s (3 req/min)")
            import time
            time.sleep(21)


if __name__ == "__main__":
    main()
