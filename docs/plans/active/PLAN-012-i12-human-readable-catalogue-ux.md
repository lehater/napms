# PLAN-012 — I12 Human-readable Catalogue UX

Status: `active`

## Goal

Remove UUID-centric presentation from the existing operator journeys while preserving UUID-based domain identity and existing authorization boundaries.

Primary outcomes:

```text
Compose Connectivity
  -> searchable human-readable source/destination/DCS choices

Access Rules / Rule Details
  -> display names first, stable IDs second

Effective / Normalized Policy
  -> human-readable catalogue context without changing policy semantics
```

## Current stage

**WP1 — catalogue display metadata and authorized presentation read model.**

## Accepted constraints

- Component Deployment UUID and DCS revision UUID remain authoritative identities;
- `displayName` is optional presentation/read metadata and is never part of RuleSemanticIdentity;
- labels do not change proposal, decision, Rule, effective-policy or normalized-policy semantics;
- no generic unauthorised catalogue browsing endpoint is introduced;
- catalogue labels are attached only after the enclosing proposal/rule/policy use case has already been authorized;
- missing labels fall back to stable technical IDs; missing presentation metadata never changes authorization or Rule validity;
- DCS protocol/service/port presentation is derived from the existing immutable DCS projection codec, not duplicated business fields;
- proposal interaction search is server-side because the catalogue may be unbounded;
- no catalogue CRUD/admin workflow is introduced in I12.

## Work packages

1. **ACTIVE — Display metadata model/migration.** Add optional display names to Component Deployment and DCS revision, PostgreSQL migration and local-demo names.
2. **Catalogue presentation use case.** Add batch description of exact Directed Interaction identities with no generic visibility semantics.
3. **Proposal interaction search.** Add server-side search over authorized directed interactions and return labels + decoded traffic summaries.
4. **Rule/API enrichment.** Add presentation descriptors to already-authorized Rule list/details and Effective Desired Policy responses.
5. **Normalized-policy enrichment.** Add catalogue labels to already-authorized normalized rows without changing normalized traffic/provenance semantics.
6. **Web UX.** Compose search + readable choices; Rules/Details/Policy views render name first and stable ID second.
7. **PostgreSQL/runtime evidence.** Prove migration, search, fallback behavior and authorization-before-enrichment.
8. **Docker demo evidence.** Update local seed and full-stack smoke to assert human-readable catalogue metadata is available.
9. **Final review/gates.** Run core, PostgreSQL, Web, Docker, harness and knowledge gates; close all P0/P1.

## Exit criteria

- normal local demo UI no longer requires interpreting UUIDs to compose connectivity;
- proposal search is server-side and bounded;
- Rule/policy screens show labels without changing identity/provenance;
- authorized responses can fall back safely when labels are absent;
- no catalogue label endpoint can reveal unrelated catalogue entities;
- migration and local seed are repeatable;
- all repository gates green;
- no open P0/P1 finding.

## Blockers

No current owner/product blocker.

## Next

Add display metadata migration/domain fields and the exact-identity catalogue presentation read model before changing HTTP/Web DTOs.
