# Blind strategic domain design

Status: ACCEPTED candidate for experiment

## Decomposition basis

Boundaries are derived only from the frozen source corpus using semantic cohesion, independent change and public-contract tests.

## Bounded Context: Resource Description

**Purpose.** Own logical Resource identity, logical network presence, current address realization, Site/Owner/Administrator meaning and basic history.

**Why separate.** Resource/network realization changes independently from application definitions, deployments, business needs and access permission. Address is explicitly not Resource identity.

**Public semantic contract.** Resolve a stable Resource reference to current network realization and provenance/history status needed by downstream application/policy materialization.

## Bounded Context: Application Communication

**Purpose.** Own reusable Application, Component and directed Interaction meaning, including independently meaningful traffic semantics.

**Why separate.** Application communication meaning is reusable across concrete deployments and network realization and can change without moving deployments/resources.

**Public semantic contract.** Resolve stable application/component/interaction references and an exact communication-semantic revision suitable for durable downstream reference.

## Bounded Context: Application Deployment

**Purpose.** Own concrete identity of a deployed Component and its association to a Resource.

**Why separate.** Deployment placement changes independently from reusable Application/Interaction meaning and from Resource address changes.

**Public semantic contract.** Resolve a stable Deployment reference to exactly one Component meaning and one Resource reference for the current MVP.

## Bounded Context: Business Connectivity

**Purpose.** Own Business Process and Connectivity Need meaning and business justification/history for why an application Interaction is required.

**Why separate.** Business need survives deployment/address changes and does not itself grant technical permission.

**Public semantic contract.** Resolve a current Process-backed Need to the required application Interaction and business provenance.

## Bounded Context: Access Policy

**Purpose.** Own deliberate concrete access-request subject, consumed permission outcome, current desired-access truth and its business/decision provenance.

**Why separate.** Permission/effective desired-access meaning changes independently from resource realization and application definition while referencing their stable semantics.

**Public semantic contract.** Expose current effective desired-access subjects using stable Deployment and exact Interaction-semantic references plus business justification/decision provenance.

## External semantic dependency: Connectivity Permission Decision

The MVP requires a permission outcome distinct from request authority, but the accepted source explicitly leaves the internal decision mechanism/reasons/workflow outside the selected baseline. Therefore the decision mechanism is not promoted to a NAPMS Bounded Context. Access Policy consumes a stable decision result correlated to one exact access request.

## Application composition, not Bounded Context: Policy Materialization

Complete vendor-neutral policy output composes current desired access with Application Communication, Application Deployment and Resource Description truth at one logical evaluation time. It owns transformation semantics but no independent business truth; therefore it belongs to APPLICATION-DESIGN rather than strategic domain ownership.

## Relationships

- Business Connectivity references Application Communication Interaction meaning, never current addresses.
- Application Deployment references one Application Communication Component and one Resource Description Resource.
- Access Policy references source/destination Application Deployments, one exact Interaction semantic revision and a current Business Connectivity Need at deliberate request submission.
- Access Policy consumes a Connectivity Permission Decision correlated to the exact request.
- Policy Materialization reads current effective Access Policy and resolves required data from the other contexts without becoming owner of their truth.

## Explicitly deferred problem-space areas

Brownfield evidence recognition, enforcement-placement discovery, configured-policy comparison, provider rendering, network mutation and cleanup optimization remain outside the selected MVP and do not create Bounded Contexts in this graph.

## Atomicity review

All five contexts have distinct semantic cohesion, independently changing truth and a public downstream contract. Policy Materialization fails the independent-truth test and therefore remains application composition. Permission Decision fails the current system-ownership test and remains an external semantic dependency until product input requires NAPMS to own that decision process.
