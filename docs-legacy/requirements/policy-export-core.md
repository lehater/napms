# Normalized desired-policy export requirements

Status: `accepted current behavior`.

Date: 2026-09-09.

## Purpose

Define the current vendor-neutral normalized desired-policy export behavior.

The export explains the effective desired Access Policy for one authorized scope and logical time using authoritative catalogue/resource facts. It does not render vendor configuration, inspect configured reality or execute network changes.

## Query context

An export is evaluated for:
- authenticated actor;
- one Rule Governance Scope;
- explicit offset-aware `asOf`.

Authority Management must admit the current effective-policy read contract for that scope/time; the current action is `ReadEffectiveDesiredPolicy`. Caller input does not establish trusted actor identity.

## Effective policy input

Access Policy supplies the effective desired-policy subset according to `docs/requirements/access-policy-core.md`.

Only effective Rules participate in a successful export. Inactive/out-of-window/different-scope Rules remain authoritative Access Policy state but do not produce normalized desired-policy rows for that query.

## Logical export snapshot

Before normalization succeeds, the application assembles one immutable logical snapshot for the export `asOf`.

For every selected Rule the snapshot must correlate:
- exact Rule semantic identity and Rule/Decision/proposal provenance;
- Application Communication Catalogue facts for the exact Component Deployments and DCS revision;
- time-qualified Deployment -> Resource binding facts;
- Resource Catalogue endpoint/address realization for the referenced Resources;
- immutable DCS projection semantics;
- authority/provenance required for the selected effective-policy read.

Each contributing fact must provide enough identity/version/effective-validity evidence to establish that it is valid for the same logical `asOf`.

The snapshot is a semantic consistency boundary. It need not be a persisted business aggregate.

## Complete-or-fail behavior

A successful export must be complete and coherently correlated.

If a required fact is:
- missing;
- stale for `asOf`;
- ambiguous;
- mismatched to the exact Rule/DCS/Resource subject;
- unavailable in a way that prevents proving correctness,

then that export attempt is not successful.

The product must not return partial rows as a successful normalized policy merely with warnings.

## Normalization

Normalization transforms only a successful immutable snapshot.

Requirements:
- output is vendor-neutral;
- DCS traffic semantics are preserved without broadening or narrowing access;
- deterministic DCS alternatives may expand into normalized technical rows;
- independent Rule meaning/provenance is not lost through cross-Rule merging;
- technical addresses are realization data, not Access Rule identity.

Normalization must not invent provider/device placement, vendor objects or execution mechanics.

## Provenance and explainability

Every successful normalized row must remain traceable to:
- authoritative Access Rule;
- Connectivity Decision correlation;
- selected governance scope and `asOf`;
- ACC interaction/DCS facts;
- Resource Catalogue realization facts;
- source/effective validity/provenance required to explain the row.

A serializer may change representation but must not remove required semantic/provenance information.

## Acceptance examples

1. An authorized empty effective policy produces a successful empty export.
2. One Active effective HTTPS Rule with valid catalogue/resource facts produces normalized HTTPS/TCP realization without changing Rule identity.
3. A missing destination Resource realization makes the export non-successful rather than silently omitting the Rule.
4. A stale DeploymentResourceBinding at `asOf` makes the export non-successful.
5. Two semantically independent Rules are not merged if that would lose separate provenance.
6. A technical address change at a later `asOf` changes realization output without changing the Access Rule semantic identity.
7. Denied/unknown read authority exposes no normalized policy data.

## Non-goals

- Configuration Rendering/vendor syntax;
- Network Enforcement Placement;
- Technical Access Evidence/configured-state reconciliation;
- provider/device execution;
- best-effort partial policy presented as successful.

These capabilities are sequenced separately in the post-Wave-1 roadmap.

## Canonical references

- effective Access Policy behavior: `docs/requirements/access-policy-core.md`;
- snapshot architecture: ADR-002 and `docs/architecture/current-architecture.md`;
- implementation state: `docs/engineering/current-state.md`.
