# Technical Access Evidence architecture boundary — I17

Status: `accepted I17 WP0 architecture contract`.

Date: 2026-09-09.

## Purpose

Define the first module/dependency boundary for Technical Access Evidence while keeping source/provider parsing outside domain meaning and preventing I18-I20 semantics from leaking into I17.

## Module boundary

Target core layout:

```text
backend/src/napms/technical_access_evidence/
    domain/
        model.py
    application/
        ports.py
        record.py
        read.py
    adapters/
        postgres/
```

Concrete source/import adapters may live under outer adapter/composition packages. Their parser/provider types do not enter TAE Domain/Application.

Dependency direction:

```text
TAE Domain
    ^
    |
TAE Application + TAE-owned ports
    ^
    |
PostgreSQL / source adapters / composition / optional runtime transport
```

## Cross-context dependencies

I17 TAE core consumes no other NAPMS bounded context.

In particular it does not import:
- Access Policy;
- Connectivity Decision;
- Connectivity Requirements;
- Resource Catalogue;
- Application Communication Catalogue;
- Authority Management;
- Network Enforcement Placement;
- Access Policy Realization.

Future I18 Access Policy Realization consumes TAE through its own consumer projection/port. TAE does not depend outward on the consumer.

## Source adapter boundary

A source adapter is responsible for:
- source-specific authentication/transport when applicable;
- parsing device/controller/traffic/file syntax;
- establishing EvidenceSourceReference;
- establishing SourceScopeReference;
- establishing stable SourceCaptureReference;
- mapping source time to Unknown/Instant/Window;
- exact normalization into TAE source-neutral draft values;
- mapping source protocol syntax to `Any | IpProtocolNumber(0..255)`;
- using protocol `Any` only with source/destination ports `Any`;
- expanding all-protocol + constrained-port syntax into exact protocol-specific entries when source semantics permit, otherwise failing normalization;
- preserving source-native service/object names as provenance when they have no accepted source-neutral meaning;
- preserving a traceable source/provenance reference.

TAE Domain/Application is responsible for:
- validating normalized invariants;
- immutable set/entry identity;
- capture idempotency/conflict semantics;
- atomic complete-set persistence outcome;
- source-neutral query semantics.

A parser failure or unrepresentable source item is not converted into a partial successful set.

## Application input

`RecordTechnicalAccessEvidenceSet` receives a source-neutral draft, not raw provider payload:

```text
EvidenceSetDraft
    kind
    source
    sourceScope
    sourceCaptureReference
    evidenceTime
    entries[]
```

`recordedAt` is supplied by an application/composition clock.

Generated Evidence Set/Entry IDs are application/domain construction inputs, not source identities.

## Persistence port

TAE owns its repository abstraction.

Minimum capabilities:

```text
get_by_id(evidenceSetId)
find_by_capture(source, captureReference)
list(filters, offset, limit)
add(evidenceSet)
commit()
```

Persistence failures distinguish:
- execution failure where success is not established;
- commit outcome unknown;
- source+capture uniqueness conflict.

On a uniqueness conflict, application re-reads the winner and compares only the source-qualified capture payload:
- kind + source scope + Evidence Time + multiset of normalized source entry facts equal -> idempotent existing result preserving original IDs/RecordedAt;
- payload differs -> capture conflict.

Generated IDs, retry-attempt recording time and incidental parser/list order are not part of retry equality. Duplicate multiplicity and factual sourcePosition remain significant.

Exact SQL/locking mechanics remain adapter choices.

## Query boundary

First read model returns TAE-owned DTOs only.

Filters may include source, source scope, evidence kind and time ranges.

There is no repository/application operation named `current`, `fresh`, `effective` or `reconciled` in I17.

## Runtime boundary

I17 does not require a public human HTTP endpoint.

The first end-to-end proof may use:
- a trusted local/import source adapter;
- application composition;
- PostgreSQL persistence/readback.

The implemented I17 proof uses a dedicated `open_technical_access_evidence_scope`. It opens TAE persistence only when the evidence path is invoked; the general HTTP/greenfield request scope does not open an otherwise-unused TAE database connection.

If a public/operator transport is introduced later in I17, it must first add an accepted authority/workflow contract rather than treating authentication as authorization.

## Architecture guardrails

- no TAE Domain/Application import of FastAPI, psycopg, provider SDKs, file parsers or runtime config;
- no cross-BC domain type reuse merely because a predicate looks similar;
- no import of Policy Export `NormalizedPolicyRow` or its desired-policy types;
- shared low-level value semantics may be duplicated locally until a real stable shared kernel is justified;
- no hidden Resource/ACC lookup during evidence recording;
- no Logical Firewall/device-placement inference in TAE;
- no current/fresh winner selection without accepted freshness semantics;
- no generic event bus/ingestion platform before a concrete consumer requires it.

## Implementation gate

WP1 may begin only after the proposed Tactical DDD, behavioral requirements/examples and this architecture boundary are accepted together.

The first core implementation must prove the boundary with architecture tests before PostgreSQL/source-adapter expansion.
