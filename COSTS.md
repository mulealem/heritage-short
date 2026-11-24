# Costs: measured latency and list-price equivalents

Fill this FROM `runs.jsonl`, not from memory. Suggested method:

```bash
python3 - <<'EOF'
import json, collections
rows = [json.loads(l) for l in open("runs.jsonl")]
by = collections.defaultdict(list)
for r in rows:
    if r.get("latency_ms"): by[(r["stage"], r["model"])].append(r["latency_ms"])
for k, v in sorted(by.items()):
    print("%-12s %-26s n=%-3d avg=%7.0fms max=%7.0fms" %
          (k[0], k[1], len(v), sum(v)/len(v), max(v)))
EOF
```

## Per-stage measurements

| Stage | Model | n | avg latency | max | GPU minutes | est. cost/run |
|---|---|---|---|---|---|---|
| narration | gemini TTS | TODO | TODO | — | — | TODO |
| keyframes | flux schnell (CF) | TODO | TODO | — | — | TODO |
| shots | wan2.2 (Kaggle T4) | TODO | TODO | TODO | TODO | — (free) |
| music | ace-step 1.5 | TODO | TODO | TODO | TODO | — (free) |
| assemble | ffmpeg (CPU) | TODO | TODO | — | — | — |

Notes:
- List-price equivalents use the `LIST_PRICES` table in `pipeline/common.py`
  and are ESTIMATES — check current prices and update both places together.
- Kaggle GPU time is free but quota-limited (~30 h/week): the honest cost of a
  720p Wan 2.2 shot is wall-clock queue + render time; measure and write it here.
- What we actually found vs what the challenge brief claimed: TODO
  (this line is where "the brief said 50–170 images/day and we measured X" goes).
