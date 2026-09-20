# Backend verification strategy

Status: ACCEPTED candidate

## Purpose

Prove that an implementation realizes accepted product/domain/application/system/interface/data/security/operability knowledge without using implementation structure as semantic truth.

## Verification levels

### V1 — Pure domain behavior

Evidence: deterministic unit/property tests against public domain operations/value contracts.

Objectives:
- Resource/Endpoint identity survives address change; missing address is explicit.
- InteractionRevision is immutable and rejects unsupported/invalid traffic semantics.
- ConnectivityNeed is not permission and retirement preserves historical meaning.
- AccessRequest subject is immutable; DENIED never yields PolicyRule; ALLOWED yields at most one Rule.
- PolicyRule ACTIVE/INACTIVE preserves identity and decision provenance.

### V2 — Application orchestration

Evidence: application contract tests with in-memory/fake public ports whose behavior is controlled by the test, not by peeking into implementation internals.

Objectives:
- SubmitAccessRequest validates current Need, exact InteractionRevision and Deployment direction before commit.
- request admission and permission decision admission are independent.
- decision recording + first Rule creation has one atomic outcome.
- current policy materialization expands owner facts exactly and returns UNRESOLVED when any active Rule lacks required realization.
- independent Rule provenance is never collapsed.

### V3 — Persistence/transaction integration

Evidence: tests against the selected real relational database engine from an empty migrated schema.

Objectives:
- schema constraints implement owner-local invariants without cross-owner write coupling;
- optimistic stale update is rejected;
- same AccessRequest receives at most one final decision/Rule;
- idempotency same-key/same-input replays result; same-key/different-input conflicts;
- failure before commit leaves no partial authoritative state;
- shared validation/write transaction observes one Need state;
- materialization reads one coherent snapshot under concurrent changes;
- Resource address/responsibility history intervals remain valid.

### V4 — HTTP/API contract

Evidence: black-box HTTP tests against a composed backend with controlled identity provider validation and real database.

Objectives:
- every documented operation accepts/returns the documented representation;
- stable status/problem codes distinguish auth, validation, stale conflict, finality, unresolved policy, dependency and internal failure;
- ETag/If-Match and Idempotency-Key behavior is observable;
- policy output is COMPLETE only with complete current facts;
- unsupported protocol-specific traffic is rejected, never approximated.

### V5 — Security

Evidence: black-box authorization matrix tests plus security-focused integration tests.

Objectives:
- invalid/expired/wrong-issuer/wrong-audience token rejected;
- each operation requires exactly its canonical permission class;
- no permission implication exists between request/decide/manage/export;
- Resource responsibility and Process organization data never grant application permission;
- token/secret/internal stack data absent from problem responses and representative logs;
- caller cannot override trusted principal identity;
- parameterized persistence boundary withstands hostile text/input values without query-shape change.

### V6 — Architecture/component structure

Evidence: deterministic source-structure/import dependency checks.

Objectives:
- domain packages do not import api/runtime/postgres/OIDC/telemetry packages;
- API does not import concrete repositories;
- module adapters do not mutate peer schemas;
- Policy Materialization has no write repository;
- transaction coordination is isolated at ConsistencyRunner/composition boundary;
- public peer ports expose owner facts rather than persistence rows.

### V7 — Operability

Evidence: composed-runtime tests with captured logs/metrics and dependency fault injection.

Objectives:
- correlationId appears across one request's diagnostic evidence;
- auth/decision/materialization events contain required safe fields;
- secrets/tokens are redacted;
- liveness does not depend on DB/OIDC;
- readiness fails on unusable DB/config/OIDC key material;
- dependency timeout maps to DEPENDENCY_UNAVAILABLE where required;
- cancelled materialization stops work without fabricating COMPLETE.

### V8 — Migration/fresh-start

Evidence: apply all migrations to empty database, start backend, execute minimum end-to-end journey.

Objective: a clean environment can reach complete policy materialization without manual hidden state injection.

## End-to-end acceptance journey

1. create Site/ResponsibilityGroup/Resource/Endpoint and current address for source and destination;
2. create Application, source/destination Components, directed Interaction and immutable revision;
3. create source/destination ComponentDeployments;
4. create BusinessProcess + current ConnectivityNeed for Interaction;
5. submit AccessRequest with request-only principal;
6. record ALLOWED with distinct decide-only principal;
7. materialize current policy with export-only principal;
8. assert COMPLETE, exact traffic/address expansion and complete provenance.

Negative sibling cases replace step 6 with DENIED, remove required realization before step 7, use wrong-direction deployments, retire Need before submission, use stale ETag, and replay idempotency keys.

## Non-gates

No latency/throughput/HA/RPO/RTO threshold is a correctness gate because no accepted numeric target exists. Such measurements may be diagnostic only.
