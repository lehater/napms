# Domain Revalidation Plan

Status: `active domain revalidation`.

Date: 2026-09-14.

## Goal

Revalidate only the domain scopes whose accepted S1 semantics or upstream contracts changed, lock coherent Strategic/Tactical DDD before Architecture/implementation, and keep unrelated completed contexts parked.

Current runtime/code/schema remain migration evidence, not automatic target truth.

## Inputs

Primary lifecycle/method inputs:

- `docs/process/domain-design-stage.md`;
- `docs/process/strategic-ddd-convergence.md` when a boundary/owner/relationship is uncertain;
- `docs/process/tactical-ddd-stage.md` when identities/lifecycles/invariants inside an accepted boundary are active;
- `docs/domain/context-map.md` for the globally converged current target relationships;
- the smallest G1 requirement passports and canonical domain/ADR artifacts needed by the selected slice.

Do not preload legacy CR/CD artifacts unless a migration/current-state question specifically requires them.

## Current accepted strategic baseline

Breadth-first capability G1 is accepted.

The 2026-09-14 global Strategic convergence pass is accepted for current target boundaries/relationships/contracts. Canonical map: `docs/domain/context-map.md`.

Current target Bounded Contexts are:

- **Business Connectivity** — Business Process, Connectivity Need, business attribution/justification;
- **Access Governance** — Access Request, bilateral consent, grant/withdrawal and governance history;
- **Access Policy** — current authoritative Policy Rule truth;
- **Authority Management** — effective actor/action/scope authority;
- **Application Communication Catalogue** — concrete ComponentDeployment + immutable Interaction subject;
- **Resource Catalogue** — Resource/Endpoint/current realization, Resource Scope Affiliation and Resource Responsibility;
- **Network Enforcement Placement** — candidate enforcement locations/policy locators;
- **Technical Access Evidence** — normalized source-qualified technical evidence;
- **Access Policy Realization** — required-vs-configured semantic reconciliation/change reasoning;
- **Network Environment Operations** — controlled mutation operation identity/lifecycle, authority admission, concurrency/outcome/provenance.

Non-peer strategic participants include Required Policy Materialization plus provider interpretation/rendering integration capabilities. Provider/network-device and optional enterprise identity/source systems are external seams, not Bounded Contexts.

ADR-019 supersedes the target-boundary assumptions that preserved/excluded the old `Connectivity Requirements` / `Connectivity Decision` model. Those names remain legacy/current-state evidence, not current target Bounded Contexts.

ADR-015 is amended: in MVP each ComponentDeployment belongs to exactly one Resource for its lifetime; moving the Component to another Resource creates another ComponentDeployment.

## Completed S2 slice — governance chain

Strategic DDD accepted:

```text
Business Connectivity
    -- Process-backed Need / justification --> Access Governance

Resource Catalogue
    -- effective Resource Scope Affiliation --> Access Governance

Authority Management
    -- effective action authority --> Access Governance

ACC
    -- concrete deployed Interaction subject --> Access Governance / Access Policy

Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

Tactical DDD accepted for the current slice:

- `docs/domain/business-connectivity/target-tactical-model.md`;
- `docs/domain/access-governance/target-tactical-model.md` revalidated for Resource Scope Affiliation input;
- `docs/domain/access-policy/tactical-model.md` revalidated against grant/withdrawal semantics;
- `docs/domain/application-communication-catalogue/target-model.md` revalidated for exactly-one-Resource deployment semantics.

Core invariants:

- Need is application-semantic business truth, not permission;
- Access Request is one explicit authorization attempt and historical evidence;
- current bilateral consent is subject-level state, not one historical Request;
- grant requires source AND destination consent;
- withdrawal by either side removes current authorization and old approved Requests do not silently restore it;
- Access Policy consumes grant/withdrawal facts and owns one authoritative Rule meaning per semantic subject;
- Resource Catalogue owns Resource Scope Affiliation while Authority Management independently owns actor/action/scope admission;
- Resource owner/administrator/contact facts are not approval authority;
- address/Endpoint changes on the same Resource do not change authorization identity;
- Resource movement creates a different ComponentDeployment and requires renewed authorization.

Governance-chain S2 result: `G2 PASS` for this affected scope (ADR-019 plus dependent scope-input revalidation).

## Completed S2 slice — required-policy materialization

ADR-020 establishes Required Policy Materialization as a non-peer derived composition:

```text
Access Policy effective Policy Rules
+ ACC deployed Interaction / traffic contract
+ Resource Catalogue current Endpoint/address realization
+ NEP candidate target/policy locators
    -> TargetRequiredPolicy | unresolved
    -> APR
```

Key guarantees:

- source contexts retain ownership of their facts;
- materialization has no independent peer-domain lifecycle;
- deduplication preserves all contributing Policy Rule provenance;
- missing Resource/address/placement/locator facts produce explicit unresolved outcomes;
- unresolved is not empty required policy and is not APR drift.

Required-policy materialization result: `G2 PASS` for the affected scope (ADR-020).

## Completed S2 slice — provider policy boundary

ADR-021 establishes:

```text
provider/device configured policy
    -> Provider Policy Interpreter          [adapter/integration]
    -> ConfiguredEffectivePolicySnapshot    [source-neutral]

TargetRequiredPolicy
+ ConfiguredEffectivePolicySnapshot
    -> APR                                  [BC]
    -> VerifiedChangeIntent
    -> Provider Policy Renderer             [adapter/integration]
    -> TargetPolicyArtifact
    -> Network Environment Operations       [BC]
```

Key guarantees:

- provider interpretation/rendering are not peer Bounded Contexts;
- TAE owns source-qualified evidence but not APR current configured-policy selection/completeness;
- APR core stays provider-neutral;
- provider rendering cannot widen/narrow/reinterpret verified intent;
- rendering fails closed when semantic equivalence cannot be established;
- NEO owns controlled execution lifecycle and does not reinterpret policy meaning or placement;
- apply success is not convergence proof.

Provider-policy boundary result: `G2 PASS` for S2 ownership/contracts (ADR-021).

## Completed checkpoint — global Strategic DDD convergence

A global consistency pass was run across all current target Bounded Contexts, derived compositions, integration capabilities and external seams.

Canonical result: `docs/domain/context-map.md`.

Closed P1/P2 findings:

- Network Environment Operations was missing from the canonical target BC list despite an accepted independent semantic lifecycle; it is now normalized as a target BC;
- Resource Catalogue -> Access Governance was implicit even though Access Governance needs responsibility-scope facts; the explicit contract now publishes effective Resource Scope Affiliation while Access Governance retains obligation/scope-selection ownership;
- relationship contracts were distributed across ADR/domain artifacts without one canonical Context Map; they are now consolidated;
- machine-readable external seams were empty despite accepted provider/optional-enterprise boundaries; they are now explicit;
- stale legacy Requirement/Decision governance language in the canonical Resource role summary was aligned to current Business Connectivity / Access Governance / Access Policy ownership;
- this execution plan was stale after ADR-020/021 and is now aligned with the active resume capsule.

Global Strategic result: `PASS` for current target ownership/boundaries/material relationships. This does **not** grant blanket G2 to contexts with remaining Tactical DDD work.

## Deferred/non-blocking strategic-adjacent questions

These are not blockers for the current Context Map:

- exact Process retirement/criticality/organization-reference detail;
- responsibility-scope change consequences for existing authorization;
- selection among legitimately overlapping applicable responsibility scopes;
- request cancellation/expiry and time-bounded authorization;
- exact Rule revision/reactivation representation;
- endpoint-specific ComponentDeployment binding;
- concrete external enterprise organization/identity/source provider contracts.

Routing rule:

- if missing product behavior is required (for example warning vs reapproval vs withdrawal), `REOPEN(S1)` for the smallest affected scope;
- if accepted behavior exists but identity/lifecycle/invariant representation is unclear, remain in Tactical DDD;
- if a concrete external source changes semantic ownership/language boundaries, re-enter Strategic DDD;
- do not invent any of these merely to complete Architecture/implementation.

## Remaining dirty domain areas

### Access Policy Realization Tactical DDD

Still unresolved:

- APR-P03 — final technical-region/value vocabulary and edge cases;
- APR-P04 — data-local semantic computation contract;
- APR-P05 — vendor-neutral change-design vocabulary;
- APR-P06 — proposed-change simulation/verification contract;
- APR-P08 — attribution/explanation semantics where required;
- APR-P09 — final APR Tactical DDD/ERD/persistence classification;
- APR-P10 — target-versus-current migration plan after target semantics are locked.

APR-P02 and APR-P07 strategic ownership are already resolved by ADR-021.

### Network Enforcement Placement internal S2 revalidation

NEP remains separately checkpointed after G1. Its public candidate target/locator contract is accepted and sufficient for APR/materialization; internal Tactical revalidation may proceed independently when selected.

### Legacy runtime/domain artifacts

Old Connectivity Requirements/Decision, Proposal and related UI/API/persistence are migration/current-state evidence. Their removal/transformation is S4/implementation work only after affected target design and architecture are accepted.

## Review method

For each selected slice:

1. identify the smallest semantic question and accepted G1 pressure;
2. route to Strategic or Tactical DDD;
3. update the highest affected semantic owner first;
4. make cross-context contracts explicit before peer internals;
5. revalidate only dependent Tactical semantics after a Strategic change;
6. record P0/P1 blockers explicitly;
7. pass G2 only when Architecture no longer has to invent ownership/identity/lifecycle/invariants;
8. do not authorize implementation without later G3/G4.

## Blockers

No repository blocker is recorded for starting APR-P03.

## Exit criteria

This active revalidation can be retired when every selected/dirty domain slice either:

- has a G2-coherent target boundary/tactical model sufficient for its intended next step; or
- is parked in a durable context-problem register with explicit blockers/revisit triggers.

No implementation is authorized merely by retiring this plan.

## Next

Resume **APR Tactical DDD** with **APR-P03 — effective technical access-space semantics and exact comparison/completeness behavior**.

Do not reopen global Strategic DDD merely to continue normal APR Tactical work. Re-enter Strategic DDD only if APR-P03 exposes an actual ownership/boundary/cross-context-contract contradiction.
