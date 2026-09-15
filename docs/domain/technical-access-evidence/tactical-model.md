# Technical Access Evidence — Tactical DDD model

## Responsibility

Technical Access Evidence owns source-qualified technical-access facts reported, observed/derived or imported for a source-defined scope and source-time statement. TAE owns the source-neutral evidence vocabulary and the invariants for recording those facts.

TAE does not own acquisition initiation, polling cadence, scheduling, retries, credentials, source transport or provider-specific collection/parsing. It also does not decide whether access is required or authorized, where traffic is enforced, whether policy is realized, what change should be made, how provider policy is rendered or how a target is mutated.

```text
Evidence != Authorization
Evidence != Desired Policy
Evidence != Policy Realization
Evidence != Enforcement Placement
Recorded Evidence != Current/Fresh Evidence
```

## Evidence kinds

```text
Configured
TrafficDerived
Imported
```

- `Configured` — a device, controller or source reports technical material as configured.
- `TrafficDerived` — technical material is derived from observed communication.
- `Imported` — technical material comes from an external artifact.

Evidence kind describes provenance/derivation. It does not grant authority or prove completeness.

## Acquisition boundary

TAE consumes acquired and faithfully normalized evidence:

```text
device/config acquisition capability ----\
NetFlow/IPFIX/flow collector -------------+--> faithful normalization --> TAE
file/import adapter ----------------------/
```

Source-specific producers are application/integration capabilities. They translate source material into the TAE contract without broadening, narrowing or manufacturing facts. If a source fact cannot be represented faithfully, the capture fails rather than persisting an approximation or silently partial result.

Network Environment Operations is not the TAE read/acquisition gateway. NEO owns controlled mutation. Concrete provider/device clients may be shared as an Architecture choice without merging semantic ownership.

## Source qualification

### EvidenceSourceReference

```text
sourceNamespace + sourceReference
```

This is a stable opaque identity for the concrete reporting, derivation or import source. It is not automatically an RC Resource, NEP target or provider/device domain identity.

### SourceScopeReference

Mandatory opaque source-defined collection boundary. It is not an Authority Management Responsibility Scope and not a NEP target identity.

### SourceCaptureReference

Mandatory opaque identity for one collection, observation or import episode. For one `EvidenceSourceReference`, the same capture reference identifies the same semantic capture attempt.

A producer may use a source-native run/snapshot/import reference or create a stable collection-run reference when the source has none.

## Evidence time

TAE separates source-qualified evidence time from NAPMS recording time.

```text
EvidenceTime =
    Unknown
  | Instant(at)
  | Window(start, end)
```

Rules:

- known instants are offset-aware;
- `Window` requires `start < end` and represents `[start,end)`;
- `Unknown` is explicit;
- `recordedAt` never substitutes for unknown source time;
- EvidenceTime is not a validity interval and does not choose a current evidence set.

`recordedAt` is the mandatory offset-aware instant when NAPMS accepted the evidence set. It is provenance, not a claim about when the source material was effective.

## Normalized technical predicate

### AddressConstraint

```text
Any
Ranges(AddressRange...)
```

An `AddressRange` is an inclusive IP interval. Its endpoints are valid addresses of one IP family with `first <= last`. Ranges use deterministic non-overlapping canonical order; overlapping or adjacent ranges of the same family may be merged without changing represented address space. An exact address is a singleton range.

### PortConstraint

```text
NotApplicable
Any
Ranges(PortRange...)
```

Port values are in `0..65535`; each range has `first <= last`; `Ranges` is non-empty and canonicalized. `NotApplicable` and `Any` have distinct meanings.

### ProtocolSelector

```text
Any
IpProtocolNumber(0..255)
```

The normalized protocol dimension uses IP protocol numbers.

`ProtocolSelector.Any` means all IP protocols with no port narrowing, therefore source and destination PortConstraint must both be `Any`. Source expressions that combine protocol alternatives with port restrictions must be expanded into exact protocol-specific entries when that preserves source meaning; otherwise normalization fails.

For `IpProtocolNumber(n)`, producers use `NotApplicable` when the selected protocol/source fact has no port dimension and `Any | Ranges` only when that port meaning is source-faithful.

### TechnicalAccessPredicate

```text
sourceAddresses: AddressConstraint
destinationAddresses: AddressConstraint
protocol: ProtocolSelector
sourcePorts: PortConstraint
destinationPorts: PortConstraint
```

The predicate represents a source-neutral technical communication region. Translation must preserve represented technical space exactly. Source-native service/object names remain provenance unless a source-neutral meaning is explicitly part of the TAE contract.

### EvidenceAction

```text
Permit
Block
```

Action is optional and is present only when source material factually asserts an effect that maps without semantic loss. Absence is not `Permit`, `Block` or `Unknown`. TrafficDerived evidence never manufactures an action merely because communication was observed.

### SourcePosition

Optional non-negative source order/position fact. It is meaningful only within its capture and does not imply cross-source/global evaluation order.

## Aggregate boundary

### TechnicalAccessEvidenceSet

```text
TechnicalAccessEvidenceSet {
    evidenceSetId
    kind
    evidenceSourceReference
    sourceScopeReference
    sourceCaptureReference
    evidenceTime
    recordedAt
    entries[]
}
```

One immutable set represents one accepted source collection/observation/import episode. After successful recording it is append-only. An empty set means the capture produced zero normalized entries; without a separate coverage contract it does not prove that no access exists.

### TechnicalAccessEntry

```text
TechnicalAccessEntry {
    evidenceEntryId
    predicate
    action?
    sourceEntryReference?
    sourcePosition?
}
```

`EvidenceEntryId` is a generated stable surrogate. Entry content is not uniqueness identity: duplicate source facts are preserved. `sourceEntryReference` is optional opaque native provenance.

## Capture identity and idempotency

`EvidenceSetId` is a generated stable surrogate. Semantic capture identity is:

```text
EvidenceSourceReference + SourceCaptureReference
```

Retry equality compares source-qualified capture payload, not generated persistence identity or retry time. The payload includes evidence kind, SourceScopeReference, EvidenceTime and a multiset of entry facts containing predicate, optional action, optional source entry reference and optional source position.

Incidental parser/list order is ignored; duplicate entry multiplicity remains significant. Generated set/entry IDs and retry-attempt `recordedAt` are excluded.

- identical payload for the same semantic capture returns the existing set unchanged, including original IDs and `recordedAt`;
- different payload for the same semantic capture is a conflict;
- no last-write-wins replacement is allowed.

## Recording semantics

```text
RecordTechnicalAccessEvidenceSet
```

Input contains kind, source reference, source scope, capture reference, EvidenceTime, normalized entries and application-owned `recordedAt`.

Recording:

1. validates source qualification, time and predicate invariants;
2. resolves an existing set by semantic capture identity;
3. returns the existing set for an identical retry;
4. rejects a mismatched retry as a source/capture conflict;
5. creates generated set/entry IDs for a new capture;
6. persists the complete immutable set atomically enough that partial entry loss is never reported as success.

If any source item cannot be normalized faithfully, the capture is rejected as a whole.

## Query semantics

```text
GetTechnicalAccessEvidenceSet(evidenceSetId)
FindTechnicalAccessEvidenceSet(source, captureReference)
ListTechnicalAccessEvidenceSets(filters, page, pageSize)
```

List filters may include source, source scope, evidence kind, recorded-at range and mechanically unambiguous known source-time range.

TAE does not expose a universal `GetCurrentEvidence`, `GetFreshEvidence` or automatic winner across captures. Evidence selection for a downstream decision belongs to that consumer/source contract.

## Provenance

Each set preserves set identity, source, source scope, capture reference, kind, EvidenceTime and RecordedAt. Each entry preserves entry identity, normalized predicate and factual optional action/source reference/source position.

Raw source payload is not mandatory TAE domain state. Provenance must remain sufficient to trace origin according to the producer/integration contract.

## Freshness, coverage and confidence

TAE defines no universal `Fresh | Stale` state, TTL or latest-capture winner. A consumer requiring evidence for an effective time must define that rule in its source/consumer contract; `recordedAt` alone does not establish currentness.

`SourceScopeReference` states where material was collected or reported. It does not imply `Complete | Partial`. A consumer requiring complete configured-policy evidence must obtain that guarantee from its accepted source/interpretation contract.

TAE defines no global confidence scale because evidence sources have no source-neutral calibration in the current model.

## Downstream boundary

TAE publishes evidence facts and never turns recording itself into authorization, desired policy or mutation intent. Consumers may interpret Configured or TrafficDerived evidence under their own accepted contracts. Provider-specific semantics that are not faithfully representable in TAE remain outside the normalized TAE model rather than being approximated.

## Invariants

1. Evidence is never authorization or desired policy.
2. TAE owns the meaning and invariants of its normalized evidence vocabulary; producers own source-specific acquisition and faithful translation.
3. TAE does not initiate polling/collection and does not own scheduling, retries, credentials or source transport.
4. EvidenceSetId is stable and generated.
5. Source + Capture Reference is semantic idempotency identity for one capture.
6. The same capture identity cannot silently change payload.
7. Evidence sets and entries are immutable after recording.
8. Duplicate entry content is preserved.
9. Source time and RecordedAt remain distinct; unknown source time remains explicit.
10. Predicate normalization preserves represented technical space exactly.
11. Optional action and position are stored only when factual.
12. Empty evidence does not imply absence without a coverage contract.
13. TAE selects no globally current/fresh evidence.
14. Partial normalization is not reported as a successful complete capture.
15. Evidence recording does not create access requests, policy rules, change intent or network operations.
16. Policy realization, target selection, provider interpretation, rendering and execution remain outside TAE.
17. NEO is not the TAE acquisition/read gateway.
