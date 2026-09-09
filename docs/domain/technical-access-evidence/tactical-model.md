# Technical Access Evidence tactical model

Status: `accepted I17 WP0 baseline`.

Date: 2026-09-09.

## Scope

This model defines the first executable consistency model for the **Technical Access Evidence** bounded context.

TAE owns the source-qualified claim that technical access material was reported, observed/derived, or imported for one source-defined scope and source-time statement.

It does not own:
- whether access is required or authorized;
- whether a technical predicate maps to a domain interaction;
- where traffic is enforced;
- whether desired policy is realized;
- vendor rendering or device mutation.

Core invariants:

```text
Evidence != Authorization
Evidence != Desired Policy
Evidence != Domain Access Resolution
Evidence != Enforcement Placement
Recorded Evidence != Current/Fresh Evidence
```

## Evidence kind

First accepted vocabulary:

```text
Configured
TrafficDerived
Imported
```

Meaning:
- `Configured` — a device/controller/source reports technical material as configured;
- `TrafficDerived` — technical material is derived from observed communication;
- `Imported` — technical material comes from a file or other external artifact.

The kind describes evidence provenance/derivation. It does not grant authority or prove completeness.

## Source qualification

### EvidenceSourceReference

Stable opaque source identity:

```text
sourceNamespace + sourceReference
```

The namespace prevents accidental collisions between unrelated source systems/adapters.

The reference identifies the concrete reporting/derivation/import source. It is not automatically:
- a Resource Catalogue identity;
- a Logical Firewall identity;
- a device/provider identity owned by Network Enforcement Placement.

Cross-context correspondence is introduced only when its owning context accepts it.

### SourceScopeReference

Mandatory opaque source-defined collection boundary.

Examples may later represent a controller policy package, device context, traffic observation query, or imported dataset, but I17 does not standardize those meanings.

`SourceScopeReference` is explicitly not an Authority Management Responsibility Scope and not a Network Enforcement Placement Logical Firewall identity.

### SourceCaptureReference

Mandatory opaque identifier for one source collection/observation/import episode.

For one `EvidenceSourceReference`, the same `SourceCaptureReference` identifies the same attempted evidence capture.

The outer adapter may derive this reference from a native snapshot/run/import identifier or create a stable collection-run identifier when the source has none.

## Evidence time

TAE separates source-qualified evidence time from NAPMS recording time.

### EvidenceTime

```text
Unknown
Instant(at)
Window(start, end)
```

Rules:
- all known instants are offset-aware;
- `Window` requires `start < end` and represents the half-open interval `[start,end)`;
- `Unknown` is an explicit source-time fact;
- `recordedAt` must never be substituted for unknown source time.

Typical use:
- Configured evidence usually has an Instant when the source/capture semantics support it;
- TrafficDerived evidence usually has an observation Window;
- Imported evidence may have Unknown, Instant or Window according to the artifact/source claim.

This is not a validity interval and does not select a current set.

### RecordedAt

Mandatory offset-aware instant when NAPMS accepted the evidence set.

`RecordedAt` is provenance. It does not assert when the source material was effective.

## Normalized technical predicate

### AddressConstraint

```text
Any
Ranges(AddressRange...)
```

`AddressRange` is an inclusive IP interval:
- first and last are valid IP addresses;
- first <= last;
- one range does not cross IP families.

Ranges are canonicalized into deterministic non-overlapping order; overlapping/adjacent ranges of the same family may be merged without changing represented address space.

An exact address is a singleton range.

### PortConstraint

```text
NotApplicable
Any
Ranges(PortRange...)
```

Rules:
- port values are within `0..65535`;
- each range has `first <= last`;
- Ranges is non-empty;
- ranges are canonicalized by merge/sort;
- `NotApplicable` is distinct from `Any`.

### ProtocolSelector

```text
Any
IpProtocolNumber(0..255)
```

The normalized protocol dimension uses IP protocol numbers rather than source/vendor names.

`ProtocolSelector.Any` means **all IP protocols with no port narrowing**. Therefore both source and destination `PortConstraint` must be `Any` when protocol is `Any`. A source expression such as "any protocol, destination port 443" is not represented as `Any + Ranges`; the adapter must expand it into exact protocol-specific entries when the source semantics make that possible, otherwise normalization fails.

For `IpProtocolNumber(n)`, the source adapter must use `NotApplicable` when the selected protocol/source fact has no port dimension and may use `Any | Ranges` only when that port meaning is source-faithful.

The outer adapter maps aliases/names such as TCP/UDP to their exact IANA protocol number. A source expression covering multiple protocol alternatives is expanded into multiple entries when that preserves semantics exactly.

Unsupported protocol dimensions or source-specific service semantics that cannot be reduced without loss are normalization failures in the first slice.

### TechnicalAccessPredicate

Source-neutral technical communication region:

```text
sourceAddresses: AddressConstraint
destinationAddresses: AddressConstraint
protocol: ProtocolSelector
sourcePorts: PortConstraint
destinationPorts: PortConstraint
```

The adapter must map source syntax to this representation without broadening or narrowing the represented technical region.

Source-native service/object names are provenance, not members of the normalized technical region unless a later accepted model assigns them source-neutral semantics.

### EvidenceAction

Optional normalized access effect:

```text
Permit
Block
```

It is present only when the source material factually asserts an effect that can be mapped without semantic loss.

Absence means no compatible action claim was made. It is not `Permit`, `Block` or `Unknown`.

TrafficDerived evidence does not manufacture Permit/Block merely because communication was observed.

### SourcePosition

Optional non-negative position/order fact.

It is stored only when ordering is factual for the source material. Position is meaningful only within its source capture and does not imply cross-source/global evaluation order.

## Aggregate boundary

### TechnicalAccessEvidenceSet

Immutable aggregate root:

```text
TechnicalAccessEvidenceSet
    evidenceSetId
    kind
    evidenceSourceReference
    sourceScopeReference
    sourceCaptureReference
    evidenceTime
    recordedAt
    entries[]
```

One set is one accepted source collection/observation/import episode.

The set is append-only after successful recording. I17 has no edit, retire, supersede or current-state lifecycle.

An empty set is valid evidence that the source capture produced zero normalized entries. Without accepted coverage semantics, an empty set is not proof that no access exists.

### Set identity and idempotency

`EvidenceSetId` is a generated stable surrogate identity.

Semantic capture identity:

```text
EvidenceSourceReference + SourceCaptureReference
```

Recording the same semantic capture again compares the **source-qualified capture payload**, not generated persistence identity or retry time.

Payload equality includes:
- kind;
- Source Scope Reference;
- Evidence Time;
- a **multiset** of source-qualified entry facts: predicate, optional action, optional source entry reference and optional source position.

Incidental parser/list order is not part of payload equality. Duplicate entry facts remain multiplicity-significant. A factual `sourcePosition` participates in each entry fact when present.

Payload equality excludes:
- Evidence Set ID;
- generated Evidence Entry IDs;
- retry-attempt `recordedAt`.

Behavior:
- identical source-qualified payload returns the existing set unchanged, including its original IDs and original `recordedAt`;
- different source-qualified payload for the same source + capture identity is an explicit conflict.

No last-write-wins replacement is allowed.

### TechnicalAccessEntry

Immutable child entity:

```text
TechnicalAccessEntry
    evidenceEntryId
    predicate
    action?
    sourceEntryReference?
    sourcePosition?
```

`EvidenceEntryId` is a generated stable surrogate.

There is no content-based entry uniqueness in I17. Duplicate predicates are preserved because duplicate source rules/records may themselves be factual evidence.

`sourceEntryReference` is optional opaque provenance when the source exposes a stable native item reference.

## Recording semantics

Semantic command:

`RecordTechnicalAccessEvidenceSet`

Input is already source-neutral material from an outer source adapter:
- kind;
- Evidence Source Reference;
- Source Scope Reference;
- Source Capture Reference;
- Evidence Time;
- normalized entries;
- application-owned `recordedAt`.

Behavior:
1. validate source qualification, time and normalized predicate invariants;
2. resolve existing set by semantic capture identity;
3. identical retry is evaluated by source-qualified capture payload and returns the existing immutable set with its original IDs/`recordedAt`;
4. mismatched source-qualified payload for the same capture identity fails as a source/capture conflict;
5. otherwise create one Evidence Set ID and generated Entry IDs;
6. persist the complete immutable set atomically enough that partial entry loss is never reported as a successful set.

If any source item cannot be normalized faithfully, the first slice rejects the complete capture. It does not silently persist a partial set that could later be mistaken for complete source material.

Source-specific parsing/collection/raw payload handling is outside Domain meaning.

## Query semantics

First queries:
- `GetTechnicalAccessEvidenceSet(evidenceSetId)`;
- `FindTechnicalAccessEvidenceSet(source, captureReference)`;
- `ListTechnicalAccessEvidenceSets(filters, page, pageSize)`.

Supported list filters may include:
- source;
- source scope;
- evidence kind;
- recorded-at range;
- known source-time range where mechanically unambiguous.

I17 intentionally exposes no `GetCurrentEvidence`, `GetFreshEvidence` or automatic winner selection across multiple captures.

Selecting evidence for technical-to-domain resolution/reconciliation belongs to a later accepted consumer contract.

## Provenance minimum

Every set preserves:
- Evidence Set ID;
- Evidence Source Reference;
- Source Scope Reference;
- Source Capture Reference;
- Evidence Kind;
- Evidence Time;
- RecordedAt.

Each entry preserves:
- Evidence Entry ID;
- normalized predicate;
- optional action;
- optional source entry reference;
- optional source position.

Raw source payload persistence is not mandatory domain state. A source/provenance reference must remain sufficient to trace the evidence origin according to the concrete adapter contract.

## Freshness, coverage and confidence disposition

### Freshness/currentness — consumer/source contract, not universal TAE state

TAE introduces no universal `Fresh | Stale` state, TTL or automatic current winner.

I20 resolves its first reconciliation need without changing that ownership: the consumer explicitly selects one Configured Evidence Set and a complete first-slice comparison requires `EvidenceTime.Instant == reconciliation asOf`.

`RecordedAt`, latest/nearest capture and age heuristics do not establish currentness.

Revisit TAE only when a concrete production source has an accepted source-qualified validity/currentness fact that must itself be preserved as evidence rather than interpreted by one consumer.

### Coverage — consumer/source contract for I20, not universal TAE state

`SourceScopeReference` records the boundary for which material was collected/reported.

TAE still does not infer `Complete | Partial` merely from a scope reference or empty/non-empty set.

I20 requires a separate trusted Managed Reconciliation Scope/source contract before it can claim a selected configured capture is a complete **effective Permit set** for the exact target/policy partition. That completeness belongs to the reconciliation/source interpretation unless a future evidence source exposes an authoritative capture-completeness fact that TAE itself must preserve.

An empty TAE set therefore remains only an empty evidence capture outside such an accepted consumer/source contract.

### Confidence — deferred

I17 introduces no global numeric/ordinal confidence scale.

Reason:
different evidence sources have no accepted common calibration.

Revisit only when a concrete consumer can define how a confidence value changes a decision without mixing source-specific semantics into TAE.

## Authority and human workflow

I17 core introduces no new Authority Management action merely for ceremony.

Trusted source-adapter admission is a composition/integration concern for the first slice.

A human-facing ingest/read workspace and AM actions are added only when a concrete operator workflow is accepted.

## Invariants

1. Evidence is never authorization or desired policy.
2. Evidence Set ID is stable and generated.
3. Source + Capture Reference is idempotency identity for one capture.
4. Same capture identity cannot silently change content.
5. Evidence sets and entries are immutable.
6. Duplicate entry content is preserved.
7. Source time and RecordedAt remain distinct.
8. Unknown source time remains explicit.
9. Predicate normalization must preserve represented technical space exactly.
10. Optional action/order are stored only when factual.
11. Empty evidence set does not imply absence without coverage semantics.
12. I17 selects no globally current/fresh evidence.
13. Partial normalization is not reported as a successful complete capture.
14. Technical-to-domain resolution, placement and reconciliation remain outside TAE.
