# Certificate formats

All JSON is parsed with duplicate-key rejection and rejection of non-finite constants. Objects are closed-world: extra fields are invalid. Integer fields reject JSON booleans.

## `finite-semantic-proof-dag-v1`

The full-vector certificate binds the request identifier, word width, ordered domains, authoritative source hashes, canonical points, canonical circuit nodes, role roots, obligation roots, and an outer SHA-256 digest. Each node stores its operation, children, result sort, and complete vector over the canonical point order. The receiver reconstructs the expected circuit from source and requires exact structural equality before validating each local vector cell.

This format can support universal acceptance and canonical counterexample selection because it covers the complete finite domain. It is not a compressed symbolic proof: against a memoized topological direct evaluator, both methods visit every node--point cell exactly once.

## `finite-semantic-refutation-v1`

The compact format contains exactly:

- `kind`;
- `request_id` and `word_bits`;
- `input_order` and complete `domains`;
- `source_sha256` for original, candidate, reference, and repair guard;
- one `obligation`;
- one in-domain `input`;
- one exact candidate `trace`; and
- `certificate_sha256` over all preceding fields.

The receiver reparses and evaluates the bound sources at only the claimed point. Acceptance proves that the named obligation is false there and that the trace is authentic. It proves neither leastness nor acceptance of any other point. The checker rejects this format for a true claimed root, malformed traces, altered sources or domains, stale or recomputed malicious bindings, and extra fields.

Canonical JSON uses UTF-8, sorted keys, no insignificant whitespace, and no NaN or infinity.
