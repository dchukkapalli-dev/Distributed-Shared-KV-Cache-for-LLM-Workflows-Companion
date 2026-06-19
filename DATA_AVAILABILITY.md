# Data Availability

The machine-readable evidence matrix (all surveyed systems × five taxonomy axes
plus headline metric, as a `.csv`), the search log, the benchmark trace schema
(`.yaml`) with example traces (`.jsonl`), the dependency-free trace-conformance
validator, and a CPU-only pilot generator are released as this machine-readable
companion artefact. The artefact is released under an open licence (MIT for code,
CC-BY-4.0 for data; see `LICENSE`) and is permanently archived on Zenodo under the
concept DOI [10.5281/zenodo.20754633](https://doi.org/10.5281/zenodo.20754633),
which always resolves to the latest version, with a source mirror at
<https://github.com/dchukkapalli-dev/Distributed-Shared-KV-Cache-for-LLM-Workflows-Companion>.

| Artefact | File | Referenced in manuscript |
|---|---|---|
| Evidence matrix (54 systems × 5 axes + headline metric) | `evidence_matrix.csv` | Taxonomy section; in-paper tables show a representative 33 of the 54 |
| Search audit trail (12 queries, 312 raw hits) | `search_log.csv` | Survey methodology / PRISMA-style flow |
| Benchmark trace schema | `kvbench/schema/trace_schema.yaml` | Benchmark proposal — trace schema and metrics |
| Example trace (3 workload families) | `kvbench/schema/example_trace.jsonl` | Benchmark proposal — companion harness contract |
| Trace-conformance validator | `kvbench/validate_trace.py` | Benchmark proposal — companion harness contract |
| CPU-only pilot generator | `kvbench/replay_harness/cpu_pilot.py` | Benchmark proposal — companion harness contract |

The benchmark component is a **contract validator**, not a benchmark execution
engine: it fixes a common trace schema and multi-axis metric set and demonstrates
that the contract is satisfiable on a commodity laptop, without claiming to
reproduce any surveyed system's production-scale numbers. Full multi-axis
measurement on real hardware is listed as an open problem in the research agenda.

No human-subjects data, proprietary data, or model weights are included.
