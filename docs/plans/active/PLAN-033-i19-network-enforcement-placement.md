# I19 — Network Enforcement Placement

Status: `active`

Date: 2026-09-09.

## Goal

Implement the first coherent Network Enforcement Placement (NEP) context so NAPMS can derive and explain where one normalized traffic relation is subject to enforcement at an explicit logical time, without vendor syntax, device execution, configured-policy reconciliation, or I20 policy-derivation semantics.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/domain/strategic-model.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/resource-role-model.md`;
- `docs/domain/ubiquitous-language.md`;
- current architecture and engineering state;
- repository architecture/change protocols.

Accepted constraints:
- NEP owns forwarding/path meaning, Logical Firewall correspondence, Enforcement Selection and Enforcement Attachment semantics.
- Logical Firewall identity is independent from provider/device realization.
- placement relevance is independent from authorization and from whether equivalent policy is configured.
- temporal facts use explicit logical time and fail closed on material uncertainty.
- I20 desired-vs-configured reconciliation and enforcement-policy derivation remain out of scope.

## WP-0 — Tactical DDD and architecture closure

Purpose:
turn the strategic NEP vocabulary into an executable semantic contract before implementation.

Decisions to establish:
- normalized Traffic Relation / forwarding-path query identity versus ephemeral query value;
- Path Knowledge fact identity, provenance, temporal validity and completeness;
- Logical Firewall identity/lifecycle;
- provider-realization correspondence semantics and temporal cardinality;
- Enforcement Attachment identity and what exactly it attaches to;
- Enforcement Selection result/status, multiplicity and ordering;
- ambiguity/unknown/no-placement semantics;
- correction/supersession semantics for observed path/provider facts;
- consumer-owned ports and dependency direction.

Artifacts:
- NEP Tactical DDD + ubiquitous-language/semantic-ownership propagation where required;
- NEP product requirements;
- NEP architecture boundary;
- repair stale current-architecture I18/I19 status while touching the canonical architecture surface.

Local exit:
all implementation-blocking semantic choices are accepted or explicitly deferred with a non-blocking revisit trigger; no I20 semantics are pulled forward.

## WP-1 — Framework-free core

Purpose:
implement NEP Domain/Application/Ports from the accepted WP-0 contract.

Required proof:
- pure domain invariants and selection semantics;
- explicit `asOf`;
- fail-closed missing/ambiguous path/correspondence/attachment knowledge;
- Logical Firewall/provider identity separation;
- deterministic result independent of input iteration order;
- no peer bounded-context or infrastructure imports in Domain/Application.

Local exit:
core tests and architecture tests define an executable specification of placement.

## WP-2 — Durable knowledge and adapters

Purpose:
provide one minimal durable NEP-owned knowledge path sufficient to prove the context beyond in-memory examples.

Expected scope, subject to WP-0:
- NEP-owned PostgreSQL persistence/migrations for selected authoritative/recorded NEP facts;
- strict local/import adapter for path/firewall/attachment knowledge if a source adapter is needed;
- temporal reads and provenance preservation;
- no direct peer-table access.

Local exit:
durable record/readback and placement selection work across PostgreSQL without changing provider/device identity into Logical Firewall identity.

## WP-3 — Composition and acceptance proof

Purpose:
prove the I19 exit in one bounded composition.

Required proof:
- one domain-meaningful traffic relation can be projected into an NEP-owned query;
- NEP returns explainable enforcement placement(s) with Logical Firewall + attachment/path provenance;
- effective-time changes alter results truthfully;
- conflicting relevant knowledge fails closed;
- no Access Rule, Connectivity Decision, TAE or APR side effects;
- no vendor configuration rendering or execution.

Public HTTP/Web workflow is not required unless WP-0 discovers an accepted product need that cannot be proven otherwise.

Local exit:
the roadmap I19 exit is executable and durable.

## WP-4 — Review, canonical absorption and roadmap promotion

Purpose:
close the semantic stage cleanly.

Required actions:
- architecture review with P0/P1 closed;
- applicable repository checks / final hosted PR gate;
- absorb durable truth into canonical domain/requirements/architecture/engineering documents;
- mark I19 complete and promote I20;
- remove this active plan and return the resume capsule to `Current: none`;
- squash merge the coherent I19 stage.

## Exit criteria

I19 is complete only when:
- normalized path/forwarding knowledge, Logical Firewall correspondence, Enforcement Attachment and Enforcement Selection have accepted executable semantics;
- Logical Firewall/provider realization identities remain explicitly independent;
- NAPMS can derive/explain enforcement placement for one normalized/domain-attributable traffic relation at explicit `asOf`;
- unknown/ambiguity/no-placement claims are evidence-safe and fail closed;
- at least one durable PostgreSQL-backed proof exists;
- core dependency and persistence ownership boundaries are tested;
- I20 reconciliation/policy derivation, I21 rendering and I22 execution are absent;
- P0/P1 review findings are closed and canonical current state promotes I20.

## Blockers

WP-0 and WP-1 are accepted/implemented. WP-2 durable capture/import persistence is implemented and architecture-hardened. WP-3 composition proof is implemented; hosted PostgreSQL validation remains part of the final WP-4 gate.

## Next

Execute WP-4: run architecture review, close P0/P1, promote the PR to Ready for the hosted core/PostgreSQL/knowledge gates, then absorb I19 and promote I20 only after green validation.
