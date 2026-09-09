# Active execution

Current: `PLAN-016B-i16b-connectivity-decision-runtime.md`

Goal: replace the transitional local Decision provider with the accepted durable Connectivity Decision runtime while preserving the completed I16A architecture.

Current task: WP5 — integrate authorized final Decision behavior into the current I16A Web information architecture.

## Working set

Read first:
- `docs/plans/active/PLAN-016B-i16b-connectivity-decision-runtime.md`

Expand only into `docs/requirements/web-ui-requirements.md`, current Web connectivity/navigation/API files and Decision HTTP tests when a concrete WP5 question requires them.

## Blockers

None. The accepted UI must preserve Connectivity as the primary resource-centric workspace and must not invent Pending/approval lifecycle semantics.

## Gate

WP4 green evidence on commit `89d73515b52c2ec12d4734cf8f6bab2c4f0324b6`:
- core gate #87 — success;
- postgres persistence gate #72 — success;
- docker local runtime gate #46 — success;
- harness gate #92 — success.

WP4 now proves:
- independent DecideConnectivity and ReadConnectivityDecision authority;
- authorized Decision scope and exact ACC subject discovery;
- direct final Allowed/NotAllowed recording;
- durable authorized list/detail with reason, evidence, validity, supersession and provenance;
- authenticated actor, decision time and authority reference are server-owned;
- Decision persistence uncertainty has explicit 503 handling;
- no pending/work-queue lifecycle was introduced.

## Next

Execute WP5 only: add the specialized Decisions Web workspace and connect existing contextual product flows to the real Decision runtime where semantics are already accepted. Preserve current Connectivity-first IA; do not start WP6 local-seed/removal work until Web behavior is green.
