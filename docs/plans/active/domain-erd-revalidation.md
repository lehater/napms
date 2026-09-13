# Domain ERD Revalidation Plan

Status: `active planning / model review`.

Date: 2026-09-13.

## Goal

Revalidate the target domain model and ERD for the remaining core MVP contexts before further implementation work. The review must distinguish domain facts and accepted decisions from current tactical/code structure so existing implementation mistakes are not promoted into the target model.

Application Communication Catalogue is already locked by ADR-015 and is consumed here only through its published contract. Connectivity Requirements and Connectivity Decision are excluded from MVP by ADR-016. The MVP Network Enforcement Placement boundary has now been revalidated and locked by ADR-018 plus `docs/domain/network-enforcement-placement/target-tactical-model.md`.

This plan may discover more work than should be solved in one pass. Preserve unresolved context-local problems, gaps, real dependencies and blockers under `docs/engineering/context-problems/` instead of inventing an ordered roadmap merely to remember future work.

## Inputs

Primary process and planning inputs:

- `docs/process/decision-protocol.md`;
- `docs/process/domain-change-protocol.md`;
- `docs/process/plan-lifecycle.md`;
- `docs/engineering/context-problems/README.md`.

For each selected context, its canonical domain/requirements/architecture/ADR sources are the semantic inputs. Current runtime code is migration evidence only after target semantics are established.

## Review candidates

The discovery pass currently concerns:

- **Resource Catalogue**;
- **Access Policy**;
- **Network Enforcement Placement** — target Tactical DDD/ERD revalidated; implementation migration follows separately;
- **Access Policy Realization** — problem framing reset and unresolved future work parked in a context problem register.

This list is not a project execution roadmap. The next context is selected by the active/project-level planning decision. Record only genuine causal dependencies between context problems.

For NEP, ADR-018 resolves the primary target model: Firewall is the NEP unit of account; batch technical pairs are evaluated against current routing state; ECMP/multipath branches and routing contexts such as VRFs are preserved; local routing provides the baseline candidate signal; Active override rules apply with `Include > Exclude > Routing`; relevant ACL/policy output is the distinct union of names across all retained local branches; NEP and TAE acquire source data independently.

## MVP exclusions and fixed boundaries

Do not redesign as MVP contexts in this pass:

- **Connectivity Requirements** — excluded from MVP by ADR-016;
- **Connectivity Decision** — excluded from MVP by ADR-016;
- **Authority Management** — except opaque references/contracts required to describe another context boundary;
- **Application Communication Catalogue** — ADR-015 is the accepted target and is not reopened by this review.

Target MVP models must not require Requirement or Decision records for normal Rule creation, UI, API or persistence flows.

No runtime migration is authorized by this plan. Domain decisions are locked first; implementation follows only after the corresponding context review is accepted and the selected active work has an explicit implementation gate.

## Review method for each context

For every context, complete the following before changing code:

1. **Purpose and boundary**
   - state the business question owned by the context;
   - list what it explicitly does not own;
   - identify upstream/downstream bounded-context contracts.

2. **Evidence and provenance**
   - inspect current Strategic DDD, accepted target decisions and owner contracts;
   - classify each important statement as domain fact, accepted target decision, derived invariant, or tactical implementation choice;
   - use current code only to detect migration/gap implications, not as automatic target truth.

3. **Canonical ERD**
   - define entities, value objects and derived projections when the model is ready to lock;
   - define identity and lifecycle;
   - define cardinalities and temporal relations;
   - distinguish persisted facts from derived/read-model data;
   - mark external references explicitly.

4. **Bounded-context coupling**
   - verify that cross-context relationships use published contracts / opaque stable identifiers rather than peer table navigation;
   - avoid cross-schema SQL foreign keys as a domain integration mechanism;
   - identify any duplicated foreign truth or hidden shared aggregate.

5. **Current-state gap**
   - compare accepted target semantics with current persistence/code only after target meaning is established;
   - list semantic mismatches separately from harmless implementation detail;
   - rank blocking mismatches P0/P1/P2/P3 where useful.

6. **Lock or park the result**
   - publish/update canonical target-model artifacts when semantics are ready to lock;
   - create an ADR when the review makes a consequential architectural/domain decision that requires one;
   - record unresolved questions explicitly rather than inventing semantics;
   - create/update a context problem register under `docs/engineering/context-problems/` when unresolved work should survive a workstream switch;
   - record only real dependencies between unresolved problems, not a total execution order;
   - create a roadmap only if an ordered migration/delivery sequence becomes evidence-backed and worth preserving;
   - do not keep a context-specific `PLAN-*.md` active merely to remember parked work.

## Context-specific questions

### Resource Catalogue

Must resolve at least:

- exact meaning and identity of `Resource`;
- `ResourceEndpoint` semantics: address, interface, exposure, or another concept;
- whether one endpoint can have multiple address realizations and whether those are temporal;
- how network-context-dependent reachability and NAT relate to Resource truth;
- scope affiliation and responsibility relations versus Resource identity;
- the unresolved ADR-015 question of whether `ComponentDeployment` may additionally bind to a specific Resource Endpoint.

### Access Policy

Must resolve at least:

- exact Access Rule aggregate/root and identity;
- consumption of the ACC-published subject:
  `sourceComponentDeploymentRef + destinationComponentDeploymentRef + interactionContractRevisionRef`;
- direct Rule creation/materialization under Authority Management admission, without mandatory Requirement or Decision records;
- Rule lifecycle, effective window, governance scope and minimum creation provenance;
- persistence form of external ACC references and absence of peer-schema FK coupling;
- which current Decision/Requirement-related fields or dependencies are now non-MVP implementation artifacts;
- whether any other current Access Policy entities/projections are accidental implementation artifacts.

### Network Enforcement Placement

ADR-018 and the canonical target Tactical DDD now fix the MVP semantics:

- `Firewall` is the NEP unit of account; no separate physical Device entity is required;
- Firewall MVP state is `Active | Inactive`, administered directly through Web UI; no separate lifecycle-command model is required;
- Firewall profile carries management address, platform discriminator, opaque credential/profile reference, connection timeouts and independent polling intervals;
- input is `TrafficPair[1..N]`; MVP candidate queries do not take `asOf`;
- only current successfully collected NEP state is retained; historical network snapshots are not MVP domain history;
- routing/interface refresh and derived reachability switch atomically;
- effective reachability is routing-context-aware and preserves VRF/context references when present;
- effective address segments are non-overlapping per Firewall/context/address family, while one segment may map to multiple interfaces for ECMP/multipath;
- candidate evaluation preserves all local source-interface/destination-interface branches rather than selecting one route;
- a Firewall is a routing candidate when at least one retained branch crosses different interfaces;
- route lookup misses contribute routing false, are logged, and do not suppress override evaluation;
- missing current routing state is logged and the Firewall is skipped for MVP candidate calculation;
- `CandidateOverrideRule` has optional source/destination ranges/interfaces where empty means ANY;
- only Active override rules participate and precedence is `Include > Exclude > Routing`;
- ACL/policy applicability is evaluated for every retained local branch;
- output locator is currently `AccessListLocator(accessListName)` only; final result is the distinct union across branches;
- attachment kind/direction/evaluation topology is adapter knowledge, not core domain state;
- NEP acquisition reads only interfaces/routing/minimal locator-binding metadata required by NEP;
- TAE independently acquires ACL/policy bodies when configured evidence is required;
- current-state `collectedAt` is preserved for age/explainability;
- Resource Catalogue Resource identity remains independent from Firewall identity;
- stronger proven-path semantics are optional and are not an MVP prerequisite.

Canonical document:

- `docs/domain/network-enforcement-placement/target-tactical-model.md`

The target NEP ERD is considered locked for this review. Remaining unresolved implementation concerns should be captured as context problems rather than treated as an implicit roadmap, including:

- concrete secret/profile storage;
- retry/backoff/scheduler failure handling;
- vendor-specific PBR or other source semantics only when a supported adapter actually requires them;
- current-code/persistence migration gaps.

### Access Policy Realization

APR remains a separate bounded context. Its single current problem statement and design direction is:

- `docs/domain/access-policy-realization/README.md`.

Do not recover APR semantics from removed documentation or from current runtime types. Current runtime code is migration evidence only after the target model is established.

APR is currently **not active execution**. Its unresolved problem space is preserved at:

- `docs/engineering/context-problems/access-policy-realization.md`.

The register includes, without imposing total order:

- comparison key and required/configured cross-context contracts;
- configured effective-policy normalization ownership;
- effective-access-space semantics, comparison scope and completeness;
- data-local semantic computation at large scale;
- semantic delta versus policy change design;
- proposed-change semantic verification;
- rendering and APR-to-NEO handoff;
- technical-to-domain explanation/attribution;
- canonical Tactical DDD/ERD/persistence decisions;
- target-versus-current implementation gaps and eventual migration.

No APR implementation work is authorized merely because these problems are recorded. A future active plan selects the concrete problem/increment after revalidating dependencies.

## Required deliverables

For each reviewed context, produce as appropriate:

- concise boundary/ownership clarification;
- canonical target model/ERD when sufficiently resolved;
- entity/value-object field and identity decisions where applicable;
- cross-context contract decisions;
- accepted invariants;
- unresolved questions/problems;
- known target-versus-current gaps;
- real dependencies and implementation blockers;
- ADR when consequential decisions require one;
- a context problem register when unresolved future work should survive a workstream switch;
- an ordered roadmap only when sequence itself is justified by accepted dependencies/migration/rollout constraints.

## Blockers

No repository blocker is currently recorded. A context-specific task starts only after the next bounded context/workstream is selected and its canonical inputs are identified.

## Completion gate

This review is complete only when each context selected for this discovery pass has either:

- an accepted target model/ERD with no blocking semantic unknowns for the intended next step; or
- an explicit context problem register preserving remaining unresolved work, real dependencies and implementation blockers without requiring an active plan.

The repository must clearly distinguish:

```text
accepted target domain model
!= unresolved context problem register
!= optional evidence-backed roadmap
!= current active execution
!= current tactical/runtime implementation
!= cross-context read composition
!= migration compatibility structure
```

## Exit criteria

This active review plan can be retired when:

- every context selected for this discovery pass has either been sufficiently locked or has its unresolved work captured in a durable problem register;
- no selected context depends on an active-plan file merely to preserve future work;
- project-wide planning can choose priorities using the context problem registers without needing old chat history.

## Next

Select the next bounded context/workstream for discovery/revalidation. APR does not need to be read unless it is deliberately resumed; its unresolved work is parked under `docs/engineering/context-problems/`.
