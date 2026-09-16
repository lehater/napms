# Catalogue curation — quality requirements

Status: M7 PILOT CANDIDATE / non-canonical.

This artifact is documentation-only. Product code and tests are read-only evidence for the pilot.

- `QREQ-CAT-001` — Catalogue mutation authorization fails closed when the required Authority Management assignment is absent or ambiguous under accepted authority semantics.
- `QREQ-CAT-002` — Mutation processing must not silently overwrite a concurrent accepted change; stale submissions produce an explicit conflict.
- `QREQ-CAT-003` — Historical identities/facts referenced by downstream business truth are preserved rather than silently rewritten or hard-deleted by ordinary curation.

Idempotency is not promoted to a standalone quality requirement in this pilot because the accepted source leaves exact behavior dependent on the command/idempotency contract. Concrete HTTP idempotency mechanics remain S3-owned.