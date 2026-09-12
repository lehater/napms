# Domain ERD Revalidation Plan

Status: `active planning / model review`.

Date: 2026-09-12.

## Goal

Revalidate the target domain model and ERD for the remaining core MVP contexts before further implementation work. The review must distinguish domain facts and accepted decisions from current tactical/code structure so existing implementation mistakes are not promoted into the target model.

Application Communication Catalogue is already locked by ADR-015 and is consumed here only through its published contract. Connectivity Requirements and Connectivity Decision are excluded from MVP by ADR-016.

## Scope and order

Review in dependency order:

1. **Resource Catalogue**
2. **Access Policy**
3. **Network Enforcement Placement**
4. **Access Policy Realization**

`Network Enforcement Placement` is the context currently responsible for selecting/reporting relevant enforcement objects/placements for a traffic relation. The review must verify whether its domain output is correctly modeled as devices, logical firewalls, candidates, placements, or another concept; the existing implementation name/result must not be assumed correct.

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

Must resolve at least:

- whether the context owns network path knowledge, enforcement candidates, selected placement, logical firewall identity, or some combination;
- distinction between physical/network device, provider realization, Logical Firewall and Enforcement Attachment;
- exact input traffic relation and output contract;
- semantics of unordered candidate sets versus proven path/order;
- what is persisted owner truth versus derived selection/query result;
- whether the current model incorrectly conflates "device list" with enforcement placement.

### 4. Access Policy Realization

Review last because it composes facts from the previous contexts.

Must resolve at least:

- whether it is correctly a bounded context or should be treated as application/domain composition;
- authoritative facts, derived facts and persistence ownership;
- mapping from semantic Access Rule to current Resource/Endpoint realization;
- use of Network Enforcement Placement outputs;
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

This review is complete only when all four contexts have accepted target ERDs that are mutually consistent with ADR-015, ADR-016 and with each other's published boundaries, and the repository clearly distinguishes:

```text
accepted target domain model
!= current tactical/runtime implementation
!= cross-context read composition
!= migration compatibility structure
```
