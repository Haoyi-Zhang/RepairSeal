# Resources and execution contract

## Required local tools

- Python 3.10 or newer; the core proof-DAG implementation uses only the standard library.
- GCC and Clang for the retained native C cross-check on defined fixture executions.
- Standard POSIX shell utilities.

The reproduction command performs no network access and invokes no language-model API. It creates temporary and replayed files only below the user-supplied output directory.

## Frozen populations

- 20 designed fixture families x 4 variants = 80 requests.
- 300 deterministic structured semantic-stress requests.
- 400 post hoc grammar-generated requests produced by a separate AST generator and interpreted by an independently written AST semantics.
- 300 Codeflaws index rows for provenance and defect-taxonomy audit only; no corresponding public source program is executed.

Every frozen structured request has four inputs with three values each, hence 81 canonical points. Grammar-differential requests have two to four inputs and 9 to 81 points. The fixed 81x one-point/full-vector cell ratio is therefore reported only for the 285 refuted requests in the frozen structured population, not as a universal property of the format.

## Process budget

The integrated reproducer uses at most three concurrent local subprocesses and no nested worker pool. This remains below the four-core project ceiling. Individual stages have bounded timeouts. The retained campaign is small enough to run from a clean extraction with well below the 4 GiB memory ceiling in the audited environment.

## Descriptive performance

The retained medians from the final core run are proof check 2.436 ms, certificate-free topological evaluation 1.588 ms, recursive reconstruction 1.270 ms, and one-point refutation 0.457 ms. These are environment-specific descriptive measurements, not portable performance bounds. The full-vector semantic-cell equality, not elapsed time, is the implementation-independent result within the stated counting model.

Peak RSS, wall-clock time, and timestamps are regenerated and intentionally excluded from deterministic scientific-field comparisons.
