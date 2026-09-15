# Technical Access Evidence architecture boundary

## Purpose

Realize Technical Access Evidence as a framework-independent module while keeping source/provider parsing outside domain meaning and keeping downstream policy-realization semantics outside TAE.

## Module boundary

```text
backend/src/napms/technical_access_evidence/
    domain/
    application/
    infrastructure/
```

Concrete source/import adapters live at outer integration/composition boundaries. Provider/parser types do not enter TAE Domain/Application.

Dependency direction:

```text
TAE Domain
    ^
    |
TAE Application + TAE-owned ports
    ^
    |
PostgreSQL / source adapters / composition / optional transport
```

TAE core consumes no other NAPMS bounded-context private model. Downstream consumers use explicit published evidence contracts/projections; TAE does not depend on those consumers.

## Source adapter boundary

A source adapter owns:

- source-specific authentication/transport;
- parsing device/controller/traffic/file syntax;
- establishing EvidenceSourceReference, SourceScopeReference and stable SourceCaptureReference;
- mapping source time to `Unknown | Instant | Window`;
- exact normalization into TAE source-neutral draft values;
- mapping source protocol syntax into the accepted protocol/port vocabulary;
- preserving source-native facts as provenance when they have no source-neutral meaning;
- failing normalization when exact representation is impossible.

TAE Domain/Application owns validation of normalized invariants, immutable set/entry identity, capture idempotency/conflict semantics, complete-set persistence outcome and source-neutral query semantics.

A parser failure or unrepresentable source item is not converted into a partial successful capture.

## Application input

`RecordTechnicalAccessEvidenceSet` receives source-neutral evidence, not raw provider payload:

```text
EvidenceSetDraft {
    kind
    source
    sourceScope
    sourceCaptureReference
    evidenceTime
    entries[]
}
```

`recordedAt` is supplied by an application/composition clock. Generated set/entry IDs are TAE identities, not source identities.

## Persistence port

TAE owns its repository abstraction. Required capabilities support:

```text
get_by_id(evidenceSetId)
find_by_capture(source, captureReference)
list(filters, offset, limit)
add(evidenceSet)
commit()
```

Persistence outcomes distinguish execution failure, unknown commit outcome and source+capture uniqueness conflict.

On a uniqueness conflict, Application re-reads the winner and compares the source-qualified capture payload. Equal payload is an idempotent retry preserving original IDs/RecordedAt; different payload is a capture conflict.

Generated IDs, retry time and incidental parser/list order are excluded from retry equality. Duplicate entry multiplicity and factual sourcePosition remain significant.

Concrete SQL and locking remain adapter concerns.

## Query boundary

TAE read models return TAE-owned DTOs/contracts only. Filters may include source, source scope, evidence kind and supported time ranges.

TAE exposes no universal `current`, `fresh`, `effective` or `reconciled` query. Selection/currentness belongs to an explicit downstream source/consumer contract.

## Runtime boundary

TAE does not require a human-facing public endpoint merely because evidence can be recorded. Trusted producer/import composition may call TAE Application directly through an integration boundary.

If an operator-facing transport exists, its authentication and Authority Management admission remain explicit application/transport concerns rather than implicit authorization by possession of source access.

Opening TAE persistence should be scoped to workflows that actually use TAE; unrelated request scopes do not acquire TAE resources by default.

## Architecture guardrails

- no FastAPI, database-driver, provider SDK, parser or runtime-config imports in TAE Domain/Application;
- no cross-BC private domain type reuse merely because technical predicates look similar;
- no desired-policy or APR types inside TAE;
- no hidden Resource/ACC lookup during evidence recording;
- no firewall/target-placement inference in TAE;
- no universal current/fresh winner without an accepted source/consumer contract;
- no generic ingestion/event platform without a concrete current need;
- no partial-success capture when one source item cannot be normalized faithfully.
