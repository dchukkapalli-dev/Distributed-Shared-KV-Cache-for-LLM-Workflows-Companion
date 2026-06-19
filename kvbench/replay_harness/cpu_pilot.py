#!/usr/bin/env python3
"""KVBench CPU-only pilot trace generator (dependency-free, Python 3 stdlib).

Synthesises a KVBench-conforming trace that emulates the three agentic patterns
discussed in the manuscript (multi-turn tool pauses, multi-agent branching, and
multi-tenant prefix-popularity mixing) WITHOUT a GPU or any model download. Its
sole purpose is to demonstrate that the benchmark contract is *satisfiable* --
that an external group can already produce and check conforming traces today --
not to reproduce any system's production-scale numbers.

The output validates against ../validate_trace.py.

Usage:
    python3 cpu_pilot.py                 # 60 records to stdout (default seed)
    python3 cpu_pilot.py -n 200 --seed 7 > my_trace.jsonl
    python3 cpu_pilot.py | python3 ../validate_trace.py -
"""
import argparse
import json
import random
import sys

GRANULARITIES = ["token", "block", "layer"]
# A plausible per-token KV byte size for a mid-size model at fp16 across a few
# layer/head configurations; the exact value is workload metadata, not a claim.
PER_TOKEN_BYTES = [2048, 4096, 8192, 16384]


# Per-regime knobs on the storage/retention axis. The single-regime pilot was
# flagged in review (R1 M-2) as not exercising the survey's multi-tier
# predictions, so the pilot now spans two regimes in addition to the default
# mix. This is the only axis varied; the trace SCHEMA is identical across
# regimes, so all output validates against the same contract.
#   warm: short tool pauses + concentrated prefix popularity  -> high reuse,
#         the cache-resident regime where loading dominates recompute.
#   cold: long tool pauses + dispersed prefixes               -> low reuse,
#         the eviction-pressure regime where retention policy matters most.
REGIMES = {
    "mixed": {"pause_range": (0.5, 12.0), "prefix_range": (256, 8192)},
    "warm":  {"pause_range": (0.1, 1.5),  "prefix_range": (1024, 8192)},
    "cold":  {"pause_range": (8.0, 45.0), "prefix_range": (128, 2048)},
}


def gen(n, seed, regime="mixed"):
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r}; choose from {sorted(REGIMES)}")
    knobs = REGIMES[regime]
    pause_lo, pause_hi = knobs["pause_range"]
    pre_lo, pre_hi = knobs["prefix_range"]
    rng = random.Random(seed)
    records = []
    t = 0.0
    tenants = [f"tenant_{i}" for i in range(4)]
    # Skewed prefix popularity across tenants (Zipf-ish) for the tenancy axis;
    # the warm regime concentrates it further, the cold regime flattens it.
    if regime == "warm":
        tenant_weights = [0.60, 0.25, 0.10, 0.05]
    elif regime == "cold":
        tenant_weights = [0.30, 0.27, 0.23, 0.20]
    else:
        tenant_weights = [0.45, 0.30, 0.15, 0.10]
    for i in range(n):
        t += rng.expovariate(1.0 / 0.25)        # mean 0.25 s inter-arrival
        tenant = rng.choices(tenants, weights=tenant_weights)[0]
        family = rng.choices(
            ["multi_turn", "multi_agent_branch", "multi_tenant"],
            weights=[0.45, 0.30, 0.25])[0]
        b = rng.choice(PER_TOKEN_BYTES)
        rec = {
            "record_id": f"r{i:05d}",
            "tenant_id": tenant,
            "agent_id": f"{tenant}_a{rng.randint(0, 5)}",
            "workload_family": family,
            "prefix_tokens": rng.randint(pre_lo, pre_hi),
            "per_token_bytes": b,
            "arrival_time_s": round(t, 4),
            "tool_pause_s": 0.0,
            "granularity": rng.choice(GRANULARITIES),
            "consistency_req": "immutable",
        }
        if family == "multi_turn":
            # tool-call pause drives the TTL/retention (consistency) axis
            rec["tool_pause_s"] = round(rng.uniform(pause_lo, pause_hi), 3)
            rec["consistency_req"] = "session"
        elif family == "multi_agent_branch":
            # fork from an earlier emitted record of the same tenant
            siblings = [r for r in records if r["tenant_id"] == tenant]
            parent = rng.choice(siblings) if siblings else None
            rec["parent_id"] = parent["record_id"] if parent else f"r{max(i-1,0):05d}"
            rec["consistency_req"] = rng.choice(["eventual", "immutable"])
        else:  # multi_tenant
            rec["consistency_req"] = rng.choice(["immutable", "strong"])
        records.append(rec)
    return records


def main():
    ap = argparse.ArgumentParser(description="Generate a KVBench-conforming pilot trace.")
    ap.add_argument("-n", "--num", type=int, default=60, help="number of records")
    ap.add_argument("--seed", type=int, default=20260530, help="PRNG seed (deterministic)")
    ap.add_argument("--regime", choices=sorted(REGIMES), default="mixed",
                    help="storage/retention regime: warm (high reuse), "
                         "cold (eviction pressure), or mixed (default)")
    args = ap.parse_args()
    for rec in gen(args.num, args.seed, args.regime):
        sys.stdout.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
