# Wave-1 normalized export trace — PLAN-026 WP-01

Status: `accepted J7 behavior trace; WP-02/WP-04 semantics aligned`.

Date: 2026-09-08.

Companion to `docs/target/wave1-story-use-case-trace.md`.

## Scope

```text
selected domain-policy subset
    -> evaluate effective Rules at one logical as-of
    -> resolve authoritative current technical realization
    -> normalize without semantic broadening/narrowing
    -> emit complete explainable vendor-neutral export
    -> STOP
```

Configuration Rendering, configured-state reconciliation and provider/device execution are outside Wave 1.

## Actor / authority

Primary actor: user/operator with effective read/export authority for the selected policy scope.

Detailed role naming is not a separate Wave-1 domain rule; Authority Management determines whether the actor may perform the read/export action for that scope/time.

## Effective selection

A selected Rule contributes desired effect only when:

```text
authoritative Rule exists from an Allowed decision
AND operational state == Active
AND supported declarative effective conditions permit effect at export as-of
```

`Inactive` or condition-false Rules remain authoritative but are outside the effective desired-policy subset and produce no normalized rows.

## One logical export time

Every export has one logical `as-of` evaluation time. Required Access Policy, Resource Catalogue and Application Communication Catalogue facts contributing to successful rows must be valid for that point or expose equivalent temporal validity sufficient to establish a coherent view.

Mutable technical realization is resolved for export `as-of`; it is not copied into immutable Rule identity.

## Completeness / degraded behavior

For every selected effective Rule, all technical facts required for truthful projection must be known and temporally valid.

If any selected effective Rule cannot be projected because required realization is missing/stale/unknown, the operation must not present a complete successful Normalized Policy Export.

Diagnostic partial rows and unresolved reasons may be returned explicitly, but they are not a downstream-ready successful export artifact.

Missing realization for a selected but non-effective Rule does not by itself make the effective-policy export incomplete.

## Minimum normalized semantics

A successful normalized row carries enough semantics to avoid reconstructing missing domain meaning downstream:

```text
Rule ID / Rule provenance correlation
+ Connectivity Decision correlation/reference
+ source technical realization
+ destination technical realization
+ DCS-derived protocol/service/port semantics
+ supported declarative Rule properties where required
+ export as-of
+ source-fact/effective-validity provenance
```

Serialization such as CSV/XLSX is an interface choice.

## Normalization boundaries

- one Rule may expand into several rows when endpoint/protocol/port realization requires it;
- every expanded row retains correlation to its authoritative Rule and source facts;
- technically equivalent rows from independently authoritative Rules must not be collapsed when provenance/business meaning would be lost;
- normalization must not broaden or narrow selected Rule semantics.

## Context contributions

- **Access Policy** — selected Rule identity/state/properties and decision correlation.
- **Resource Catalogue** — authoritative current Resource/Endpoint/address realization for export `as-of`.
- **Application Communication Catalogue** — immutable DCS semantics and other current facts required for projection.
- **Authority Management** — effective read/export authority for selected scope/time.

Not required inline:
- Connectivity Decision internals;
- Technical Access Evidence;
- configured-vs-desired reconciliation;
- target/vendor selection;
- Configuration Rendering;
- provider/device execution.

## Acceptance examples

Canonical examples: `docs/target/wave1-acceptance-examples.md` (E8-E13).

## Deferred J8/J9

- J8 Configuration Rendering consumes the normalized contract plus target/vendor context in a later wave and must preserve its semantics.
- J9 provider/device execution is a later controlled operational responsibility.
