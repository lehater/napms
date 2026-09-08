# Wave-1 semantic contracts — PLAN-026 WP-06

Status: `accepted G2 semantic-contract baseline`.

Date: 2026-09-08.

## Principle

These contracts define business meaning, authority, minimum facts, temporal/error semantics and ownership only. They do not prescribe API shape, DTOs, transport, persistence, service count or deployment topology.

## C1 — Authority Management -> Proposal composition

Purpose: establish whether an actor may propose connectivity for a scope/time.

Owner: Authority Management.

Minimum meaning:

```text
AuthorityCheck
    actor
    domain action = propose connectivity
    scope
    effective time
    result = permitted | not permitted
    provenance/effective validity sufficient for explanation
```

Rules:
- permitted to propose does not imply `ConnectivityDecision = Allowed`;
- later authority changes do not rewrite provenance of an already accepted proposal action;
- missing/unknown required authority does not become implicit permission.

## C2 — Application Communication Catalogue -> Proposal composition

Purpose: provide valid semantic Rule subjects.

Owner: Application Communication Catalogue for Application/Component/Deployment/DCS structure.

Minimum meaning:

```text
Source Component Deployment
Destination Component Deployment
immutable DCS contract/revision
structural compatibility / described directed interaction
```

Rules:
- selected DCS must explicitly describe a compatible directed interaction for the selected deployments/component roles;
- structurally undescribed combinations are not valid proposal subjects;
- no blanket `same Application` rule is added independently of described DCS semantics;
- Component-to-Application and Deployment-to-Component identities cannot be silently rebound under an existing Rule reference;
- decision-relevant DCS semantics are immutable for the referenced contract/revision.

## C3 — Access Rule Proposal -> Connectivity Decision

Purpose: ask whether one exact semantic connection may exist in principle.

Producer: proposal application composition.
Consumer/owner of decision internals: deferred Connectivity Decision Domain.

Minimum subject:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS contract/revision
```

Rules:
- proposal has no authoritative Rule ID/state/effect;
- proposal subject is immutable for the decision correlation;
- newer identity-defining facts must not be silently substituted into an existing proposal.

## C4 — Connectivity Decision -> Access Policy

Purpose: provide the minimum permission fact required for Rule materialization.

Minimum contract:

```text
ConnectivityDecision
    subject = exact proposed Rule semantic identity
    result = Allowed | NotAllowed
    decision reference/provenance = opaque where available
```

Rules:
- only `Allowed` permits Access Policy materialization/resolution;
- `NotAllowed` materializes no Rule;
- Access Policy does not infer or own internal decision reasons/process;
- request authority is not reinterpreted as decision reason;
- historical decision is not silently rewritten by later external-context change.

## C5 — Access Policy authoritative Rule contract

Purpose: own durable desired-access semantics.

Owner: Access Policy.

Minimum meaning:

```text
Rule ID
semantic identity = Source Deployment + Destination Deployment + immutable DCS
operational state = Active | Inactive
supported declarative operational properties
Connectivity Decision correlation
business provenance/audit required by Wave 1
```

Rules:
- exactly one authoritative Rule per semantic identity;
- repeated allowed materialization is idempotent;
- first materialization from `Allowed` starts `Active`;
- `Active <-> Inactive` preserves Rule identity/decision coverage and is auditable;
- schedule/periodicity does not redefine identity/decision subject;
- technical realization is not copied into Rule identity.

## C6 — Access Policy -> Effective Desired Policy selection

Purpose: determine which selected authoritative Rules contribute desired effect at one logical time.

Minimum rule:

```text
contributes_effect =
    authoritative from Allowed
    AND Active
    AND supported declarative effective conditions permit at as-of
```

Rules:
- selected but non-effective Rules emit no export rows;
- `Inactive` is not deletion;
- selection/filtering is domain-policy scoped, not vendor/device scoped;
- read/export action requires effective Authority Management permission for scope/time.

## C7 — Resource Catalogue -> Normalized Policy Export

Purpose: resolve current technical realization without changing Rule identity.

Owner: Resource Catalogue.

Minimum meaning for each required endpoint realization:

```text
Resource/Endpoint correlation
technical address/endpoint realization required for projection
effective validity / source provenance
```

Temporal rule: realization must be valid for export `as-of` or provide equivalent evidence sufficient to establish that validity.

Error rule: missing/stale/unknown realization for a selected effective Rule prevents a complete successful export of that selection.

## C8 — Application Communication Catalogue -> Normalized Policy Export

Purpose: supply immutable DCS protocol/service/port semantics and any current nonidentity facts required for technical projection.

Rules:
- DCS decision-relevant semantics referenced by Rule identity are immutable;
- required facts must be valid/explainable for export `as-of` where temporality applies;
- missing required facts for an effective Rule prevent complete successful export.

## C9 — Normalized Policy Export contract

Purpose: provide a vendor-neutral downstream-ready projection of selected effective desired policy.

Minimum row semantics:

```text
Rule correlation
Connectivity Decision correlation/reference
source technical realization
destination technical realization
DCS-derived protocol/service/port semantics
supported declarative Rule properties where required
export as-of
source-fact/effective-validity provenance
```

Artifact-level rules:
- one logical `as-of`;
- successful artifact is complete for all selected effective Rules;
- diagnostic partial rows may exist only under explicit non-successful/degraded result;
- one Rule may expand to multiple rows with Rule/source correlation retained;
- independently authoritative Rules are not merged if provenance/business meaning would be lost;
- normalization does not broaden/narrow selected semantics;
- serialization format is not domain meaning.

## C10 — Normalized Policy Export -> future Configuration Rendering

Status: `D0 deferred boundary`.

Future renderer may consume normalized semantics plus target/vendor context. It may change representation/grouping only when semantically equivalent; it must not redefine Rule identity, permission, desired-policy meaning or provenance.

## C11 — Future execution boundary

Status: `D0 deferred boundary`.

Provider/device execution consumes implementation-ready representation in a later wave. Retry/rollback/partial/unknown mutation semantics and execution authority do not belong to Wave-1 contracts.

## WP-06 result

Authority, ownership, minimum facts, temporal semantics, error semantics and deferred boundaries are explicit for every interaction required by the Wave-1 propose -> decide-consume -> materialize/manage -> select -> normalized-export chain.
