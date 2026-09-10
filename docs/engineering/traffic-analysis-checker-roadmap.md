# Traffic Analysis Checker Roadmap

Status: `I26 complete and absorbed for the supported local target`.

Date: 2026-09-10.

## Purpose

Provide the ordered implementation path for the technical-entry-point analysis code-named **Checker**.

The accepted observable behavior is owned by `docs/requirements/traffic-analysis-checker.md`.

Checker was intentionally implemented UI-first, with backend seams introduced only where current owner APIs/read models were insufficient.

## Ordered roadmap

### C0 — Semantic re-entry and contract correction — complete

The I19 ordered `ForwardingPath` capability remains a stronger optional contract only when a source can prove traversal/order. Baseline Checker Network Context is a possibly incomplete unordered candidate set with potential false positives, explicit provenance, source relevance and knowledge gaps.

### C1 — Checker Web skeleton on deterministic fixtures — complete

A dedicated Checker workspace was created with source/destination/protocol/port/as-of inputs and Overview, Network Context, Policy, Ownership and Evidence tabs. Fixtures were used only for UI-first construction; the product read path now uses the real API.

### C2 — Checker application/read contract — complete

`TrafficAnalysisQuery` / `TrafficAnalysisResult`, owner-preserving consuming ports and authenticated HTTP transport were implemented with no independent Checker persistence.

### C3 — Technical address to domain resolution — complete

Resource Catalogue reverse address resolution plus Application Communication Catalogue bindings provide `IP -> Endpoint -> Resource -> Component` projections while preserving resolved, ambiguous, historical and unknown outcomes.

### C4 — Policy/governance composition — complete

Checker reuses owner-preserving scoped connectivity composition for Connectivity Requirement, Connectivity Decision, Access Rule and Effective Policy summaries. Multiple/partial/unknown results remain explicit.

### C5 — Network Context candidate integration — complete

Checker consumes unordered relevant enforcement/device candidates without inventing a path or sequence. Candidate provenance, source relevance and knowledge gaps are exposed.

### C6 — Per-candidate Technical Access Evidence correlation — complete

For every candidate, Checker reads the latest applicable stored `Configured` Technical Access Evidence snapshot for `asOf`, exposes capture/record/source/provenance and correlates matching technical entries. No synchronous live device read is performed.

### C7 — Shared traffic-predicate matching semantics — complete

Backend matching distinguishes exact, candidate-covers-query, query-covers-candidate, partial overlap and no-match semantics across supported addresses/protocol/ports. Web renders backend results and does not own duplicate set algebra.

### C8 — Resource ownership/contact capability — complete for local target

Resource Catalogue owns a temporal Resource Responsibility model supporting person/team references and service owner, technical owner, operations/support and business owner roles. Responsibility/contact remains distinct from Authority Management action authority. The selected local runtime uses deterministic local responsibility data.

### C9 — Full Checker integration and acceptance — complete

The real `/api/v1/traffic-analysis` composition is wired into the local runtime and Web UI. Local deterministic data exercise several Network Context candidates, stored evidence snapshots, a missing-evidence candidate and ownership/contact discovery.

### C10 — Role-oriented presentation refinement — deferred

No additional role-specific truth models or hard-coded job-title semantics are required for I26 completion. Future presentation refinement may use the same projection and capability/visibility rules when a concrete usability requirement appears.

## Implemented dependency sequence

```text
C0 semantic correction
  -> C1 UI fixtures
  -> C2 read contract
  -> C3 domain resolution
  -> C4 policy composition
  -> C5 network candidates
  -> C6 evidence-backed rules
  -> C7 predicate matching
  -> C8 ownership/contacts
  -> C9 integration/acceptance
```

## Accepted implementation constraints

- Local-first remains the selected target.
- Deterministic stubs are preferred over speculative provider/enterprise integrations.
- No real lab or live device transport is required.
- Checker is evidence-driven, not device-driven.
- Technical Access Evidence is never authorization truth.
- Network Context uncertainty remains visible to the user.
- `ForwardingPath` must not be used as a synonym for baseline Network Context candidate enumeration.

## Completion evidence

The pre-absorption I26 head passed:
- core gate;
- harness gate;
- knowledge gate;
- web gate;
- PostgreSQL persistence gate;
- Docker local runtime gate, including fresh authenticated product execution, preserved-volume restart with rotated database credential, logical backup/clean restore, migration replay no-op and operator status diagnostics.

Canonical current product state is summarized by `docs/engineering/current-state.md` and `docs/architecture/current-architecture.md`.
