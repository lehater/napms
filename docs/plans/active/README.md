# Active execution

Current: `tae-acquisition-boundary.md`
Goal: clarify the Technical Access Evidence acquisition/normalization boundary without leaving S2 Domain Design.
Current task: record TAE as owner of normalized technical evidence while keeping collection initiation outside TAE and NEO outside the read/acquisition path.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/plans/active/tae-acquisition-boundary.md`, accepted TAE Tactical model, canonical Context Map/Strategic model, ADR-021, and the 2026-09-15 stakeholder clarification of acquisition ownership.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:

- `docs/domain/technical-access-evidence/tactical-model.md`
- `docs/domain/context-map.md`
- `docs/domain/strategic-model.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`
- `docs/domain/network-environment-operations/tactical-model.md`

Expand only if a concrete contradiction requires another owner.

## Recovery facts

- TAE remains a Bounded Context and owns immutable source-qualified normalized technical evidence.
- Collection/acquisition is initiated outside TAE by application/integration capabilities such as device/config collectors, NetFlow/IPFIX collectors or import adapters.
- TAE owns the meaning/invariants of its normalized evidence contract; source-specific producers must translate faithfully into that contract.
- TAE does not own polling cadence, scheduling, retries, credentials or source transport.
- NEO owns controlled mutation operations and is not the semantic read/acquisition gateway.
- Whether collectors and NEO share concrete provider/device access adapters/libraries is S3 Architecture, not S2 domain truth.
- TAE does not turn evidence into authorization, desired policy or ACL proposals; interpretation remains with downstream consumers/integration capabilities.

## Blockers

None currently known.

## Gate

Affected-edge G2 is open while canonical TAE/source relationships are being updated. Previous global MVP G2 remains the baseline outside this affected edge.

## Next

Update TAE Tactical ownership first, then Context Map / strategic projection, challenge the affected edges, and return the project to S2 ACCEPTED if no P0/P1 contradiction remains.
