# Catalogue Curation Acceptance Examples

Status: `accepted examples for I27 Stage 0`.

Date: 2026-09-10.

## Purpose

Make the first end-to-end catalogue curation value slice concrete before implementation and prevent generic CRUD behavior from becoming the accidental product contract.

Canonical behavior is owned by `docs/requirements/catalogue-curation.md`; Tactical DDD is owned by the ACC/Resource Catalogue tactical-model documents.

## Example A — onboard one application and resource

Given an authorized catalogue curator and an existing Responsibility Scope reference `payments-team`, the curator can create:

```text
Application: Checkout
  Component: Web
    Deployment: Checkout Web / production

Resource: checkout-web-prod
  Endpoint: 10.10.10.10
  Scope affiliation: payments-team

Deployment -> Resource binding
```

The resulting deployment and Resource become available to downstream connectivity discovery according to existing catalogue visibility and scope rules.

The client does not author stable UUIDs, provenance references or database fact identifiers.

## Example B — define communication semantics

Given two Active Component Deployments, the curator can define one directed communication specification using product fields representing the supported semantic subset, for example:

```text
source: Checkout Web / production
destination: Orders API / production
protocol: tcp
destination port: 443
service label: https
```

The backend validates and canonicalizes this authoring model and persists one immutable DCS revision/projection.

The UI does not ask the user to edit encoded `projection_payload` bytes or vendor ACL syntax.

## Example C — rename without changing identity

Renaming:

```text
Checkout Web / production
-> Checkout Frontend / production
```

changes display metadata only.

Existing Connectivity Requirements, Decisions and Rules still reference the same Component Deployment UUID and remain semantically unchanged.

## Example D — move is replacement, not hidden reassignment

If a deployment originally belongs to Component `Checkout Web` but should now represent Component `Portal Web`, the curator cannot mutate its parent Component in place.

The supported workflow is to create the replacement structural identity and retire the old deployment when appropriate. Existing historical policy remains attached to the old deployment identity.

## Example E — retire from leaves upward

An Application with an Active Component cannot be retired.

A Component with an Active Component Deployment cannot be retired.

The user must explicitly retire active children first. Retirement does not hard-delete DCS revisions, bindings or downstream Requirement/Decision/Rule history.

## Example F — change a Resource address

A Resource `orders-prod` currently realized at `10.20.20.20` moves to `10.20.20.30`.

The system ends/replaces the current Resource Realization Version and creates a new temporal realization. The Resource identity stays the same.

Historical Checker/as-of queries may still resolve the old address according to existing temporal contracts.

## Example G — responsibility is not permission

A person recorded as `TechnicalOwner` for Resource `orders-prod` can be displayed as an operational contact.

That relation alone does not permit the person to mutate the Resource, create a DCS, approve connectivity or modify an Access Rule. Each action requires independent Authority Management admission.

## Example H — compatibility migration does not guess Application structure

For a pre-I27 Component Deployment with no persisted parent Application/Component:

```text
deployment id: D1
display name: Orders API prod
```

migration keeps `D1`, creates the deterministic compatibility Application `Imported catalogue`, and creates one deterministic compatibility Component for `D1`.

Two legacy deployments with equal display names are not automatically grouped into one Component.

## Example I — Resource retirement preserves history

Retiring a Resource prevents it from being selected as an Active Resource in new catalogue authoring, but historical bindings, realization facts and policy references remain readable where existing authorization/read contracts permit them.

Resource retirement does not silently revoke Authority Management assignments or rewrite another bounded context.

## Example J — concurrent edit does not silently win

Two browser sessions load the same catalogue entity. Session A renames it and succeeds. Session B then submits a mutation based on the older version.

The second mutation must receive an explicit concurrency conflict rather than silently overwriting A's change.

The exact HTTP version/ETag representation is defined by the I27 command-concurrency decision.
