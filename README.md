# Companion artefact

Machine-readable artefacts for the survey **"A Distributed Shared KV-Cache Layer
for Agentic LLM Workflows: A Survey and Design Study of KV-Cache-as-a-Service."**

**Deposit.** Permanently archived on Zenodo under the concept DOI
[10.5281/zenodo.20754633](https://doi.org/10.5281/zenodo.20754633), which always
resolves to the latest version. Source mirror at
<https://github.com/dchukkapalli-dev/Distributed-Shared-KV-Cache-for-LLM-Workflows-Companion>.

## Contents

```
companion/
  README.md                 this file
  LICENSE                   dual licence (MIT for code, CC-BY-4.0 for data)
  CITATION.cff              citation metadata
  DATA_AVAILABILITY.md      what is released and where it is referenced
  evidence_matrix.csv       all 54 classified systems x 5 taxonomy axes + headline metric
  search_log.csv            per-query search audit trail (feeds the PRISMA flow)
  kvbench/                  the reproducible benchmark contract
    README.md
    validate_trace.py       dependency-free trace-conformance validator
    schema/
      trace_schema.yaml      machine-readable trace schema
      example_trace.jsonl    12-record example covering all three workload families
    replay_harness/
      cpu_pilot.py           CPU-only conforming-trace generator
      requirements.txt       (stdlib only)
      README.md
```

## Provenance of the two data files

- `evidence_matrix.csv` — the full classification underlying the manuscript's
  taxonomy tables. The two in-paper tables reproduce a representative 33 of the
  54 rows for space; this file is the complete matrix on all five axes.
- `search_log.csv` — the 12 queries (arXiv, ACM DL, IEEE Xplore, venue
  proceedings, DBLP, and forward/backward snowballing) whose `raw_hits` sum to
  the 312 records identified in the manuscript's PRISMA-style flow. After
  cross-source de-duplication this yields 241 screened, 102 full-text assessed,
  and 88 retained (of which 54 are systems). The `relevant_after_screen` column
  is a per-query relevance tally and need not sum to a PRISMA cell because the
  same record can surface under several queries.

## Reproducing the benchmark contract check

```bash
cd kvbench
python3 validate_trace.py schema/example_trace.jsonl          # -> PASS
python3 replay_harness/cpu_pilot.py | python3 validate_trace.py -   # -> PASS
```

Python 3.8+ standard library only; no third-party packages.
