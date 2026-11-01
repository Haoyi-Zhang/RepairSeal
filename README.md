# RepairSeal

This artifact accompanies *Source-Bound Semantic Certificates for Finite
Program-Repair Checking*, a bounded evidence-design and matched-recalculation
study of explicit repair policies and canonical diagnostics.

Measurements come from executed artifact workflows. Complete-JSON and bounded
framed-stream receivers implement the same full-domain decision contract.

## Scope

### Identity-scoped approval journal

`src/admission_journal.py` is an owned durable application consumer. The
receiver registers its request separately from incoming packets, records a
checked semantic decision, and answers approval queries only for an explicit
current request identity. Replacing a candidate advances its revision; an old
receipt cannot approve that replacement. A valid refutation remains a negative
decision. An exhausted work allowance or malformed packet commits no receipt.
The equally informed certificate-free path offers the same decisions.

```sh
python -B -m unittest discover -s tests -p test_admission_journal.py -v
python -B tests/check_admission_results.py
python -B tests/admission_journal_study.py --output /fresh/owned-approval
python -B tests/report_admission_results.py --output ../paper/admission-results.tex
```

The retained `results/admission-journal` activity contains 28 clean receiver
processes, five separately registered requests, one approval and four
refutations. All full/direct decisions, canonical witnesses and checked-cell
counts agree. Receiver sandboxes contain no producer module. Five closed
SQLite journals retain the actual receipts; request replacement invalidates
the old approval and stale evidence rejects. This is one source-derived repair
and four existing controls, not five independent upstream applications. It
does not measure review effort, latency or a new memory advantage. The journal
assumes owned local storage and SQLite's serialized durability contract; it
does not authenticate the external source correspondence or a live deployment.

### Source-linked ceiling-division consumer case

The actual upstream llama.cpp macro edit is retained in
`public-data/ceil-div-source.json`, with immutable before/after revisions,
full-source fingerprints, exact macro lines and the MIT notice in
`public-data/ceil-div-LICENSE.txt`. The manual correspondence proof is
`proofs/ceil-div-correspondence.md`. Only pure unsigned 32-bit scalar arguments
and a nonzero divisor are in scope; the study executes owned normalized
functions, not llama.cpp, Vulkan, upstream tests or a vulnerable application.

One command retrieves both original source files as text, checks their byte
identities and macro lines, then regenerates the finite correspondence and
consumer decisions in a new directory:

```sh
python -B tests/upstream_ceil_case.py --verify-upstream --output /new/ceil-result
```

Omit `--verify-upstream` for the offline model/packet replay. The canonical
inputs, 210 interpreted candidate-point observations, five full packets, four
compact packets and outcomes are in `results/upstream-ceil/`. Each request has
42 points: 12 in the overflow repair region and 30 preservation points. The
actual replacement is accepted; the unchanged original is refuted. Three
additional adverse candidates are explicitly authored controls for preservation,
an unused undefined assignment and trace-priority/overfit behavior, not
independent upstream fixes. Full and certificate-free direct checking agree
on every verdict, canonical witness and cell count.

For a separate receiving process:

```sh
python -B src/proof_dag_checker.py results/upstream-ceil/supplied-request.json results/upstream-ceil/supplied-full.json
python -B -m unittest discover -s tests -p test_upstream_ceil.py -v
```

The receiver obtains its authoritative request separately from the packet.
Full checking authenticates every intermediate value and the declared policy;
direct recalculation makes the same decision without producer evidence.
Compact refutation can accept the authentic nonleast point (2,UINT_MAX), while
the full trace-priority diagnostic is (31,UINT_MAX) for the owned trace control.
Neither format authenticates external source history or the manual mapping.
Paper tables are regenerated only after replay of the retained packets.

### Typed transfer of the selected macro expressions

`src/macro_bridge.py` now lowers the selected before/after expression text rather
than requiring handwritten scalar bodies. Its bounded parser admits pure word
arithmetic, comparisons and explicit Boolean-to-word conversion; unsupported
syntax, signed intermediate arithmetic, calls, side effects and preprocessing
ambiguity fail closed. The receiver still supplies the selected definition,
unsigned-32 pure-argument premise, reference, repair selector and finite domain.
The bridge does not infer real caller types, evaluate arbitrary macro arguments,
or parse/preprocess the containing C++ application.

```sh
python -B -m unittest discover -s tests -p test_macro_bridge.py -v
python -O -B -m unittest discover -s tests -p test_macro_bridge.py -v
python -B tests/macro_transfer_study.py --native --verify-upstream --output /fresh/macro-transfer
```

The retained `results/macro-transfer/` run verifies the two complete immutable
upstream source files as text, derives both scalar models and checks the same
42 inputs (12 repair, 30 preservation). GCC and Clang execute only a small,
reviewed pure-arithmetic harness containing the selected expressions and their
generated lowerings. All 84 paired compiler/input rows preserve the respective
old modular and new ceiling formulas, comprising 336 scalar outputs, not 336
independent programs. For each compiler, the old formula differs from ceiling
on 12 of 42 points; the new formula matches ceiling on all 42. The retained
summary field `lowered_models_match_mathematical_reference` denotes the two
version-specific formulas, not agreement of both versions with ceiling.
Full and direct checking accept the generated request with 1,680
cells each. The upstream application and its tests are not built or executed.
Without `--verify-upstream`, replay uses the retained selected definitions;
it does not claim fresh source acquisition. Without `--native`, it is model-only.
The complete Linux reproducer runs the native harness without network retrieval.
Inserted trace events belong to the normalization, not native macro execution.

### Descriptor-allocation consumer

The source-derived consumer connects the selected repaired value to the
reservation/consumption path of the matrix-multiplication caller. Both complete
immutable source files are checked against their existing identities, including
the batch declaration, reservation, loop, allocation update and consumption
guard. The authoritative limit type is recorded from the Vulkan specification.
This is a selected manual context correspondence, not generic C++ analysis.

```sh
python -B -m unittest discover -s tests -p test_descriptor_consumer.py -v
python -O -B -m unittest discover -s tests -p test_descriptor_consumer.py -v
python -B tests/descriptor_consumer_study.py --native --output /fresh/descriptor-consumer --compare results/descriptor-consumer
```

The existing 42 batch/limit pairs are retained. A predeclared limit of 64 loop
iterations admits 32 pairs and explicitly excludes 10. Starting with requested,
allocated and consumed counts all equal to four, the old expression
under-reserves on five admitted pairs; the replacement fits every dispatch.
Two native compilers agree with the accounting model on 128 role/input/compiler
rows. Spare pool capacity can mask under-reservation, so the model distinguishes
an incorrect requested increment from an actually denied dispatch.
Seven admitted pairs use the reported maximum device limit; the smaller limits
are arithmetic stress controls, not claimed conforming device configurations.

For an independently acquired exact pair of upstream files, add
`--source-before /private/before.cpp --source-after /private/after.cpp`.
Without these options, the command replays the retained context and does not
claim fresh upstream acquisition. The retained source check is in
`results/descriptor-consumer/summary.json`; the device report remains attributed
to the upstream issue. No GPU, shader, complete Vulkan application or new
independently sampled program is executed by this local consumer. The
conditional invariant and its assumptions are explained in
`proofs/ceil-div-correspondence.md`.

The paper reads generated counts from the same bound observations:

```sh
python -B tests/report_descriptor_consumer.py --output ../paper/descriptor-consumer-results.tex
```

The older Codeflaws native observations remain derived historical records.
Their original C and test bytes are not redistributed. The exact-archive and
four-source fingerprint gates and full opt-in command are documented below
under **External archive retrieval and identity gate**; offline model replay is
not a native rerun. No current ceiling-division run changes that evidence.

The receiver checks loop-free scalar unsigned-32 C over explicit finite ordered
input domains. It owns the original program, candidate, reference and repair
guard. The obligations are candidate definedness, agreement in the repair region
and preservation outside it.

The full-vector format is checked after independent parsing and canonical
circuit reconstruction. A compact one-point refutation checks one actual
violation and its candidate trace. It establishes rejection, not acceptance or
the least violating point. On equal full-domain acceptance obligations, full
checking and the certificate-free topological evaluator perform the same local
semantic-cell work. The one-point reduction corresponds to a different,
existential obligation.

## Receiver-owned cross-request reuse

The optional `src/reusing_checker.py` checks the same full packets while retaining
independently established cells in a single-threaded, process-local receiver cache.
No producer cache or serialized cache is imported. Structural identities include the
operator, sort, literal or input name, and complete child identities; point identities
include named unsigned values rather than coordinate offsets. Changed source is rebuilt
and current bindings/roots/vectors are still checked. A failed packet adds no cell facts.
At most 65,536 cells and 32,768 structural terms are retained; term-space pressure clears
the cache, and cell-space pressure merely leaves new cells uncached. This changes reuse
work, not acceptance. The trusted in-process cache is not an untrusted interchange format.

```sh
python -B tests/test_receiver_reuse.py -v
python -O -B tests/test_receiver_reuse.py -v
python -B tests/receiver_reuse_study.py --output /absolute/fresh/reuse.json --compare results/receiver-reuse.json
```

In the fixed fixture-then-stress order, all 380 retained requests have identical status
and canonical witness under cold full/direct and cached full/direct checking. Each cold
arm evaluates 1,179,684 cells; each equally informed cached arm recomputes 413,944 and
reuses 765,740. Full-vector checking still compares all 1,179,684 submitted cells, whereas
the direct arm receives no vectors. There is no new wall-time experiment or claim of a
certificate-exclusive cache advantage. Eight regression methods cover changed source,
new domain values, reordered named axes, current packet tampering, invalid packet rollback,
capacity limits, and undefined candidates in ordinary and optimized Python execution.
The warm receiver also rejects all 600 retained first-seed full-packet mutations (20
correct fixtures, 30 classes), with no alteration of previously established cell facts.
These are replayed controls, not 600 new defects. This is a new owned finite replay,
not added Codeflaws admission or a rewrite of old runs.

## Bounded vector reception and matched storage baselines

`src/vector_stream.py` receives one canonical node record per line. It rebuilds
the header from the authoritative request, bounds each read using the expected
descriptor and finite point count, checks every cell, and releases computed
vectors after their last use. Obligation and candidate trace roots stay live.
No verdict is returned until the terminal integrity seal and exact EOF pass.
This bounds receiving records, not request admission or producer conversion.
Conversion starts from a complete producer packet and is not a streaming
generation algorithm. The full JSON protocol remains supported.

```sh
python -B src/vector_stream.py encode /path/full.json /fresh/packet.rows
python -B src/vector_stream.py check /path/request.json /fresh/packet.rows
python -B src/vector_stream.py direct /path/request.json
python -B -m unittest discover -s tests -p test_vector_stream.py -v
python -O -B -m unittest discover -s tests -p test_vector_stream.py -v
python -B tests/vector_stream_study.py --output /fresh/logical.json --compare results/vector-stream.json
python -B tests/vector_stream_study.py --allocations --output /fresh/allocations.json
```

All 380 frozen requests preserve the status, canonical witness and 1,179,684
semantic cells per arm. The median peak retained-vector fraction is 0.400;
this is a within-request residency ratio, not a whole-runtime allocation ratio.
The matched direct method has the same last-use schedule, and a full-residency
direct baseline has the same prepared operator kernel without reclamation.

The allocation study fixes 50 requests before measurement: all 20 correct
fixtures and stress-manifest offsets 0,10,...,290. Three rotated-order repeats
per arm give 600 measurements. Every arm gets the same decoded authoritative
request; both wire formats use canonical compact JSON. Certificate file
decoding, reconstruction, validation and diagnosis
are measured; producer conversion and request loading are excluded. On the
recorded Windows CPython runtime, median paired peak-allocation ratios are
0.490 for framed/full-JSON reception, 0.669 for liveness/full-residency direct
evaluation, and 1.577 for framed/matched-liveness direct evaluation. Thus
reclamation is available without a certificate; certificate reception still
has extra allocation costs. These are traced Python allocations, not RSS,
throughput, independent real-world programs, or a claim of general compression.
Raw observations and environment are in `results/vector-allocation.json`.

A separate opt-in Linux fresh-process RSS activity stopped at its fixed
110-second limit after 584/600 planned measurements. Forty-eight of the 50
predetermined requests have complete four-arm/three-repeat pairs; the other
two are explicitly incomplete or unobserved, not replaced. Complete-prefix
medians are about 22.2 MiB for each arm, with all three paired ratios rounding
to 1.000: this does not establish a process-memory benefit. Raw and unmatched
records, the frozen protocol and the budget-stop error are retained losslessly
in `results/vector-rss/observations.zip`; `summary.json` labels the analysis
incomplete. It is not relabeled or pooled with later data.

An independently frozen full-cohort replication completes all 600 measurements:
the same 50 requests, four fresh-process arms and three rotated repeats. All
outcomes match their fixed expectations and semantic cell work agrees within
every pair. Arm medians are 22,688 / 22,532 / 22,684 / 22,542 KiB for complete
JSON, full direct, framed stream and liveness direct, respectively. Medians of
the paired framed/JSON, liveness/full-direct and framed/liveness-direct ratios
are 1.000177, 1.000000 and 1.006571. These complete observations do not demonstrate
a framed-process RSS advantage. The declared 300-second/180-child-CPU-second
limits were respected (27.750 seconds wall, 27.533 child CPU); those resource
clocks are not a cross-run latency comparison. Full raw records and the frozen
plan are in `results/vector-rss/replication.zip`, with descriptive statistics in
`replication-summary.json`. Original incomplete and new complete records remain
separate. This closes the RSS population-coverage gap, not a claim of benefit.

`python -B tests/verify_vector_rss.py` and
`python -B tests/verify_vector_rss_replication.py` verify both retained payloads
without new memory measurements. See `resources.md` for boundaries and limits.
Neither measurement activity is part of the default reproducer or CI.

## Setup and run

Use Python 3.10 or later. Portable receiver and comparison checks need only the
standard library. The complete resource-accounted campaign requires Linux, GCC,
Clang and standard POSIX utilities. Runners resolve and record the actual
compiler paths; no project command downloads a toolchain, dataset or model.

From this directory, use a fresh output directory outside the project:

```sh
python3 -B tests/reproduce_all.py --output /absolute/fresh/repairseal-run
```

This runs the replay-table baseline, two native compiler checks, the 380-request
study and 8,945 selected certificate controls, input/receiver regressions, the
300-row Codeflaws metadata audit, the corrected 400-request grammar differential
and the retained-file replay. The disk gate reloads authoritative requests and
recovers their input order from the generators and saved seeds, not certificates.
The output must be absent or empty. Failed commands and scientific mismatches
exit nonzero; diagnostic output remains available.

For the functional clean-extraction check, including that complete campaign:

```sh
python3 -B tests/release_gate.py
```

The gate checks dependency closure and packaged-file hygiene before execution.
Its optional `--keep-output` accepts a new or empty directory and preserves
caller-owned contents. Without it, the gate cleans only its own temporary tree.

## Focused checks and outputs

These portable commands avoid native compilation and the complete campaign:

```sh
python -B tests/test_cli_utf8.py
python -B tests/test_reproduction_contract.py
python -B tests/test_boundary_selection.py -v
python -B tests/test_nested_trace_repair.py
python -B tests/test_coordinate_membership.py
python -B tests/test_prepared_cells.py
```

The UTF-8 checks preserve receiver-owned identifiers under a non-UTF8 host
default. Comparison controls distinguish permitted environment telemetry changes
from scientific values and preserve occupied output directories. Boundary
selection keeps three small values plus all five mandatory unsigned boundaries.
Nested-source checks preserve preorder source-site numbering across skipped
branches and shared AST occurrences.

A portable retained-packet report can be generated separately:

```sh
python -B tests/bounded_closure_report.py --output /absolute/fresh/bounded-replay
```

That report rechecks 380 full packets, 285 authentic compact refutations and
the same-information direct path. It also checks grammar source/axis bindings;
it does not rerun the 400-request semantic campaign. Full native/compiler
reproduction remains Linux-only; unavailable Windows POSIX telemetry is null.

## Retained evidence

| Study | Result | Location |
|---|---|---|
| Frozen core | 380 requests: 95 accepted, 285 refuted | `results/`, `proof-data/structured-study.json` |
| Equal acceptance work | 45,198 cells per arm on 20 correct fixtures | retained study and paired receiver records |
| Core full checking | 1,179,684 cells per arm over all requests | `results/bounded-receiver-replay/` |
| Corrected grammar | 400 requests, 657,728 points; 47,327,168 cells per full-domain arm | `proof-data/holdout-differential/` |
| Nested source sites | Five owned requests, 320 candidate-point observations | `results/nested-source-occurrences/` |
| Selected mutations | 6,000 full, 2,850 compact, 95 forged-acceptance controls rejected | frozen study records |

The full/compact byte comparison concerns the same 285 refutations: median
sizes are 15,604 and 667 bytes. The 81-fold cell reduction on those 81-point
requests compares universal checking with one supplied violation, not equal
acceptance guarantees. Grammar inputs and mutation controls are constructed
tests, not independent public-program defects.

Paired measurements are retained separately by source/environment in
`results/boundary-selection/receiver-timing.json` and
`results/nested-source-occurrences/receiver-timing.json`. Both compare equal
acceptance obligations; the reported full/direct ratios exceed one. To run a
new, isolated measurement, inspect `tests/receiver_timing.py` and supply an
unused output file. Do not pool current allocation measurements with historical
container timings.

## Implementations and conditions

- `src/proof_dag_producer.py`: full-vector producer.
- `src/proof_dag_checker.py`: receiver parser, canonical circuit and direct baseline.
- `src/refutation_witness_checker.py`: one-point receiver.
- `tests/structured_study.py`, `holdout_differential.py`, `disk_replay.py`:
  core study, grammar differential and authoritative disk replay.
- `formats.md`, `proofs/`: schemas, local rules and conditional arguments.
- `resources.md`, `claim_evidence_ledger.csv`: resource protocol and evidence map.

The receiver checks exact schemas, source/domain/root bindings and every
required local semantic value. Resource bounds cover actual AST depth and node
counts; the current selector admission conservatively requires its definedness
to simplify to true. Manual proof arguments and separate checker code are
complemented by finite tests, not proof-assistant mechanization.

## Codeflaws boundary

`public-data/` freezes 300 unique rows from a pinned official Codeflaws
defect-detail index: 284 `WRONG_ANSWER`, 9 `RUNTIME_ERROR`, and 7
`TIME_LIMIT_EXCEEDED` records over 181 contest identifiers. The original frozen
index audit used metadata only: it did not acquire or execute corresponding
source programs, and those 300 records are not 300 compiled, repaired, or
certificate-checked programs. A later, separately identified source study uses
a privately acquired official archive; it does not replace that historical
population or relabel its results.

### Optional offline source study

`tests/codeflaws_cases.py` contains project-authored mathematical normalizations
of two source-selected natural pairs from the frozen index:
`4-A-bug-18258406-18258457` and `84-A-bug-9385928-9385933`. Each pair contributes
its buggy and supplied versions, giving four requests on 64 points each.
Selection was structural, not random or based on held-out outcomes. References
come from the official task specifications, not the supplied outputs. The
study evaluates supplied versions; it does not generate repairs or estimate
benchmark-wide repair effectiveness.

The unchanged receiver's source audit covers 600 archive-member occurrences
across the 300 indexed pairs, with 588 distinct submission filenames and 582
distinct source contents. It admits zero original translation units. These
are unsupported-language admissions, not repair-correctness verdicts; the
four adapted requests do not count as original-source admission.

For model-only replay, Python and the bundled project files suffice:

```bash
python -B tests/codeflaws_source_study.py --output ../private-source-models
```

Use a new or empty output directory. This default mode performs no download,
archive inspection, C compilation, or native execution. It checks full-vector
and certificate-free topological results against the mathematical oracle,
records equal work (4,352 cells per arm across the four requests), and records
paired timings. Equal work does not establish a speedup. Compact
checking is compared with direct checking of the same supplied point/trace;
neither proves acceptance or leastness, and witness discovery is not free.
Source inspection and manual I/O/type mapping are separate, untimed construction
work, not an automated frontend or a zero-cost preprocessing stage.

### External archive retrieval and identity gate

Obtain the archive separately from the download link on the
[official Codeflaws site](https://codeflaws.github.io/), after assessing the
applicable rights and terms. Its advertised link is the unversioned
[NUS archive](http://www.comp.nus.edu.sg/~release/codeflaws/codeflaws.tar.gz);
the private acquisition used the corresponding
[HTTPS URL](https://www.comp.nus.edu.sg/~release/codeflaws/codeflaws.tar.gz).
Do not substitute the website's GitHub source ZIP/tarball, a partial download,
or another snapshot. Record the actual retrieval URL, date, byte count and
SHA-256 privately. No artifact command downloads this payload.

The reviewed archive is exactly 265,695,532 bytes with SHA-256
`2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11`.
The driver rejects any other size or digest before opening the tar stream.
This identifies the locally reviewed snapshot; the metadata Git commit is
not an archive release identifier or a distributor signature. Inside the
archive, the four reviewed whole-source identities are:

| Member below `codeflaws/` | SHA-256 |
|---|---|
| `4-A-bug-18258406-18258457/4-A-18258406.c` | `0713806f76a4bf8c22a3ee7ca6a2585b2d08e2073b02094f6c7337ec1d0c24df` |
| `4-A-bug-18258406-18258457/4-A-18258457.c` | `6f74c3b6969296535b12ca5393e781fa0c8ce783f1c40f2dd4d2247634c31486` |
| `84-A-bug-9385928-9385933/84-A-9385928.c` | `1686ffd63ba4033a98d5b3d6b96b8e28a89764b99ae523958191a99d68e56431` |
| `84-A-bug-9385928-9385933/84-A-9385933.c` | `c6cacf09a2c35fa5e4071b10e0cf1b361060f1bf62dcf57375b23ee2cec34c90` |

The driver checks these source digests and the complete 600-member cohort,
rejecting missing or duplicate source-member identities. To repeat only that
inspection and model replay, without running third-party code:

```bash
python -B tests/codeflaws_source_study.py --archive /private/codeflaws.tar.gz --output /private/source-inspection
```

### Explicit reviewed-only native opt-in

Native execution requires both `--execute-reviewed` and an explicit local
compiler, in addition to the exact archive. Only opt in after reviewing all
four complete translation units and their source-to-model correspondence:

```bash
python -B tests/codeflaws_source_study.py --archive /private/codeflaws.tar.gz --execute-reviewed --compiler /path/to/reviewed/cc --output /private/source-native
```

For an already installed, reviewed Zig compiler use its executable path and
add `--zig`; the study does not install a toolchain. Compilation is serial,
uses C11/O0 and an isolated private working directory, and runs only the four
unchanged, digest-matched translation units. No upstream build/repair script
is run. This opt-in is not part of the core reproducer, release gate, or CI.

The native protocol compares decoded stdout with the corresponding model on
each 64-point domain (256 source-version/input observations). The 4A codec maps
exact `YES`/`NO` labels to 1/0 after stripping surrounding whitespace; the 84A
codec requires a single nonnegative decimal integer. Process status zero is
successful completion, not the scalar model output. Correspondence assumes
successful input/output and a 32-bit signed-`int` implementation; the driver
checks integer-width macros. On these legal inputs the relevant arithmetic
intermediates are nonnegative and at most 300,000,000, so the unsigned-32
normalization preserves the computation. It does not cover malformed inputs,
I/O failure, arbitrary signed C, or all legal task inputs. Certificate source
bindings and canonical branch traces refer to the normalized functions, not
directly to the original whole programs or measured native branch traces.

Existing repair and held-out tests are a separate comparison: up to the first
eight inputs per split/subject by lexical member name, selected before their
payloads are read, with no replacement or model tuning from held-out outcomes.
The current selection comprises 24 input/output pairs, each run on both
versions (48 test executions, not 48 distinct tests). Actual completion,
agreement, failures and timings must be read from the run's `summary.json`,
`native-observations.csv`, and `existing-test-observations.csv`; protocol counts
alone are not successful-run evidence.

Project-authored correspondence explanations and the derived records are in
[results/source-correspondence/](results/source-correspondence/), with the
measured current source bindings, four full packets and two compact packets.
Keep the archive, original source/test bytes, compiler, binaries and raw private
logs outside the deliverable. Publish only project-authored code/models and
derived data that do not reproduce upstream source or test payloads; check
serialized requests, certificates and logs as well as file extensions.

The bundled index's pinned repository provenance, its row-97 empty-tag
normalization, and the exact upstream MIT notice are documented in
[licenses/NOTICE.txt](licenses/NOTICE.txt) and
[licenses/Codeflaws-MIT.txt](licenses/Codeflaws-MIT.txt). That repository notice
does not establish an archive-wide license or rights from every Codeforces
contestant. Project licensing does not relicense upstream programs or tests.

## Manuscript diagrams

The model and protocol schematics are drawn directly in Python as vector PDFs
with embedded STIX fonts. They encode the stated relationships, not measured
performance. To regenerate them with Python 3.9+ and Matplotlib:

```sh
python -B figures/draw_schematics.py --output figures
```

## Portable path notation

Published execution records use `<PYTHON_ROOT>`, `<NODE_ROOT>` and `<RUNTIME_ROOT>` for local tool installations, `<DEPENDENCIES_ROOT>` for local dependencies, and `<PROJECTS_ROOT>`, `<ARTIFACT_ROOT>`, `<SOURCE_ROOT>` and `<WORK_ROOT>` for the workspace, artifact checkout, source checkout and temporary work directory of the recorded run. These are path aliases, not literal directories or claims that historical temporary files are included in this bundle. Substitute the corresponding local roots when replaying a command. Recorded tool versions, source/input identities, measurements, outcomes and failures are unchanged. Current file inventories bind the portable published bytes; any `recorded_` identity denotes pre-normalization bytes.
