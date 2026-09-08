# Wave-1 product requirements — Greenfield baseline

Status: `accepted Wave-1 functional baseline — PLAN-026 WP-03`.

Date: 2026-09-08.

## Scope

Wave 1 delivers one end-to-end product outcome:

```text
compose/request application-backed connectivity
    -> consume ConnectivityDecision(Allowed | NotAllowed)
    -> materialize/manage authoritative Access Rules
    -> select effective desired policy
    -> produce a complete, explainable vendor-neutral normalized export
    -> STOP
```

Configuration Rendering, firewall/provider execution and configured-state reconciliation are outside Wave 1.

## Requirements

### REQ-W1-001 — Compose a concrete Access Rule Proposal

Status: `accepted`.
Disposition: `change/replace` historical request-ingestion semantics.

An actor with effective request authority for the relevant scope may compose and submit one or more independent `Access Rule Proposal` items using trusted domain/catalogue objects rather than firewall/vendor syntax.

Each proposal identifies exactly:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable decision-relevant DCS contract/revision
```

The proposal is not an authoritative Access Rule and has no desired-policy effect before an `Allowed` decision.

Provenance:
- Legacy `SCN-001`: need to normalize/validate requested access before downstream use;
- accepted PLAN-026 WP-02 decisions replace document/IP-row identity with domain-backed semantic identity.

Acceptance intent:
- actor without effective request authority cannot submit for that scope;
- unresolved/invalid domain references cannot form a valid proposal subject;
- submitting several proposals together does not create a shared bulk business lifecycle.

### REQ-W1-002 — Preserve proposal semantic identity through decision

Status: `accepted`.
Disposition: `new` target invariant.

The product must correlate a Connectivity Decision to the exact immutable semantic subject that was proposed. It must not silently substitute newer Source/Destination/DCS identity-defining facts into an existing proposal or decision.

Acceptance intent:
- decision subject equals proposal subject;
- identity-defining semantic change produces another Rule subject and requires another decision.

### REQ-W1-003 — Consume Connectivity Decision without inventing its internals

Status: `accepted`.
Disposition: `replace` historical approval mechanism.

Wave 1 consumes:

```text
ConnectivityDecision
    subject = proposed Access Rule semantic identity
    result = Allowed | NotAllowed
    reference/provenance = opaque where available
```

Only `Allowed` permits materialization/resolution of an authoritative Access Rule. `NotAllowed` produces no authoritative Rule.

The internal decision reasons, policy model, human/automatic mechanism, exceptions, review and supersession lifecycle remain deferred.

### REQ-W1-004 — Materialize one authoritative Access Rule per semantic identity

Status: `accepted`.
Disposition: `new` target requirement.

For one semantic identity tuple, exactly one authoritative Access Rule exists. Repeated materialization of the same `Allowed` identity is idempotent and resolves the existing Rule ID.

On first materialization from `Allowed`, the Rule starts in `Active` state.

Acceptance intent:
- first allowed materialization -> stable Rule ID + `Active`;
- repeated allowed materialization -> same Rule ID, no duplicate Rule;
- not-allowed proposal -> no Rule.

### REQ-W1-005 — Maintain operational Rule state independently from permission

Status: `accepted`.
Disposition: `new` target requirement.

Wave 1 supports:

```text
Active <-> Inactive
```

`Inactive` preserves Rule identity/history but removes desired network effect. Changing `Active/Inactive` does not require a new Connectivity Decision.

Every state transition is auditable at business level.

### REQ-W1-006 — Maintain supported declarative operational properties

Status: `accepted at current D1 depth`.
Disposition: `new/change` target requirement.

An allowed Rule may carry supported declarative operational properties required by Wave 1, including schedule/periodicity where applicable. These properties describe when/how an already allowed Rule contributes desired effect and do not redefine Rule identity or decision subject.

Exact tactical representation is deferred to implementation design; material examples are owned by WP-04.

### REQ-W1-007 — Preserve semantic identity across technical realization changes

Status: `accepted`.
Disposition: `replace` IP-centric historical request semantics.

Changing IP/endpoint/VM/provider or other technical realization does not by itself change the Access Rule identity or rewrite its historical Connectivity Decision.

Technical projection is recalculated from authoritative current catalogue truth.

### REQ-W1-008 — Select an authorized effective desired-policy subset

Status: `accepted`.
Disposition: `new` target requirement.

An actor with the required read/export authority may select a domain-policy subset for export.

At export `as-of`, a Rule contributes desired effect only when:

```text
authoritative Rule exists from an Allowed decision
AND Rule == Active
AND declarative effective conditions permit effect
```

Selection/filter semantics must operate on domain-policy meaning, not vendor/device syntax.

### REQ-W1-009 — Resolve technical realization for one logical export time

Status: `accepted`.
Disposition: `new` target requirement, informed by Legacy missing-evidence weakness.

A Normalized Policy Export is evaluated for one logical `as-of` time. Required Resource Catalogue and Application Communication Catalogue facts used for each row must be valid for that evaluation point or provide equivalent temporal validity sufficient to establish a coherent view.

Missing, stale or unknown required realization prevents a complete successful projection of the affected selected Rule.

### REQ-W1-010 — Produce a complete vendor-neutral Normalized Policy Export

Status: `accepted`.
Disposition: `replace/defer` historical firewall split and configuration-generation pipeline.

For the selected effective Rule subset, the product produces a vendor-neutral normalized technical table suitable for downstream human use or a future renderer without reconstructing missing domain meaning.

Minimum row semantics include:

- authoritative Rule correlation;
- Connectivity Decision correlation/reference where available/required;
- source technical realization;
- destination technical realization;
- DCS-derived protocol/ports/interaction semantics required for realization;
- supported declarative Rule properties;
- export `as-of`;
- source-fact provenance/effective validity sufficient to explain the projection.

CSV/XLSX or another serialization is an interface choice, not domain meaning.

### REQ-W1-011 — Do not present incomplete projection as successful export

Status: `accepted`.
Disposition: `change` historical best-effort semantics.

If any selected effective Rule cannot be truthfully projected, the operation must not present the result as a complete successful Normalized Policy Export.

Diagnostic partial rows and explicit unresolved reasons may be returned, but they are not a successful export artifact suitable for downstream realization.

This deliberately replaces Legacy behavior that could conflate missing evidence with negative evidence and return best-effort output.

### REQ-W1-012 — Preserve independent Rule provenance through normalization

Status: `accepted`.
Disposition: `new` target invariant, aligned with semantics-preserving Legacy generation rules.

Normalization may expand one Rule into multiple technical rows where endpoint/protocol/port semantics require it. Technically identical effects from independently authoritative Rules must not be merged when doing so would lose Rule/decision provenance.

Normalization must not broaden or narrow the traffic semantics represented by the selected Rules.

### REQ-W1-013 — Preserve explainable business provenance end-to-end

Status: `accepted`.
Disposition: `new` target requirement.

The product must be able to correlate at business level:

```text
requesting actor + effective authority scope/time
    -> Access Rule Proposal subject
    -> Connectivity Decision reference/result
    -> authoritative Access Rule ID + semantic identity
    -> relevant Rule state/property history
    -> authoritative realization/DCS facts used for export
    -> normalized export row(s) + export as-of
```

Storage/event-log/version-token mechanisms are architecture/implementation decisions.

## Historical requirement dispositions for Wave 1

| Historical need | Wave-1 disposition | Result |
|---|---|---|
| Word/Excel request ingestion | `defer` | not required for greenfield Wave 1; revisit only as transition compatibility |
| XUIT external request ID | `defer` | historical integration identity is not Wave-1 domain identity |
| normalize/validate requested access before use | `change/retain intent` | domain-backed Proposal must be structurally/semantically valid before decision/materialization |
| IP/protocol/port rows as requested-access identity | `replace` | semantic identity is Deployment + Deployment + immutable DCS |
| replace stored request on re-import | `remove from Wave 1` | no persistent bulk Access Request entity |
| determine firewall placements from routing | `defer` | belongs to later realization/rendering work, not Wave-1 normalized desired-policy export |
| Legacy best-effort output with missing evidence | `replace` | incomplete required evidence blocks successful export |
| current-policy duplicate analysis | `defer` | configured-state reconciliation is outside Wave 1 |
| vendor/device configuration generation | `defer` | Configuration Rendering future wave |
| preserve rule semantics during rendering/grouping | `retain as D0 invariant` | later renderer must not broaden/narrow normalized desired-policy semantics |
| device mutation/deployment | `defer` | Network Environment Operations future wave |

## Explicit Wave-1 deferrals

- internal Connectivity Decision model/process;
- Word/Excel/XUIT compatibility;
- firewall/topology placement calculation;
- vendor/device rendering;
- configured-policy comparison/reconciliation;
- provider/device execution and retry/rollback;
- rich Change Management/revocation lifecycle;
- Rule states beyond `Active/Inactive`.

## WP-03 result

The selected Wave-1 functional/product needs now have explicit target disposition and testable outcome semantics. Remaining detail belongs to acceptance examples, quality scenarios and semantic contracts rather than additional broad requirements discovery.
