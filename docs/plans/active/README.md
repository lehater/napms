# Active execution

Current: `domain-erd-revalidation.md`

Goal: regroup accepted capabilities into coherent Bounded Contexts and contracts without preserving superseded Connectivity Requirements / Connectivity Decision boundaries merely because they existed previously.

Current task: start S2 from the revalidated G1 contracts and determine semantic ownership/context boundaries for Business Connectivity, Access Governance, Authority Management, Access Policy, catalogue truth and realization/reconciliation.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Lifecycle basis: breadth-first capability `G1 PASS` on branch `docs/g1-capability-revalidation-review`. Current accepted S1 owners are `business-connectivity-g1.md`, `access-governance-g1.md`, `access-policy-core.md`, `application-catalogue-domain-target.md`, `policy-realization-reconciliation-g1.md` and the revalidated `scoped-connectivity-inventory.md`. The 2026-09-14 stakeholder checkpoint remains source evidence. Legacy CR/CD/I14 packets and current runtime/API behavior do not override these requirements.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/requirements/business-connectivity-g1.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/application-catalogue-domain-target.md`
- `docs/requirements/policy-realization-reconciliation-g1.md`
- `docs/requirements/scoped-connectivity-inventory.md`
- `docs/engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`
- `docs/process/domain-design-stage.md`

Then inspect the current Strategic DDD/capability/context-map artifacts only as `DIRTY` downstream models to be revalidated, not as constraints that can override G1.

## G1 closure

Breadth-first capability G1 is accepted for the current scope.

Resolved P1 requirement conflicts:

1. **Access Policy single Decision dependency** — `docs/requirements/access-policy-core.md` now consumes bilateral authorization grant/withdrawal semantics rather than one global `Allowed | NotAllowed` Decision.
2. **ComponentDeployment Resource cardinality** — `docs/requirements/application-catalogue-domain-target.md` now requires exactly one Resource per ComponentDeployment for MVP; Resource movement creates a different concrete deployment subject.
3. **Scoped Connectivity legacy orchestration** — `docs/requirements/scoped-connectivity-inventory.md` and examples now compose Need, bilateral Access Governance, Policy Rule authorization and realization rather than `Requirement -> Proposal -> Decision -> Rule`.
4. **Requirements routing ambiguity** — `docs/requirements/README.md` now distinguishes current target owners from legacy/dirty packets.

No blocking S1 stakeholder unknown remains for entering Strategic DDD. Remaining unknowns are S2/later choices and are preserved in the capability checkpoint.

## Downstream DIRTY artifacts

At least the following must be revalidated in S2/later because their accepted assumptions depend on superseded S1 truth:

- `docs/domain/strategic-model.md` — old CR/CD BC structure, ADR-016 MVP exclusion and direct AM→Access Policy authorization path;
- `docs/domain/capabilities.md` — old capability ownership/grouping around Connectivity Requirements/Decision;
- `docs/domain/connectivity-decision-model.md` and Connectivity Requirements tactical material — legacy domain realization, not current G1 target;
- `docs/domain/access-policy/tactical-model.md` — single Decision consumption and current state/window mechanics require revalidation against bilateral grant/withdrawal semantics;
- `docs/decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md` plus ACC target domain model — zero/many Resource-binding assumption is dirty;
- `docs/domain/access-policy-realization/README.md` — provider-specific rendering ownership must be revalidated against the normalized/provider-boundary direction;
- UI/API/current implementation artifacts that expose old Requirement/Decision/proposal workflows are migration evidence only until later gates.

## NEP parked recovery state

NEP remains independently checkpointed after `G1 PASS`:
- accepted behavior is in `docs/requirements/network-enforcement-placement-core.md`;
- its next stage is S2 Domain Design revalidation;
- no runtime migration or implementation is authorized.

NEP does not need to be the first S2 slice. Strategic capability/context regrouping should establish upstream ownership/contracts before affected Tactical DDD is resumed.

## Other recovery facts

- Access Policy Realization implementation remains parked and unauthorized.
- APR unresolved future work remains at `docs/engineering/context-problems/access-policy-realization.md`.
- Requirement-to-Policy Alignment and legacy CR/CD packets remain historical/current-state evidence and require explicit revalidation before reuse.
- No G4 implementation lease exists.

## Blockers

No repository blocker for starting S2 Strategic DDD.

## Gate

Breadth-first capability `G1 PASS`.

Next gate: `G2` after Strategic/Tactical Domain Design is sufficiently revalidated for the selected scope.

## Next

Start S2 with capability cohesion/ownership analysis:

```text
accepted capabilities
    -> semantic ownership / invariants
    -> candidate Bounded Context grouping
    -> upstream/downstream contracts
    -> Context Map
    -> Tactical DDD only for contexts selected after the strategic boundary is coherent
```

First S2 question: determine whether Business Connectivity and Access Governance are separate semantic owners/Bounded Contexts or parts of a larger cohesive governance context, while keeping Authority Management and Access Policy responsibilities distinct unless evidence proves otherwise.
