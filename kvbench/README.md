# KVBench — a reproducible benchmark contract for distributed shared KV-cache systems

KVBench is the **contract** proposed in the manuscript's benchmark section. It is
deliberately a *contract validator*, not a benchmark execution engine: the
headline metrics reported by the surveyed systems were measured under different
models, prompts, KV-object sizes, and hardware, so they cannot be compared.
KVBench fixes a common trace schema and a common multi-axis metric set so that
independently produced results become comparable, and ships a runnable validator
plus a CPU-only pilot so a reviewer can check that the contract is satisfiable
today.

## Contents

```
kvbench/
  README.md                     this file
  validate_trace.py             dependency-free trace-conformance validator
  schema/
    trace_schema.yaml           machine-readable trace schema (source of truth)
    example_trace.jsonl         12-record example covering all three families
  replay_harness/
    cpu_pilot.py                CPU-only conforming-trace generator
    requirements.txt            (empty — stdlib only)
    README.md                   harness usage
```

## Quick start

```bash
# 1. validate the shipped example trace
python3 validate_trace.py schema/example_trace.jsonl

# 2. generate a fresh conforming trace and validate it
python3 replay_harness/cpu_pilot.py | python3 validate_trace.py -
```

Both commands print `PASS` and exit 0 on a stock Python 3.8+ install.

## The trace schema

Each line of a trace is one request annotated with: `record_id`, `tenant_id`,
`agent_id`, optional `parent_id` (for branching), `workload_family`
(`multi_turn` / `multi_agent_branch` / `multi_tenant`), `prefix_tokens` (the *L*
of the placement model), `per_token_bytes` (*b*), `arrival_time_s`,
`tool_pause_s`, `granularity` (*g*), and `consistency_req` (*chi*). A conforming
trace must exercise at least two of the three workload families. See
`schema/trace_schema.yaml` for the full field-by-field contract and the
required-metrics-by-axis list.

## What KVBench does not do

It does not run a model, measure a GPU, or claim any system's numbers. It makes
the survey's metric comparisons *checkable* rather than anecdotal; full
multi-axis measurement on real hardware is named as an open problem in the
manuscript's research agenda.
