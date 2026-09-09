# Access Policy Realization Reconciliation Requirements — I20

Status: `accepted I20 WP-0 behavioral baseline`.

Date: 2026-09-09.

## Purpose

Define observable behavior for vendor-neutral desired enforcement derivation and desired-vs-configured reconciliation inside Access Policy Realization.

## REQ-APR-REC-001 — Keep I20 inside APR

Access Policy Realization shall own desired enforcement-policy derivation, configured-policy reconciliation and exact semantic delta.

I20 shall not create a new Bounded Context merely because new result types/adapters are required.

## REQ-APR-REC-002 — Use one explicit logical time

One complete I20 evaluation shall use one offset-aware `asOf` for desired policy, RC/ACC interpretation and NEP placement.

The first complete configured comparison shall require selected TAE `Configured` evidence with `EvidenceTime = Instant(asOf)`.

`RecordedAt`, latest/nearest capture or wall-clock now shall not substitute for that fact.

## REQ-APR-REC-003 — Derive desired policy only from effective authorized Rules

Desired Enforcement Intent shall originate only from a coherent effective Access Policy selection for the requested governance scope at `asOf`.

Inactive, out-of-window or different-scope Rules shall not contribute desired enforcement regions.

## REQ-APR-REC-004 — Preserve exact domain correctness

APR shall use the shared I18 Technical-to-Domain Access Resolution semantics to validate desired technical fragments.

A desired technical fragment shall not be called business-correct when it necessarily permits a Domain Interaction that is not represented by the effective desired Rule set.

If all competing Domain Interactions for the fragment are desired, APR may merge technical intent while preserving all Rule/domain provenance.

Predicate-relevant Unknown or unexplained desired technical remainder shall fail closed.

## REQ-APR-REC-005 — Preserve Enforcement Attachment granularity

The first Enforcement Target shall be identified by Logical Firewall + Enforcement Attachment.

APR shall not collapse distinct Enforcement Attachments merely because they share one Logical Firewall/provider.

Provider/path/traversal references remain provenance rather than target identity.

## REQ-APR-REC-006 — Preserve complete NEP outcomes

Desired derivation shall consume NEP placement through an APR-owned projection/port at the same `asOf`.

`Placed`, `NoEnforcement`, `NoForwardingPath`, `Ambiguous` and `Unknown` shall not be reinterpreted as one another.

Ambiguous/Unknown placement shall not select a winner or guessed target.

## REQ-APR-REC-007 — Require explicit managed-scope correlation

A complete reconciliation shall require an explicit trusted contract correlating:
- one Access Policy governance scope;
- one Enforcement Target;
- one TAE source/scope representing the same configured policy partition.

Matching strings, same device/firewall name or provider identifiers shall not establish that equivalence.

Without trustworthy correlation, result shall be `Unknown`.

## REQ-APR-REC-008 — Require effective configured-policy semantics

APR shall compare desired Permit regions with source-neutral **effective configured Permit regions**, not arbitrary raw firewall entries.

A source whose Block/order/default/zone semantics affect effective permission shall normalize those semantics in a source-specific outer adapter before APR can claim a complete configured snapshot.

Unsupported evaluation semantics shall produce `Unknown`.

## REQ-APR-REC-009 — Require configured completeness for complete delta

`Satisfied`, `Add`, `Remove`, `Replace` and complete `No-op` shall require configured capture completeness for the exact Managed Reconciliation Scope.

TAE Source Scope, non-empty/empty entries, or Evidence Kind alone shall not imply completeness.

An empty capture may prove zero configured permit regions only when the explicit consumer/source contract establishes complete effective-policy coverage.

## REQ-APR-REC-010 — Select evidence explicitly

I20 shall not automatically choose the latest/current TAE Evidence Set.

The first slice shall reconcile one explicitly selected Evidence Set/capture.

A later selection/currentness policy requires an accepted source/consumer contract.

## REQ-APR-REC-011 — Reuse I18 configured attribution

Each configured effective Permit predicate shall use the existing I18 resolution semantics at the same `asOf`.

No reconciliation-specific technical-to-domain matcher may produce different correspondence, ambiguity or remainder meaning.

I18 Unknown shall make complete reconciliation Unknown. Relevant I18 ambiguity shall make reconciliation Ambiguous with no winner.

## REQ-APR-REC-012 — Compute exact common/missing/extra regions

For one complete comparable scope, APR shall compute:

```text
common  = desired ∩ configured
missing = desired - configured
extra   = configured - desired
```

The product shall preserve exact canonical witnesses and shall not broaden/narrow technical space.

## REQ-APR-REC-013 — Classify complete reconciliation

Policy Reconciliation status shall be:
- `Satisfied`;
- `Drift`;
- `Ambiguous`;
- `Unknown`.

Unknown shall take precedence over Ambiguous; both shall take precedence over a confident Satisfied/Drift claim.

## REQ-APR-REC-014 — Classify Required Semantic Change exactly

For a complete non-ambiguous scope:
- no missing and no extra -> `No-op`;
- missing only -> `Add`;
- extra only -> `Remove`;
- both missing and extra -> `Replace`.

The exact missing/extra witnesses shall remain authoritative.

`Replace` is semantic delta, not a promise of one vendor/device replace operation.

## REQ-APR-REC-015 — Preserve provenance

A complete or degraded result shall preserve attributable references sufficient to explain:
- Access Rule/Rule Semantic Identity and desired-policy snapshot;
- RC/ACC facts used for technical meaning;
- NEP Logical Firewall/Enforcement Attachment and placement provenance;
- selected TAE Evidence Set/source/scope/capture/evidence time;
- configured source/scope/completeness/evaluation contract;
- I18 correspondences/ambiguities/remainders;
- exact common/missing/extra witnesses;
- `asOf`.

## REQ-APR-REC-016 — Keep derived truth non-persistent by default

I20 shall not require an APR table/repository/current-result lifecycle.

Desired Enforcement Policy and Policy Reconciliation are derived on demand unless a later accepted product/runtime requirement establishes independent identity/lifecycle/persistence.

## REQ-APR-REC-017 — Keep rendering/execution downstream

I20 shall not determine:
- vendor syntax/object/grouping/order;
- provider-native rule identity;
- device mutation commands;
- retry/rollback/idempotency of execution;
- post-change verification.

Those concerns remain I21/I22 scope.

## Trace

Tactical semantics:
- `docs/domain/access-policy-realization/reconciliation-tactical-model.md`.

Executable examples:
- `docs/requirements/access-policy-realization-reconciliation-acceptance-examples.md`.

Architecture:
- `docs/architecture/access-policy-realization-reconciliation-boundary.md`.
