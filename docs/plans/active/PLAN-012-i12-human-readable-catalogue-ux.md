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

**WP7–WP8 — PostgreSQL/runtime/Docker evidence.**

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

1. **DONE — Display metadata model/migration.** Optional Component Deployment/DCS display names, validation, tracked PostgreSQL migration and local-demo names are implemented.
2. **DONE — Catalogue presentation use case.** Exact-identity batch descriptions preserve order and fail soft on missing labels while requiring exact DCS subject correlation.
3. **DONE — Proposal interaction search.** Bounded server-side search is wired through the existing authority-first proposal use case.
4. **DONE — Rule/API enrichment.** Already-authorized proposal/Rule/Effective Policy responses carry optional presentation descriptors.
5. **DONE — Normalized-policy enrichment.** Authorized normalized rows carry catalogue labels without changing technical/provenance semantics.
6. **DONE — Web UX.** Compose is searchable/label-first; Rules/Details/Policy views show names first and stable IDs second.
7. **ACTIVE — PostgreSQL/runtime evidence.** Migration/search/fallback/authorization behavior is covered and being gated.
8. **ACTIVE — Docker demo evidence.** Local seed and public smoke assert labels/traffic summary.
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

Run core/PostgreSQL/Web/Docker evidence, close P0/P1 findings, then absorb I12 into canonical current state.
