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

Primary actor: user/operator with effective `ReadEffectiveDesiredPolicy` authority for the selected RuleGovernanceScope.

Detailed role naming is not a separate Wave-1 domain rule; Authority Management determines whether the actor may perform that action for the requested scope/as-of.

## Effective selection

For the first implementation, Access Policy selects one authorized RuleGovernanceScope at a time.

A Rule contributes desired effect only when:

```text
authoritative Rule exists from an Allowed decision
AND RuleGovernanceScope == selected scope
AND operational state == Active
AND (EffectiveWindow absent OR start <= export as-of < end)
```

`Inactive`, out-of-window or different-governance-scope Rules remain authoritative but are outside the effective desired-policy subset and produce no normalized rows.

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
Rule ID + Rule semantic identity + RuleGovernanceScope
+ Connectivity Decision correlation/reference
+ effective Rule state/property context
+ one source Resource/Endpoint/address realization + RC provenance
+ one destination Resource/Endpoint/address realization + RC provenance
+ DcsTrafficAlternative
+ snapshot/export as-of
+ read-authority provenance
+ ACC fact/validity/provenance
```

`DcsTrafficAlternative` is the Wave-1 source-neutral traffic selector:

```text
protocol = canonical non-empty token
sourcePorts = NotApplicable | Any | canonical inclusive PortRange set
destinationPorts = NotApplicable | Any | canonical inclusive PortRange set
serviceReference = optional ACC-owned semantic reference/label
```

Port ranges are inclusive `0..65535`, canonicalized to sorted non-overlapping/non-adjacent ranges, and remain ranges rather than per-port expansion. `Any` and `NotApplicable` are distinct meanings.

Serialization such as CSV/XLSX is an interface choice.

## Normalization boundaries

- normalization consumes only a successful immutable Export Snapshot; it performs no live catalogue/authority lookup;
- each row uses exactly one captured source EndpointRealization and one captured destination EndpointRealization;
- one Rule expands by the deterministic product of source realizations × destination realizations × DCS traffic alternatives;
- every expanded row retains correlation to its authoritative Rule and all contributing source facts;
- technically equivalent rows from independently authoritative Rules are not cross-Rule collapsed;
- range semantics stay ranges and are not enumerated into individual ports;
- normalization must not broaden or narrow selected Rule semantics;
- concrete DCS payload byte encoding is a translation/codec concern, not normalized policy meaning.

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
