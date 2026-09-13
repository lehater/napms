# PLAN — Access Policy Realization target design

Status: `active / D1 cross-context contracts`.

Date: 2026-09-13.

## Goal

Advance Access Policy Realization from the accepted problem framing to a locked target Tactical DDD without changing runtime implementation prematurely.

Canonical framing:

- `docs/domain/access-policy-realization/README.md`.

Durable ordered sequence:

- `docs/engineering/access-policy-realization-design-roadmap.md`.

Parent model review:

- `docs/plans/active/domain-erd-revalidation.md`.

## Current stage

Selected stage: **D1 — Lock cross-context inputs and outputs**.

Implementation gate: **closed**.

No APR runtime code, persistence migration, renderer rewrite, Network Operator View rewrite or UI migration is authorized by this plan stage.

## Accepted starting facts

Treat the following as fixed unless the decision protocol explicitly reopens them:

- APR is a separate bounded context;
- target selection/relevance/path reasoning is upstream;
- APR compares target-specific required effective policy with comparable configured effective policy;
- equality is semantic effective-access equality, not raw rule/configuration equality;
- realization assessment, semantic delta and policy change design are separate concerns;
- proposed changes require semantic pre-execution verification;
- rendering is downstream of semantic design/verification and operational mutation remains NEO;
- very large policy sets must be computable data-locally without mandatory full application-memory materialization;
- peer-private persistence is not a cross-context integration contract;
- current APR runtime types are migration evidence only, not target truth.

## D1 trigger

The APR problem statement deliberately leaves final input contracts open. Before effective-access algebra, engine design or Tactical DDD can be locked, the repository must define what one comparison actually references and which owner guarantees each part of that input.

## D1 questions to resolve

### 1. Comparison key

Determine the minimum opaque correlation APR needs to identify one comparable policy unit:

- target reference;
- policy/ACL/subpolicy locator if required;
- comparison scope/partition;
- any stable snapshot/revision key needed to ensure the two sides address the same unit.

Do not import NEP candidate/path/relevance semantics into this key.

### 2. Required effective-policy publication

Determine:

- which owner/application composition publishes target-specific required effective policy;
- how Access Policy, ACC/RC realization facts and upstream target assignment are correlated without moving their authority into APR;
- snapshot/reference identity;
- effective/logical time semantics;
- completeness meaning;
- provenance required to trace the required side back to authoritative owner facts;
- whether the payload is row-oriented, reference-oriented or another published data-local projection.

### 3. Configured effective-policy publication

Determine:

- which owner publishes configured effective policy for the same comparison key;
- exact relationship to TAE evidence/source scope/capture;
- snapshot/reference identity;
- evidence/effective-time semantics;
- explicit completeness contract;
- provenance and unsupported/unknown behavior.

### 4. Normalization ownership

Determine where provider-specific semantics become comparable source-neutral effective access:

- ordered ACL behavior;
- Permit/Block/default behavior;
- nested provider objects/groups;
- service/protocol aliases;
- policy attachment/subpolicy scope;
- NAT-dependent semantics where relevant.

APR must not compare raw rows as if they were effective access. The owner and contract for this conversion must be explicit before D2.

### 5. Data-local publication boundary

Determine how APR can execute close to data while preserving bounded-context ownership:

- owner-published projection/view/table/API contract;
- consistency/snapshot semantics;
- rebuild/freshness rules for derived projections where applicable;
- explicit prohibition on peer-private table dependency;
- no cross-schema FK that creates a hidden shared aggregate.

### 6. APR output references needed by later stages

Define only the output shape necessary to support later design stages without prematurely fixing aggregates:

- realization-assessment reference/metadata;
- semantic-delta reference/access contract;
- provenance to required/configured snapshots and comparison key.

Do not design D4 change operations or D6 renderer contracts in D1.

## Work order

1. Inspect the smallest current canonical owner contracts for Access Policy, ACC, Resource Catalogue, NEP and TAE that participate in the APR handoff.
2. Build one boundary/ownership table for the required side, configured side and target correlation.
3. Classify each unresolved item as factual, semantic or To-Be choice using `docs/process/decision-protocol.md`.
4. Resolve the comparison key and required-policy publication contract.
5. Resolve the configured-policy/completeness contract.
6. Resolve provider-specific effective-policy normalization ownership.
7. Resolve the published/data-local integration boundary.
8. Update the highest canonical owner first for every accepted decision.
9. Add APR requirements/architecture/ADR artifacts only where the decision belongs at those layers; avoid duplicating the domain statement.
10. Refresh this plan/resume capsule with the D1 result and select D2 only after the D1 gate passes.

## D1 required deliverables

Before selecting D2, the repository must contain:

- exact APR comparison-key contract;
- required effective-policy input contract;
- configured effective-policy input contract;
- explicit configured completeness semantics;
- time/snapshot semantics for both sides;
- normalization ownership decision;
- cross-context publication/data-local integration decision;
- provenance requirements;
- conceptual APR assessment/delta reference outputs sufficient for subsequent stages;
- explicit unresolved/non-blocking deferrals with revisit triggers, if any.

The accepted contracts must live in their correct canonical owner documents, not only in this active plan.

## D1 exit gate

D1 passes only if one APR comparison can be described unambiguously as:

```text
comparison key
+ required effective-policy snapshot/reference
+ configured effective-policy snapshot/reference
+ same-scope/comparability guarantee
+ explicit configured completeness
+ time semantics
+ provenance
```

and APR can interpret those inputs without asking why NEP selected the target.

If any of these remains materially undefined, D2 stays blocked.

## Validation for this stage

This is a domain/requirements/architecture design stage.

Required validation before declaring D1 complete:

- check canonical cross-context consistency manually against the affected owner docs;
- run `make knowledge-check` when repository execution is available;
- run `make harness-check` if active-plan/routing/harness invariants are changed beyond ordinary plan content;
- no claim that runtime tests validate target semantics before implementation begins.

## Out of scope until later roadmap stages

Do not solve these in D1 unless they block the input contract:

- final technical-region algebra;
- final realization status names;
- PostgreSQL range/index schema;
- BDD/FDD/atomic-predicate adoption;
- change-operation vocabulary;
- proposed-policy simulation mechanics;
- renderer input mode;
- APR canonical ERD/aggregate decision;
- runtime migration patches;
- public API/UI redesign.

## Next stage

After the D1 exit gate passes, select **D2 — effective-access-space semantics and assessment rules** from `docs/engineering/access-policy-realization-design-roadmap.md` and replace the current active stage accordingly.
