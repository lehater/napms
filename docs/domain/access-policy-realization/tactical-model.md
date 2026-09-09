# Access Policy Realization Tactical Model — I18 Technical-to-Domain Access Resolution

Status: `accepted I18 WP0 Tactical DDD baseline`.

Date: 2026-09-09.

## Purpose

Define the first executable Tactical DDD for the **Technical-to-Domain Access Resolution** capability owned by **Access Policy Realization (APR)**.

The capability answers:

> Given one normalized Technical Access Predicate, effective Resource Catalogue knowledge and effective Application Communication Catalogue knowledge at one explicit logical time, which Domain Interaction technical regions does the predicate correspond to, which parts are ambiguous, and which technical remainder is not resolved?

It does not answer whether access is authorized, desired, correctly placed, configured correctly, or what change should be executed.

## Ownership

APR owns:
- Domain Access Resolution;
- Access Correspondence;
- ambiguity classification;
- unresolved technical remainder;
- the shared technical/domain coverage algebra.

Upstream contexts keep ownership of their facts:
- Technical Access Evidence owns source-qualified evidence;
- Resource Catalogue owns Resource/Endpoint realization;
- Application Communication Catalogue owns Component Deployment, DCS and DeploymentResourceBinding;
- Access Policy owns desired/authorized Access Rules;
- Network Enforcement Placement owns enforcement placement.

Resolution is derived truth. I18 introduces no APR aggregate identity, lifecycle or persistence requirement.

## Consumer-independence invariant

Proposal-side and Reconciliation-side matching are the same capability.

```text
same Technical Access Predicate
+ same effective RC knowledge
+ same effective ACC knowledge
+ same asOf
= same Domain Access Resolution
```

No consumer-specific mode may change correspondence, ambiguity or remainder semantics.

## Inputs

### Technical Access Predicate

APR receives a source-neutral predicate projection containing:
- source address constraint: `Any | Ranges`;
- destination address constraint: `Any | Ranges`;
- protocol selector: `Any | IpProtocolNumber(0..255)`;
- source port constraint: `NotApplicable | Any | Ranges`;
- destination port constraint: `NotApplicable | Any | Ranges`.

This projection is semantically equivalent to the TAE normalized predicate but is APR-owned input. APR Domain does not import TAE Domain types.

### Logical time

Every resolution requires explicit offset-aware `asOf`.

I18 does not infer `asOf` from:
- NAPMS `RecordedAt`;
- the latest evidence capture;
- wall-clock now.

A caller may select a source EvidenceTime instant/window according to a later consumer contract, but Unknown EvidenceTime remains unknown and never becomes `RecordedAt`.

### Domain knowledge snapshot

APR consumes an APR-owned projection of effective RC + ACC knowledge.

One candidate technical region is attributable to exactly one Domain Interaction:

```text
Domain Interaction
    Source Component Deployment
    + Destination Component Deployment
    + immutable DCS revision

effective technical region
    source Resource binding(s)
    + source endpoint address(es)
    + destination Resource binding(s)
    + destination endpoint address(es)
    + one normalized DCS traffic alternative
```

The projection carries exact source/destination address facts, exact IP protocol number, port constraints and attributable ACC/RC provenance.

## Domain Interaction

A Domain Interaction is identified by:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

It is not automatically an Access Rule.

Several technical regions may belong to the same Domain Interaction because of:
- multiple effective Resource bindings;
- multiple endpoints;
- multiple DCS traffic alternatives.

Duplicate technical fragments for the same Domain Interaction do not create ambiguity merely because provenance has multiple supporting facts.

## Technical region algebra

### Supported first executable algebra

The first exact algebra supports predicates with one exact `IpProtocolNumber`.

Address `Any` is the union of complete IPv4 and IPv6 address universes.

For one exact protocol:
- port `Any` is the complete numeric port universe `0..65535`;
- port `Ranges` is the canonical numeric subset;
- `NotApplicable` is a distinct non-numeric port semantic;
- numeric port regions and `NotApplicable` do not overlap.

A predicate with `ProtocolSelector = Any` is valid upstream evidence but the first I18 algebra returns **Unknown** because a protocol-wide port-applicability/difference algebra has not been accepted. The original predicate remains traceable and no narrower/broader meaning is invented.

Revisit trigger:
- the first accepted consumer requiring exact all-protocol resolution, or
- an accepted protocol-applicability model that makes exact difference representable.

### Canonical fragments

A supported predicate is decomposed into canonical Technical Region Fragments.

Each fragment has:
- one source IP interval within one IP family;
- one destination IP interval within one IP family;
- one exact IP protocol number;
- one source port region;
- one destination port region.

Multi-range address/port constraints become a canonical union of fragments. Fragment order is representation only.

### Intersection and difference

Intersection is exact set intersection over compatible fragment dimensions.

Difference is exact set difference and may return several canonical fragments.

No approximation, CIDR widening, port widening or best-effort truncation is permitted.

## Access Correspondence

For one technical fragment T and one Domain Interaction technical fragment D:

```text
Exact
Covers
CoveredBy
PartialOverlap
None
```

Definitions:
- `Exact`: T = D.
- `Covers`: D is a strict subset of T.
- `CoveredBy`: T is a strict subset of D.
- `PartialOverlap`: intersection is non-empty and neither contains the other.
- `None`: intersection is empty.

Correspondence records preserve the exact overlap witness and the Domain Interaction + RC/ACC provenance that supports it.

## Domain Access Resolution

One resolution contains:
- the original APR Technical Access Predicate;
- explicit `asOf`;
- input provenance;
- all supported Domain Interaction correspondences;
- ambiguity witnesses;
- unresolved technical remainder;
- predicate-relevant knowledge gaps;
- resolution status.

### Resolution status

```text
Exact
Covered
Partial
Ambiguous
Unresolved
Unknown
```

Status precedence:

```text
Unknown
  > Ambiguous
  > Exact
  > Covered
  > Partial
  > Unresolved
```

#### Exact

Use `Exact` only when:
- knowledge is complete for the predicate;
- no ambiguity exists;
- exactly one distinct Domain Interaction matches;
- one of its technical regions is exactly equal to the full input predicate;
- unresolved remainder is empty.

#### Covered

Use `Covered` when:
- knowledge is complete;
- no ambiguity exists;
- at least one Domain Interaction corresponds;
- the union of known overlap witnesses covers the entire input predicate;
- the result is not `Exact`.

This includes a technical predicate that is fully contained within a broader Domain Interaction region or spans several non-ambiguous regions.

#### Partial

Use `Partial` when:
- knowledge is complete;
- no ambiguity exists;
- at least one non-empty correspondence exists;
- exact unresolved remainder is non-empty.

#### Ambiguous

Use `Ambiguous` when one non-empty technical overlap witness is attributable to more than one **distinct Domain Interaction**.

APR returns all competing correspondences and does not select a winner.

#### Unresolved

Use `Unresolved` when:
- knowledge is complete for the predicate;
- no Domain Interaction overlaps the predicate;
- the complete unresolved remainder equals the original predicate.

#### Unknown

Use `Unknown` when a trustworthy complete resolution cannot be established, including:
- `ProtocolSelector = Any` under the first algebra;
- predicate-relevant RC realization is missing/stale/non-unique/corrupt;
- predicate-relevant ACC projection/binding state is invalid/ambiguous;
- an address-relevant DCS traffic selector cannot be translated to exact source-neutral transport semantics;
- any other upstream fact required to determine overlap is unavailable.

Known correspondences may still be returned as evidence, but no completeness claim is made.

## Unresolved Technical Remainder

For supported complete knowledge:

```text
remainder
= input technical region
  - union(all non-empty known overlap witnesses)
```

The remainder is represented as canonical Technical Region Fragments.

For `Unknown`, APR may still compute fragments not covered by known correspondences, but marks remainder completeness false. These fragments mean only “not resolved by currently usable knowledge”, not proof that no missing fact maps them.

## Ambiguity

Ambiguity is technical/domain non-uniqueness, not missing authority.

Two overlap fragments are ambiguous only when:
- they overlap in technical space; and
- they belong to different Domain Interaction identities.

Multiple RC/ACC provenance facts supporting the same Domain Interaction are aggregated, not treated as competing business meanings.

## Effective RC/ACC knowledge

The APR adapter may omit an ACC interaction with no effective Resource binding at `asOf`; it has no effective technical realization to compare.

When effective binding exists but its Resource realization cannot be established, APR must fail closed with a predicate-relevant knowledge gap unless already-known facts prove the candidate disjoint from the input predicate.

Unsupported DCS transport meaning becomes a knowledge gap only when effective address knowledge cannot prove that candidate disjoint from the input predicate.

This prevents unrelated catalogue records from turning every resolution into global Unknown while preserving fail-closed semantics for potentially relevant missing knowledge.

## Provenance minimum

Input provenance is opaque/source-qualified and may include:
- Evidence Set ID;
- Evidence Entry ID;
- evidence source/capture reference.

APR does not own those upstream identities.

Every correspondence preserves enough attributable facts to explain:
- Domain Interaction identity;
- ACC DCS/binding fact/provenance references;
- source RC Resource/Endpoint fact/provenance;
- destination RC Resource/Endpoint fact/provenance;
- exact overlap witness;
- `asOf`.

Knowledge gaps preserve their semantic owner and attributable reference when available.

## TAE adapter rule

The dependency direction is:

```text
TAE Domain/Application
        ^
        | consumed by outer adapter
        |
APR input projection -> APR Application/Domain
```

TAE never imports APR and never stores Domain Access Resolution.

TAE entry `Permit | Block | absent` action is evidence provenance only; I18 correspondence compares the technical predicate region and does not convert evidence action into authorization or desired-state meaning.

## Non-goals / deferred semantics

I18 does not:
- select a “current/fresh” Evidence Set;
- decide authorization;
- create/materialize Access Rules;
- use Access Policy desired-state truth;
- determine Network Enforcement Placement;
- reconcile desired vs configured policy;
- define Add/Remove/Replace/No-op;
- render vendor configuration;
- execute network changes;
- persist Domain Access Resolution;
- expose a public HTTP/Web workflow.

These remain separate later contracts.
