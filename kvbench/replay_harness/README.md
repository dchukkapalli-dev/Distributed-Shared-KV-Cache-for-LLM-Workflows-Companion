# KVBench replay harness — CPU-only pilot

`cpu_pilot.py` synthesises a KVBench-conforming trace that emulates the three
agentic workload families (multi-turn tool pauses, multi-agent branching,
multi-tenant prefix-popularity mixing) **without a GPU or any model download**.

It exists to demonstrate that the benchmark *contract is satisfiable* — that an
external group can already produce and validate conforming traces today. It is
**not** a benchmark execution engine and makes **no** claim to reproduce any
surveyed system's production-scale numbers.

## Requirements

Python 3.8+ standard library only (see `requirements.txt`). No `pip install`
step is needed.

## Usage

```bash
# 60 records to stdout (default deterministic seed, mixed regime)
python3 cpu_pilot.py

# custom size and seed, saved to a file
python3 cpu_pilot.py -n 200 --seed 7 > my_trace.jsonl

# generate and validate in one pipe
python3 cpu_pilot.py | python3 ../validate_trace.py -

# exercise the two storage/retention regimes (see below)
python3 cpu_pilot.py --regime warm | python3 ../validate_trace.py -
python3 cpu_pilot.py --regime cold | python3 ../validate_trace.py -
```

Output is JSON Lines conforming to `../schema/trace_schema.yaml`. Runs in
seconds on a commodity laptop. Generation is deterministic for a fixed
`(--seed, --regime)`.

## Regimes (storage / retention axis)

The pilot spans two regimes in addition to the default mix, so it exercises the
survey's multi-tier retention predictions rather than a single operating point:

| `--regime` | tool pauses | prefix popularity | what it stresses |
|---|---|---|---|
| `warm`  | short (0.1–1.5 s) | concentrated | high-reuse, cache-resident regime where loading dominates recompute |
| `cold`  | long (8–45 s) | dispersed | eviction-pressure regime where retention/TTL policy matters most |
| `mixed` (default) | 0.5–12 s | moderate | a blend of the two |

Only this axis is varied; the trace **schema is identical across regimes**, so
every regime's output validates against the same contract.

## Why synthetic and dependency-free (deliberate design)

`cpu_pilot.py` synthesises a conforming trace rather than instrumenting a real
model, and `requirements.txt` pins nothing. This is intentional, not an
omission: the harness is a *contract-satisfiability demonstrator*, not a
benchmark execution engine, so it must run on any stock Python 3.8+ install with
no GPU, no model download, and no `torch`/`transformers` pin. Driving the schema
from a real model on real hardware — and reporting the full multi-axis metric
set — is named as an open problem in the manuscript's research agenda, not
claimed here.
