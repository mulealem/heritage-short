# Experiments

One entry per experiment: hypothesis → change → result. Change ONE thing,
keep the seed fixed, write the result even when it is boring. Ten is a good
target; one well-measured experiment that changed your mind beats five bolted on.

## Template

```
### E1: <question>
- Hypothesis: ...
- Change: (one thing; seed fixed at ...)
- Result: ... (numbers from runs.jsonl where possible)
- Decision: ...
```

## Ready-made experiment candidates

- E: FLUX steps 4 vs 8 — does quality justify 2× latency on keyframes?
- E: fixed seed vs varied seed across 8 keyframes — how much character drift?
- E: Wan 2.2 num_inference_steps 30 vs 50 on the same keyframe — visible gain on T4?
- E: short motion prompt (motion+camera only) vs full re-description — which clips fail?
- E: TTS voice A vs B in your language — which pronounces place names correctly?
- E: sidechaincompress threshold 0.02 vs 0.05 — audibility of pumping under Amharic speech?
- E: Ken Burns variant per shot (zoom-in vs pan) — does varied motion read better in the cut?
- E: same shot, open model vs frontier model — cost, latency, blind preference of 5 people.
