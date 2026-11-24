# Failures: what broke, what was tried, what fixed it

Real blockers only — quota, memory, consistency, language, tooling that moved.
This file is graded: what earns marks is the honest loop of break → try → fix.

## Template

```
### F1: <what broke>
- When/symptom: ...
- What I tried: ...
- Fix or workaround: ...
- Lesson: ...
```

## Known-so-far

- This dev machine has no GPU and a broken `pip3` → the whole pipeline was
  written stdlib-only on purpose; GPU stages run on Kaggle (see kaggle/README.md).
- FFmpeg here is 4.2.7: no `xfade` (hard cuts + fades instead), no `gradients`
  lavfi source (mock keyframes use `color` + drawbox). Version-pinning matters:
  record the exact version any filter assumption depends on.
- TODO: quota walls, OOM on Kaggle T4, character drift across shots, TTS
  mispronouncing place names in your language — as they happen.
