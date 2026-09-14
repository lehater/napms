# Active execution

Current: `domain-erd-revalidation.md`

Goal: converge the revalidated capability model into coherent Strategic and Tactical DDD before any affected architecture or implementation work resumes.

Current task: Tactical DDD for Business Connectivity and Access Governance after Strategic DDD established them as separate target Bounded Contexts and kept Authority Management / Access Policy independent.

Lifecycle stage: `S2`

Stage state: `IN_PROGRESS`

Lifecycle basis: breadth-first capability `G1 PASS` is integrated in `main`. ADR-019 now establishes Business Connectivity and Access Governance as separate semantic owners; `docs/domain/strategic-model.md`, `strategic-model.json`, `capabilities.md` and `semantic-ownership.md` are revalidated on branch `docs/s2-strategic-capability-recomposition`. ADR-016 and ADR-005 are superseded for current target semantics. Tactical identities/lifecycles/invariants for the new contexts remain to be accepted before G2.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/requirements/business-connectivity-g1.md`
- `docs/requirements/access-governance-g1.md`
- `docs/process/tactical-ddd-stage.md`

## Expand when needed

Load ADR-019 and the revalidated strategic/semantic-ownership artifacts when checking a boundary or contract. Load Access Policy/ACC/Authority Management artifacts only for a concrete cross-context invariant. Existing CR/CD tactical models are legacy evidence, not target truth.

## Accepted Strategic DDD result

The affected strategic boundary has converged:

```text
Business Connectivity
    Process + Connectivity Need + business attribution
            |
            | Process-backed Need / justification
            v
Access Governance <----- Authority Management
    Request + bilateral consent + grant/withdrawal
            |
            | AuthorizationGranted / AuthorizationWithdrawn
            v
Access Policy
    current authoritative Policy Rule truth
```

Application Communication Catalogue supplies the concrete deployed Interaction subject; Resource Catalogue owns endpoint/address realization.

Business Connectivity and Access Governance remain separate because their authoritative truths and lifecycles change independently: a Need may survive deployment replacement/revocation, while consent is concrete-deployment authorization and may be withdrawn without deleting the Need.

## Tactical design pressure

### Business Connectivity

Must define minimally:
- Business Process identity/lifecycle meaning needed by NAPMS;
- Connectivity Need identity and sameness across deployment/address changes;
- Process-to-Need and Need-to-Interaction invariants;
- business attribution/current-justification semantics without turning observation into Need.

### Access Governance

Must define minimally:
- Access Request identity/history and immutable authorization subject per Request;
- source/destination Approval Obligation semantics;
- side decision/provenance rules;
- current bilateral consent/grant semantics per authorization subject;
- withdrawal/revocation so cancelling one historical Request cannot leave equivalent old approval silently authorizing the subject;
- reauthorization after revocation as a new explicit authorization action;
- grant/withdrawal handoff to Access Policy.

Exact persistence, APIs, workflow engine, ORM/state storage and role/group implementation remain downstream.

## Downstream DIRTY artifacts

At least:
- old Connectivity Requirements / Connectivity Decision tactical models;
- `docs/domain/access-policy/tactical-model.md` where it consumes a single final Decision;
- ADR-015 / ACC target model where Resource binding multiplicity conflicts with G1;
- APR provider-rendering ownership;
- UI/API/runtime flows tied to old Requirement/Decision semantics.

## NEP parked recovery state

NEP remains independently at `G1 PASS`; its next step is S2 revalidation when selected. No implementation is authorized.

## Blockers

No external blocker is known for starting minimal Tactical DDD. Exact Process criticality scale, richer Process lifecycle, time-bounded authorization representation and responsibility-scope-change policy are deferred unless the core tactical invariants require them.

## Gate

S2 is `IN_PROGRESS`.

Strategic convergence for Business Connectivity / Access Governance: `PASS` for the affected boundary.

G2 remains pending until the affected Tactical DDD and dependent Access Policy/ACC semantics are mutually coherent.

## Next

Define the minimal target tactical models for Business Connectivity and Access Governance. Preserve unresolved richer lifecycle questions explicitly rather than inventing storage/state machines.
