# I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation

Status: `active`

Date: 2026-09-09.

## Goal

Complete the first coherent Access Policy Realization (APR) outcome so NAPMS can derive vendor-neutral desired enforcement semantics from effective Access Policy + Network Enforcement Placement and reconcile them against explicitly selected configured evidence without inventing source completeness, policy-scope ownership, currentness, vendor evaluation or device-execution semantics.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/domain/access-policy-realization/tactical-model.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/technical-access-evidence/tactical-model.md`;
- `docs/domain/network-enforcement-placement/tactical-model.md`;
- current Access Policy desired-policy/export behavior;
- current architecture and repository domain-change/decision protocols.

Accepted constraints entering I20:
- APR owns technical↔domain resolution, enforcement-policy derivation and desired-vs-configured reconciliation.
- Access Policy owns desired/authorized Access Rule truth.
- NEP owns forwarding/enforcement placement and never changes meaning for the APR consumer.
- TAE owns immutable source-qualified evidence; evidence is not currentness, completeness, authorization or desired policy by itself.
- I18 correspondence algebra remains consumer-independent and must be reused rather than replaced by a reconciliation-specific matcher.
- I21 owns target/vendor rendering; I22 owns provider/device acquisition/mutation/execution.

## WP-0 — Tactical DDD, scope and architecture closure

Purpose:
resolve the semantic prerequisites that make `Satisfied`, `Add`, `Remove`, `Replace` and `No-op` truthful rather than convenient guesses.

Decisions to establish:
- desired enforcement-policy identity/value shape and the exact relation to Access Rule + NEP placement;
- whether enforcement intent is keyed by Logical Firewall alone or by the concrete Enforcement Attachment/placement occurrence;
- managed reconciliation scope: what proves that desired policy and configured evidence refer to the same policy partition;
- configured evidence eligibility and explicit selection; no implicit latest/current winner;
- source-contract requirements for configured-policy completeness and effective evaluation semantics;
- exact temporal correlation between desired policy, placement and configured evidence;
- treatment of configured `Permit | Block | absent` action when source evaluation semantics are incomplete;
- canonical desired/configured region algebra and exact missing/extra/common witnesses;
- `Add | Remove | Replace | No-op` as semantic delta classification without implying vendor/device operations;
- ambiguity/Unknown precedence and whether known partial witnesses remain explainable;
- reuse of I18 Technical-to-Domain Resolution for configured evidence attribution;
- APR persistence/public workflow disposition for the first slice.

Artifacts:
- I20 APR Tactical DDD extension;
- I20 product requirements + acceptance examples where useful;
- I20 architecture boundary;
- semantic-ownership/ubiquitous-language propagation only where the accepted meaning changes;
- repair stale I19 strategic-model wording discovered during re-entry.

Local exit:
all implementation-blocking I20 semantics are accepted or explicitly deferred with fail-closed behavior and a revisit trigger; no I21 rendering or I22 device mechanics are pulled forward.

## WP-1 — Framework-free derivation and reconciliation core

Purpose:
implement APR-owned source-neutral values and pure deterministic policy algebra.

Required proof:
- exact canonical technical-region union/intersection/difference without broadening/narrowing;
- desired enforcement intent derived only from effective desired policy + complete NEP placement;
- enforcement target identity preserves the accepted placement granularity;
- exact common/missing/extra witnesses;
- deterministic `Add | Remove | Replace | No-op` classification only for complete comparable snapshots;
- Unknown/Ambiguous never downgraded by input ordering or known partial overlap;
- no peer bounded-context/infrastructure imports in APR Domain/Application;
- existing I18 correspondence semantics remain unchanged.

Local exit:
core tests form an executable specification of I20 derivation/reconciliation semantics.

## WP-2 — Owner-preserving adapters and evidence contract

Purpose:
connect the I20 core to authoritative existing owners without cross-context persistence or source-semantic invention.

Expected scope, subject to WP-0:
- APR-owned desired-policy port backed by existing Access Policy + RC/ACC coherent projection;
- APR-owned placement port backed by NEP `SelectEnforcement`;
- explicit configured-evidence selection backed by TAE;
- trusted source/reconciliation-scope contract proving target correlation, managed-scope equivalence, effective configured-policy semantics and completeness where a complete result is claimed;
- I18 Domain Access Resolution reuse for configured-evidence attribution;
- explicit knowledge gaps when a source contract cannot establish those claims.

Local exit:
outer adapters can produce truthful APR-owned desired/configured snapshots while owner contexts remain independent.

## WP-3 — Durable composition and acceptance proof

Purpose:
prove I20 across the existing PostgreSQL-backed owners without creating copied APR business truth.

Required proof:
- effective Access Policy changes alter desired enforcement intent at explicit logical time;
- NEP placement changes move desired intent to the correct enforcement target without changing Access Rule identity;
- a complete configured capture can prove `No-op`, missing-only `Add`, extra-only `Remove` and mixed `Replace`;
- incomplete/uncorrelated/temporally incompatible configured evidence fails closed as Unknown;
- ambiguous configured-domain attribution preserves all competitors and no winner;
- no Access Rule, Connectivity Decision, NEP or TAE mutation side effect;
- no APR persistence unless WP-0 establishes an independent lifecycle/identity need;
- no vendor syntax or provider mutation.

Public HTTP/Web workflow is not required unless WP-0 discovers an accepted product need that cannot be proven otherwise.

Local exit:
the roadmap I20 exit is executable against durable owner data with exact provenance.

## WP-4 — Review, canonical absorption and roadmap promotion

Purpose:
close the semantic stage cleanly.

Required actions:
- architecture review with P0/P1 closed;
- applicable repository checks / final hosted PR gate;
- absorb durable truth into canonical domain/requirements/architecture/engineering documents;
- mark I20 complete and promote I21 Configuration Rendering;
- remove this active plan and return the resume capsule to `Current: none`;
- squash merge the coherent I20 stage.

## Exit criteria

I20 is complete only when:
- desired enforcement semantics have accepted source-neutral Tactical DDD;
- configured evidence can be compared only under an explicit same-target/same-managed-scope contract;
- absence-based claims require trustworthy completeness rather than empty/non-empty inference;
- exact common/missing/extra regions and provenance are preserved;
- `Add | Remove | Replace | No-op` is an exact semantic classification, not a vendor operation recipe;
- ambiguity/Unknown/currentness/temporal limitations fail closed;
- I18 Technical-to-Domain Resolution is reused consistently for configured attribution;
- at least one PostgreSQL-backed end-to-end proof exists over existing owner contexts;
- no I21 rendering or I22 device execution is implemented;
- P0/P1 review findings are closed and canonical current state promotes I21.

## Blockers

WP-0 semantic choices are accepted in the I20 Tactical DDD/requirements/architecture contract. No plan-level blocker remains for WP-1. Source-specific configured evaluation beyond the accepted effective-Permit contract remains fail-closed/deferred rather than blocking the core.

## Next

Execute WP-1: implement framework-free APR desired-enforcement values, exact policy algebra, derivation/reconciliation decisions and executable core/architecture tests from the accepted WP-0 contract.
