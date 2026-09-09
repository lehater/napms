# PLAN-018 — Technical-to-Domain Access Resolution

Status: `active`

Date: 2026-09-09.

## Goal

Implement the first shared **Technical-to-Domain Access Resolution** capability inside **Access Policy Realization (APR)** so one normalized Technical Access Predicate can be interpreted against effective Resource Catalogue + Application Communication Catalogue knowledge with one consumer-independent coverage algebra.

The first useful end-to-end result is:

```text
one source-qualified TAE entry
    -> APR-owned technical predicate projection
    -> effective RC + ACC domain candidate snapshot
    -> shared correspondence/coverage algebra
    -> Domain Access Resolution
       + matched Domain Interactions
       + exact overlap witnesses
       + unresolved technical remainder
       + ambiguity/unknown provenance
```

I19 Network Enforcement Placement and I20 reconciliation/enforcement-policy derivation remain downstream.

## Inputs

- `docs/domain/capabilities.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/ubiquitous-language.md`;
- `docs/domain/technical-access-evidence/tactical-model.md`;
- `docs/requirements/technical-access-evidence-core.md`;
- `docs/architecture/technical-access-evidence-boundary.md`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/process/domain-change-protocol.md`;
- `docs/process/decision-protocol.md`.

## Accepted starting truth

- Technical-to-Domain Access Resolution belongs to Access Policy Realization.
- Proposal-side and Reconciliation-side matching are the same capability.
- The same Technical Access Predicate + same RC/ACC/effective-time knowledge must produce the same Domain Access Resolution independent of consumer.
- TAE owns source-qualified technical evidence and must not acquire domain-interaction meaning.
- Domain Interaction identity is Source Component Deployment + Destination Component Deployment + matching immutable DCS revision.
- RC owns Resource/Endpoint technical realization; ACC owns Component Deployment, DCS and effective DeploymentResourceBinding truth.
- Technical resolution is derived truth: it does not authorize access, create Access Rules, choose enforcement placement or mutate source contexts.

## Work packages

### WP0 — Tactical DDD and observable-contract closure — done

Create/accept together:
- `docs/domain/access-policy-realization/tactical-model.md`;
- `docs/requirements/technical-domain-access-resolution.md`;
- `docs/requirements/technical-domain-access-resolution-acceptance-examples.md`;
- `docs/architecture/access-policy-realization-resolution-boundary.md`.

Resolve explicitly:
- APR Domain Access Resolution result semantics;
- exact pairwise Access Correspondence algebra;
- resolution-level Exact/Covered/Partial/Ambiguous/Unresolved/Unknown semantics;
- effective-time handling;
- unresolved technical remainder representation;
- ambiguity detection across distinct Domain Interactions;
- provenance minimum;
- RC/ACC consumer-owned projection boundary;
- TAE-to-APR adapter boundary;
- protocol/port comparison limits that must fail closed instead of inventing semantics.

Infrastructure gate: closed.

Exit:
no blocking semantic unknown remains for the first resolution core and no I19/I20 meaning is required to implement it.

### WP1 — Domain/Application/Ports core

- add framework-free `access_policy_realization` Domain/Application packages;
- implement normalized region intersection/containment/difference for the accepted first algebra;
- implement one consumer-independent `ResolveTechnicalAccess` use case;
- expose APR-owned source-neutral domain-knowledge port;
- preserve exact overlap witnesses, remainder and provenance;
- add core/architecture tests.

Infrastructure gate remains closed.

Exit:
a supplied complete domain-candidate snapshot can resolve one technical predicate deterministically without peer-context/framework imports in APR Domain/Application.

### WP2 — RC + ACC + TAE outer adapters

After WP1 gate:
- implement the APR domain-knowledge adapter over existing RC + ACC authoritative repositories/application semantics;
- enumerate effective ACC interactions and bindings at `asOf`;
- consume RC endpoint realizations without copying ownership;
- translate only accepted DCS transport semantics to APR source-neutral regions; unsupported/invalid transport meaning becomes explicit Unknown;
- add a TAE projection adapter that maps evidence predicates/provenance into APR input without adding APR dependency to TAE;
- do not add APR persistence, public HTTP/Web, Authority Management workflow, NEP or Access Policy coupling.

Exit:
one durable TAE entry can be projected through current RC/ACC knowledge into the same APR core used by any future consumer.

### WP3 — Integration proof

- prove Exact, Covered, Partial, Ambiguous, Unresolved and Unknown outcomes;
- prove exact unresolved remainder for supported predicates;
- prove effective-time changes can change resolution only through effective RC/ACC knowledge;
- prove competing Domain Interactions create ambiguity rather than arbitrary winner selection;
- prove TAE remains unchanged and no Access Rule/Decision side effect occurs;
- prove unsupported/incomplete RC/ACC technical meaning fails closed.

Exit:
repository integration demonstrates technical evidence -> domain resolution with traceable source + catalogue/resource provenance.

### WP4 — Architecture review and closure

- run P0-P3 architecture review and close all P0/P1 findings;
- run applicable core/harness/knowledge and hosted final PR gates;
- absorb stable I18 outcomes into canonical domain/requirements/architecture/engineering truth;
- mark I18 done and promote I19 as next, not selected;
- clear active execution and remove this PLAN only after final gates.

## Priority risks

### P0

- consumer-specific proposal/reconciliation resolution semantics;
- treating technical evidence or resolution as authorization;
- importing RC/ACC/TAE peer implementation types into APR Domain;
- silently picking one Domain Interaction when technical space is ambiguous;
- dropping unresolved technical remainder;
- inventing protocol/service/port meaning that current ACC/TAE contracts cannot support;
- using I19 placement or I20 reconciliation concepts to make I18 convenient.

### P1

- broadening/narrowing technical regions during normalization or subtraction;
- conflating missing current realization with known no-match;
- losing effective-time or RC/ACC/TAE provenance;
- global Unknown caused by unrelated catalogue records instead of predicate-relevant uncertainty;
- persisting derived Domain Access Resolution without an accepted lifecycle/identity need.

### P2

- premature performance/indexing work before a proven resolution query shape;
- public HTTP/Web surface without an accepted operator use case;
- generic policy-algebra framework beyond the first accepted resolution behavior.

## Exit criteria

1. APR Tactical DDD defines Domain Access Resolution, Access Correspondence, ambiguity, unknown and unresolved remainder.
2. One source-neutral algebra is used regardless of future proposal/reconciliation consumer.
3. Supported technical predicates resolve Exact/Covered/Partial/Unresolved deterministically with exact overlap/remainder witnesses.
4. Distinct Domain Interactions overlapping the same technical fragment produce Ambiguous, never arbitrary winner selection.
5. Incomplete/untranslatable predicate-relevant RC/ACC knowledge produces explicit Unknown.
6. Resolution uses explicit offset-aware `asOf` and preserves input + RC + ACC provenance.
7. APR Domain/Application are framework-free and own their consuming ports.
8. TAE remains an upstream evidence owner; the adapter direction is TAE -> APR projection, never APR meaning inside TAE.
9. No APR persistence, NEP, reconciliation, rendering, device execution or public workflow is introduced.
10. Canonical truth is updated, active execution is cleared, and I19 is promoted only after final gates.

## Blockers

None for WP1.

WP0 review closed with no P0/P1 semantic blockers. The accepted first algebra is intentionally exact-protocol-number scoped; Protocol Any remains explicit Unknown until a protocol-wide port-applicability/difference model is accepted.

## Next

Execute WP1 only: framework-free APR Domain/Application/Ports core plus core/architecture tests. Keep peer-context adapters and infrastructure closed until the WP1 gate passes.
