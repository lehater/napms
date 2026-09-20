# Coding-Agent Challenge 14 — post-requirements revalidation PASS

Status: PASS
Blocking P0/P1 findings: none

Canonical requirements baseline:
- napms/main commit: 9200f301ea3c179d2bedef83c1fb0f298e622337
- docs/requirements/first-mvp-product-requirements.yaml
- 42 ACCEPTED requirements

Revalidated design lineage:
- original frozen blind snapshot: ac6c2e1c17b50a62abd3320c4e4cb6cbbaf129ba
- post-freeze repair branch: research/blind-revalidation-repairs-v1

## Repaired findings

### RV-001 — scoped/time request and export authority — CLOSED
- Resource owns immutable AuthorityScopeRef affiliation.
- access.request is a scoped/time AuthorityGrant checked for every distinct source/destination Resource scope at database-owned admissionAt.
- policy.export is a scoped/time AuthorityGrant checked for every distinct selected Resource scope at materialization evaluationAt.
- Site, Resource responsibility, Process organization/criticality and Need existence never manufacture authority.

### RV-002 — authority provenance — CLOSED
- AccessRequest stores immutable RequestAuthorityEvidence for every admitted scope.
- AuthorizationEvidence projects request actor, request time and exact authority scope/bounds/evaluatedAt.
- materialization emits ExportAuthorityEvidence for every selected scope using the same evaluationAt used for policy effectiveness.

### RV-003 — Resource multi-endpoint grouping — CLOSED
- Resource is explicitly the logical access-management unit.
- adding an Endpoint is an explicit caller assertion of membership in that unit.
- no domain/application/data layer auto-groups or moves Endpoints by address, Site, owner, administrator or naming similarity.

### RV-004 — Business Process criticality — CLOSED
- BusinessProcess carries optional mutable criticalityLabel.
- value is opaque trimmed non-empty descriptive text.
- no score, ordering, taxonomy, authority or propagation semantics are invented.

### RV-005 — numeric quality target semantics — CLOSED
- latency/throughput/availability/scale numeric targets are explicitly NOT_REQUIRED for first MVP.
- absence is intentional product truth, not unknown/deferred.
- future targets require new accepted input.

## Consumer challenge

An IMPLEMENTATION consumer no longer needs to decide:
- how request/export scope is derived;
- what time governs authority;
- how authority evidence is represented/preserved;
- whether Site/Owner/Process metadata grants authority;
- how Resource endpoint grouping is inferred;
- whether/how criticality is represented;
- whether numeric MVP SLOs are unknown or intentionally absent.

Remaining choices are local implementation freedoms already enumerated by Implementation Design.

## Result

All 42 canonical first-MVP requirements have an explicit satisfied design disposition.
No blocking Product/Domain/Security/Interface/Data/Verification decision remains from the revalidation findings.

IMPLEMENTATION semantic closure is restored subject to structural Harness/CI validation.
