# Technical Access Evidence — context problems

Bounded context: **Technical Access Evidence (TAE)**

Canonical semantic sources:

- `docs/domain/technical-access-evidence/tactical-model.md`
- `docs/domain/context-map.md`
- `docs/domain/strategic-model.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`

## Accepted/fixed constraints

- TAE owns the canonical normalized source-qualified evidence language and immutable evidence history.
- TAE does not initiate collection and does not own polling cadence, scheduling, retries, credentials or source transport.
- Device/config collectors, NetFlow/IPFIX collectors and import adapters are non-BC acquisition/integration capabilities that translate source material into the TAE contract.
- NEO owns controlled mutation and is not the general evidence-read/acquisition gateway.
- TAE evidence does not itself create authorization, desired policy, ACL/access proposals or remediation intent.
- Provider Policy Interpreter may consume selected TAE configured evidence under an explicit source contract, provider material directly, or both.

## Open architecture problems

### TAE-A01 — provider/device access realization

Decide how acquisition capabilities access real equipment/controllers/telemetry sources and whether they share concrete provider/device clients, protocol libraries or adapters with NEO.

This is an S3 Architecture question. Shared implementation must not merge TAE acquisition ownership with NEO mutation semantics.

### TAE-A02 — acquisition orchestration

Choose the concrete application/runtime realization for polling, scheduled collection, push ingestion, retries, credentials and source-specific backoff/failure handling.

The mechanism must preserve the domain rule that TAE accepts source-qualified normalized evidence but does not own collection scheduling.

### TAE-A03 — production source coverage contracts

For each production configured-policy source, define whether PPI receives provider material directly, through TAE evidence, or both, and what source contract is sufficient to assert completeness/currentness for a comparison scope.

TAE itself must not infer `Complete` or `Current` merely from recency or an empty/non-empty capture.

## Dependencies / blockers

None of these questions block the accepted S2/G2 domain baseline. They become implementation blockers only when the corresponding real acquisition/provider integration slice is selected.

## Evidence still needed

- first concrete device/provider acquisition API;
- first NetFlow/IPFIX ingestion path;
- operational requirements for polling cadence/retry/credential handling;
- provider interpretation requirements for the first configured-policy source.

## Revisit triggers

Revisit this register when S3 starts for TAE acquisition/provider integration, a real device/config collector is selected, or a NetFlow/IPFIX collector is introduced.
