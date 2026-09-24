# Generator-Independent Semantic Certificates

This artifact accompanies **Source-Bound Semantic Certificates for Finite Program-Repair Checking: Full-Vector Work Equivalence and Compact Refutations**.

## Supported scope and results

The implementation covers loop-free scalar 32-bit unsigned C over explicit finite ordered input domains. The receiver owns the original program, candidate, reference, repair guard, and three obligations: candidate definedness, repair-region agreement, and preservation outside that region.

Two evidence formats are implemented:

1. a **full-vector proof DAG**, checked after independent receiver parsing and canonical circuit reconstruction; and
2. a **compact one-point refutation**, which proves one actual violation and its candidate trace but cannot prove acceptance or leastness.

| Evidence | Result |
|---|---:|
| Frozen core requests | 380 (95 accepted, 285 refuted) |
| Exact-oracle status and canonical-witness agreement | 380/380 |
| Full-vector targeted corruptions rejected | 6,000/6,000 |
| Compact refutations verified | 285/285 |
| Compact corruptions rejected | 2,850/2,850 |
| Forged refutations of accepted requests rejected | 95/95 |
| Post hoc grammar-differential requests | 400 |
| Grammar oracle/topological agreement | 400/400 and 400/400 |
| Grammar compact refutations / rejected forgeries | 300/300 and 100/100 |
| Full proof / topological-direct cells on 20 correct fixtures | 45,198 / 45,198 |
| Recursive diagnostic cells | 309,582 (6.85x repeated work, not certificate gain) |
| Median full / compact bytes in the frozen core | 15,213 / 667 (22.8x) |
| Median compact semantic-cell reduction | 81x on the retained 81-point requests |

The exact negative result is central: full-vector checking and a certificate-free memoized topological evaluator perform the same number of local semantic-cell operations. The format supplies auditable source-bound evidence, not semantic-work reduction or an end-to-end speedup. The compact format obtains a real reduction only by certifying the weaker existential rejection claim.

The 400 grammar-generated requests were added during final blind audit with a separate AST generator and interpreter. They reduce template-overfitting risk but are post hoc, synthetic, and not a public-program sample.

## Reproduce everything

Requirements: Python 3.10 or newer, GCC, Clang, and standard POSIX utilities. No network, model API, credentials, private cache, or paper directory is used.

```bash
python3 tests/reproduce_all.py --output ../replayed-results
```

The output directory must be absent or empty. The command reruns the replay-table negative baseline, native compiler cross-checks, the 380-request study, 8,945 certificate negative controls, fail-closed security regressions, the 300-row Codeflaws index audit, and the 400-case post hoc grammar differential, then compares deterministic scientific evidence with retained results.

For a dependency-closure and packaging check from a clean extraction:

```bash
python3 tests/release_gate.py
```

The release gate parses every Python file, rejects nested archives, caches, and generated checksum/inventory manifests, verifies required dependencies, and executes the complete reproducer.

## Important entry points

- `src/proof_dag_producer.py`: untrusted full-vector producer.
- `src/proof_dag_checker.py`: receiver parser, canonical DAG builder, full-vector checker, and strong topological baseline.
- `src/refutation_witness_producer.py`: compact witness packager.
- `src/refutation_witness_checker.py`: receiver one-point checker.
- `tests/structured_study.py`: frozen 380-request study and 8,945 negative controls.
- `tests/holdout_differential.py`: post hoc 400-case grammar/AST differential audit (the legacy filename is retained for evidence compatibility).
- `tests/proof_dag_security.py`: malformed requests, strict JSON, type aliases, resource boundaries, and operator probes.
- `proofs/proof-dag.md`: conditional full-vector soundness argument.
- `proofs/refutation-boundary.md`: compact-refutation soundness and leastness boundary.
- `claim_evidence_ledger.csv`: claim-to-proof/code/input/result ledger.

## Trust and independence boundary

The receiver validates schemas and limits, computes source bindings, reparses source, reconstructs canonical topology, and checks evidence. The full-vector checker imports no producer module. The compact checker reuses receiver-owned parser/circuit code and imports neither producer. The proofs are manual conditional arguments, not proof-assistant derivations. Differential, native, boundary, and mutation testing reduce implementation risk but do not mechanically prove the receiver.

## Codeflaws boundary

`public-data/` freezes 300 unique rows from a pinned official Codeflaws defect-detail index: 284 `WRONG_ANSWER`, 9 `RUNTIME_ERROR`, and 7 `TIME_LIMIT_EXCEEDED` records over 181 contest identifiers. Corresponding source programs are not bundled or executed. No result represents those records as compiled, tested, repaired, or certificate-checked programs. This is the principal external-validity and venue-readiness limitation.
