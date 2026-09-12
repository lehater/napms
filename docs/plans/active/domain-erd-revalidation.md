# Domain ERD Revalidation Plan

Status: `active planning / model review`.

Date: 2026-09-13.

## Goal

Revalidate the target domain model and ERD for the remaining core MVP contexts before further implementation work. The review must distinguish domain facts and accepted decisions from current tactical/code structure so existing implementation mistakes are not promoted into the target model.

Application Communication Catalogue is already locked by ADR-015 and is consumed here only through its published contract. Connectivity Requirements and Connectivity Decision are excluded from MVP by ADR-016. The MVP Network Enforcement Placement boundary has now been revalidated and locked by ADR-018 plus `docs/domain/network-enforcement-placement/target-tactical-model.md`.

## Scope and order

Review in dependency order:

1. **Resource Catalogue**
2. **Access Policy**
3. **Network Enforcement Placement** — target Tactical DDD/ERD revalidated; implementation migration follows separately
4. **Access Policy Realization**

For NEP, ADR-018 resolves the primary target model: Firewall is the NEP unit of account; batch technical pairs are evaluated against current routing state; ECMP/multipath branches and routing contexts such as VRFs are preserved; local routing provides the baseline candidate signal; Active override rules apply with `Include > Exclude > Routing`; relevant ACL/policy output is the distinct union of names across all retained local branches; NEP and TAE acquire source data independently.

## MVP exclusions and fixed boundaries

Do not redesign as MVP contexts in this pass:

- **Connectivity Requirements** — excluded from MVP by ADR-016;
- **Connectivity Decision** — excluded from MVP by ADR-016;
- **Authority Management** — except opaque references/contracts required to describe another context boundary;
- **Application Communication Catalogue** — ADR-015 is the accepted target and is not reopened by this review.

Target MVP models must not require Requirement or Decision records for normal Rule creation, UI, API or persistence flows.

No runtime migration is authorized by this plan. Domain decisions are locked first; implementation follows only after the corresponding context review is accepted.

## Review method for each context

For every context, complete the following before changing code:

1. **Purpose and boundary**
   - state the business question owned by the context;
   - list what it explicitly does not own;
   - identify upstream/downstream bounded-context contracts.

2. **Evidence and provenance**
   - inspect Strategic DDD, accepted requirements/ADRs and preserved reconstruction evidence;
   - classify each important statement as domain fact, accepted target decision, derived invariant, or tactical implementation choice;
   - use current code/tactical model only to detect drift, not as automatic target truth.

3. **Canonical ERD**
   - define entities, value objects and derived projections;
   - define identity and lifecycle;
   - define cardinalities and temporal relations;
   - distinguish persisted facts from derived/read-model data;
   - mark external references explicitly.

4. **Bounded-context coupling**
   - verify that cross-context relationships use published contracts / opaque stable identifiers rather than peer table navigation;
   - avoid cross-schema SQL foreign keys as a domain integration mechanism;
   - identify any duplicated foreign truth or hidden shared aggregate.

5. **Current-state gap**
   - compare accepted target ERD with current Tactical DDD, persistence schema and code;
   - list semantic mismatches separately from harmless implementation detail;
   - rank blocking mismatches P0/P1/P2/P3 where useful.

6. **Lock the result**
   - publish one canonical target-model document with PlantUML ERD;
   - create/supersede an ADR when the review changes an accepted decision;
   - record unresolved questions explicitly rather than inventing semantics;
   - create a separate migration roadmap only after the target model is accepted.

## Context-specific questions

### 1. Resource Catalogue

Must resolve at least:

- exact meaning and identity of `Resource`;
- `ResourceEndpoint` semantics: address, interface, exposure, or another concept;
- whether one endpoint can have multiple address realizations and whether those are temporal;
- how network-context-dependent reachability and NAT relate to Resource truth;
- scope affiliation and responsibility relations versus Resource identity;
- the unresolved ADR-015 question of whether `ComponentDeployment` may additionally bind to a specific Resource Endpoint.

### 2. Access Policy

Must resolve at least:

- exact Access Rule aggregate/root and identity;
- consumption of the ACC-published subject:
  `sourceComponentDeploymentRef + destinationComponentDeploymentRef + interactionContractRevisionRef`;
- direct Rule creation/materialization under Authority Management admission, without mandatory Requirement or Decision records;
- Rule lifecycle, effective window, governance scope and minimum creation provenance;
- persistence form of external ACC references and absence of peer-schema FK coupling;
- which current Decision/Requirement-related fields or dependencies are now non-MVP implementation artifacts;
- whether any other current Access Policy entities/projections are accidental implementation artifacts.

### 3. Network Enforcement Placement

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
- I19 proven-path semantics remain optional stronger/current-runtime capability, not an MVP prerequisite.

Canonical document:

- `docs/domain/network-enforcement-placement/target-tactical-model.md`

The target NEP ERD is considered locked for this review. Remaining work is implementation planning rather than unresolved core domain semantics:

- concrete secret/profile storage;
- retry/backoff/scheduler failure handling;
- vendor-specific PBR or other source semantics only when a supported adapter actually requires them;
- migration roadmap from current I19/I26 code/persistence to the accepted target.

### 4. Access Policy Realization

Review last because it composes facts from the previous contexts.

Must resolve at least:

- whether it is correctly a bounded context or should be treated as application/domain composition;
- authoritative facts, derived facts and persistence ownership;
- mapping from semantic Access Rule to current Resource/Endpoint realization;
- use of ADR-018 NEP Firewall candidate/local-branch/access-list outputs;
- correlation of NEP locators with Technical Access Evidence policy contents;
- reconciliation/configuration-generation boundaries;
- whether current entities are true domain identities or transient projections/results.

## Required deliverables

For each reviewed context, produce:

- one concise boundary/ownership table;
- one canonical target ERD in PlantUML;
- entity/value-object field and identity table;
- cross-context contract table;
- list of accepted invariants;
- list of unresolved questions;
- target-vs-current implementation gap report;
- ADR and migration roadmap only where the review changes the accepted model.

## Completion gate

This review is complete only when all four contexts have accepted target ERDs that are mutually consistent with ADR-015, ADR-016, ADR-018 and with each other's published boundaries, and the repository clearly distinguishes:

```text
accepted target domain model
!= current tactical/runtime implementation
!= cross-context read composition
!= migration compatibility structure
```
