# Blind strategic domain design

Status: ACCEPTED after Source Corpus amendment 01

## Decomposition basis

Boundaries are derived only from the amended Source Corpus using semantic cohesion, independent change and public-contract tests.

## Bounded Context: Resource Description

**Purpose.** Own logical Resource identity, logical network presence, current address realization, Site/Owner/Administrator meaning and basic history.

**Why separate.** Resource/network realization changes independently from application definitions, deployments, business need and permission. Address is explicitly not Resource identity.

**Public semantic contract.** Resolve stable Resource references to current network realization and explanatory Site/responsibility/address history.

## Bounded Context: Application Communication

**Purpose.** Own reusable Application, Component and directed Interaction meaning, including independently meaningful traffic semantics.

**Why separate.** Reusable communication meaning changes independently from concrete deployment and network realization.

**Public semantic contract.** Resolve stable Application/Component/Interaction references and exact immutable communication-semantic revisions.

## Bounded Context: Application Deployment

**Purpose.** Own concrete identity of a deployed Component and its association to a Resource.

**Why separate.** Concrete placement changes independently from reusable Application/Interaction meaning and Resource address realization.

**Public semantic contract.** Resolve a stable Deployment reference to exactly one Component and one Resource for the selected MVP.

## Bounded Context: Business Connectivity

**Purpose.** Own Business Process and Connectivity Need meaning, currentness and history: why an application Interaction is needed.

**Why separate.** Business justification survives deployment/address changes, may be added or retired independently from access permission, and does not itself authorize access.

**Public semantic contract.** Resolve a Need to Process/Interaction/business provenance and distinguish current from retired justification without rewriting history.

## Bounded Context: Access Policy

**Purpose.** Own deliberate access requests, consumed permission outcomes, one authoritative current-access identity per semantic access, operational/effective state, authorization evidence and associations to business justifications.

**Why separate.** Permission/current desired-access truth changes independently from Resource realization and Business Need lifecycle while referring to their stable semantics.

**Public semantic contract.** Expose current access subjects, permission evidence, ACTIVE/INACTIVE + declarative effectiveness, justification references and auditable history. It does not own whether a referenced Need is currently active; that remains Business Connectivity truth.

## External semantic dependency: Connectivity Permission Decision

The MVP consumes a final permission outcome distinct from request authority. Internal decision reasons, approval policy, human/automatic mechanism, exceptions and supersession remain outside current NAPMS ownership. Access Policy consumes a stable final result correlated to one exact AccessRequest.

## Application composition, not Bounded Context: Policy Materialization

Vendor-neutral policy materialization composes:
- selected current Access Policy;
- current Business Connectivity justification status;
- exact Application Communication semantics;
- Application Deployment placement;
- current Resource realization.

It owns transformation/selection orchestration and completeness semantics, but no independent business truth. It remains APPLICATION-DESIGN rather than a Bounded Context.

## Relationships

- Business Connectivity references reusable Application Communication Interaction meaning, never current addresses/deployments.
- Application Deployment references one Component and one Resource.
- An AccessRequest references source/destination Deployments, one exact InteractionRevision and one current Need as submission justification.
- NeedRef is **not** part of current-access semantic identity.
- ALLOWED AccessRequests for the same semantic access resolve the same authoritative current access and add permission/provenance evidence rather than duplicate it.
- Access Policy may associate additional NeedRefs with an existing current access; association itself does not grant permission.
- Business Connectivity retirement/currentness of those Needs is resolved dynamically and never rewritten by Access Policy.
- Policy Materialization derives a reconciliation condition when an access has no current known Need; it does not auto-revoke/deactivate it.

## Explicitly deferred problem-space areas

Brownfield evidence recognition, enforcement-placement discovery, configured-policy comparison, provider rendering, network mutation, cleanup optimization, permission-decision supersession policy and recurring schedule language remain outside the selected MVP.

## Atomicity review

All five contexts have distinct semantic cohesion, independently changing truth and public contracts. Policy Materialization owns no independent domain truth and remains application composition. Permission Decision remains external until accepted input requires NAPMS to own that decision process.
