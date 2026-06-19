#!/usr/bin/env python3
"""KVBench trace-conformance validator (dependency-free, Python 3 stdlib only).

This is the *contract validator* described in the manuscript's benchmark
proposal (Section "A Reproducible Benchmark Proposal"). It does NOT execute a
benchmark or measure any system; it checks whether an arbitrary party's trace
file conforms to the KVBench trace schema (schema/trace_schema.yaml), so that
independently produced traces and metric outputs become comparable.

Usage:
    python3 validate_trace.py schema/example_trace.jsonl
    python3 ../replay_harness/cpu_pilot.py | python3 validate_trace.py -

Exit status: 0 if every record conforms, 1 otherwise.
"""
import argparse
import json
import sys

# The schema is mirrored here in pure Python so the validator needs no YAML
# parser. schema/trace_schema.yaml is the human-readable source of truth; this
# dictionary must agree with it.
WORKLOAD_FAMILIES = {"multi_turn", "multi_agent_branch", "multi_tenant"}
GRANULARITIES = {"token", "block", "layer"}
CONSISTENCY_REQS = {"strong", "session", "eventual", "immutable"}

# field name -> (python type(s), validator predicate, human description)
REQUIRED_FIELDS = {
    "record_id": (str, lambda v: len(v) > 0, "non-empty string"),
    "tenant_id": (str, lambda v: len(v) > 0, "non-empty string"),
    "agent_id": (str, lambda v: len(v) > 0, "non-empty string"),
    "workload_family": (str, lambda v: v in WORKLOAD_FAMILIES,
                        f"one of {sorted(WORKLOAD_FAMILIES)}"),
    "prefix_tokens": (int, lambda v: v >= 0, "integer >= 0  (L)"),
    "per_token_bytes": (int, lambda v: v > 0, "integer > 0  (b)"),
    "arrival_time_s": ((int, float), lambda v: v >= 0, "number >= 0"),
    "tool_pause_s": ((int, float), lambda v: v >= 0, "number >= 0"),
    "granularity": (str, lambda v: v in GRANULARITIES,
                   f"one of {sorted(GRANULARITIES)}  (g)"),
    "consistency_req": (str, lambda v: v in CONSISTENCY_REQS,
                       f"one of {sorted(CONSISTENCY_REQS)}  (chi)"),
}
# parent_id is optional but, when present, must be a string or null.
OPTIONAL_FIELDS = {"parent_id"}


def validate_record(rec, lineno):
    errs = []
    if not isinstance(rec, dict):
        return [f"line {lineno}: record is not a JSON object"]
    for field, (typ, pred, desc) in REQUIRED_FIELDS.items():
        if field not in rec:
            errs.append(f"line {lineno}: missing required field '{field}' ({desc})")
            continue
        val = rec[field]
        # bool is a subclass of int in Python; reject it where int is expected.
        if typ is int and isinstance(val, bool):
            errs.append(f"line {lineno}: field '{field}' must be {desc}, got bool")
            continue
        if not isinstance(val, typ):
            errs.append(f"line {lineno}: field '{field}' must be {desc}, "
                        f"got {type(val).__name__}")
            continue
        if not pred(val):
            errs.append(f"line {lineno}: field '{field}' must be {desc}, got {val!r}")
    pid = rec.get("parent_id", None)
    if pid is not None and not isinstance(pid, str):
        errs.append(f"line {lineno}: optional field 'parent_id' must be a string or null")
    # Cross-field rule: a branch record should declare a parent.
    if rec.get("workload_family") == "multi_agent_branch" and not pid:
        errs.append(f"line {lineno}: multi_agent_branch record must set a non-null 'parent_id'")
    unknown = set(rec) - set(REQUIRED_FIELDS) - OPTIONAL_FIELDS
    if unknown:
        errs.append(f"line {lineno}: unknown field(s) {sorted(unknown)}")
    return errs


def main():
    ap = argparse.ArgumentParser(description="Validate a KVBench trace (JSONL).")
    ap.add_argument("trace", help="path to a .jsonl trace, or '-' for stdin")
    args = ap.parse_args()

    stream = sys.stdin if args.trace == "-" else open(args.trace, encoding="utf-8")
    all_errs = []
    n = 0
    families = set()
    try:
        for lineno, line in enumerate(stream, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                all_errs.append(f"line {lineno}: invalid JSON ({e})")
                continue
            n += 1
            families.add(rec.get("workload_family"))
            all_errs.extend(validate_record(rec, lineno))
    finally:
        if stream is not sys.stdin:
            stream.close()

    if n == 0:
        print("FAIL: trace is empty (0 records)", file=sys.stderr)
        return 1

    covered = families & WORKLOAD_FAMILIES
    if len(covered) < 2:
        all_errs.append(
            f"trace covers only {sorted(covered)}; the contract requires "
            f"at least two of {sorted(WORKLOAD_FAMILIES)}")

    if all_errs:
        for e in all_errs:
            print(e, file=sys.stderr)
        print(f"FAIL: {n} record(s) read, {len(all_errs)} conformance error(s).",
              file=sys.stderr)
        return 1

    print(f"PASS: {n} records conform; workload families present: {sorted(covered)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
