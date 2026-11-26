"""Per-stage latency/cost summary from runs.jsonl (the COSTS.md numbers).

Usage: python3 tools/cost_report.py
"""
import collections
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common


def main():
    rows = [json.loads(l) for l in open(common.RUNS_LOG)]
    by = collections.defaultdict(list)
    cost = collections.Counter()
    for r in rows:
        if r.get("latency_ms"):
            by[(r["stage"], r["model"])].append(r["latency_ms"])
        if r.get("status") == "ok" and r.get("cost_usd_est"):
            cost[(r["stage"], r["model"])] += r["cost_usd_est"]
    print("%-12s %-30s %5s %10s %10s %10s" %
          ("stage", "model", "n", "avg_ms", "max_ms", "est_usd"))
    for (stage, model), v in sorted(by.items()):
        print("%-12s %-30s %5d %10.0f %10d %10.4f" %
              (stage, model, len(v), statistics.mean(v), max(v),
               cost[(stage, model)]))


if __name__ == "__main__":
    main()
