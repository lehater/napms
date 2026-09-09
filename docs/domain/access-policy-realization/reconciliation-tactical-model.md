# Access Policy Realization Tactical Model — I20 Enforcement Derivation and Reconciliation

Status: `accepted I20 WP-0 Tactical DDD baseline`.

Date: 2026-09-09.

## Purpose

Define the first executable semantics for the central **Access Policy Realization (APR)** outcome:

1. derive exact vendor-neutral desired enforcement intent from effective desired Access Policy plus Network Enforcement Placement;
2. compare that intent with explicitly selected configured enforcement evidence for the same managed enforcement scope;
3. preserve exact common/missing/extra technical regions and explainable domain/evidence/placement provenance;
4. classify the complete semantic delta as `Add | Remove | Replace | No-op` without implying a vendor command or device mutation.

I20 remains inside the existing Access Policy Realization Bounded Context. It does not create a new Bounded Context or a new authoritative policy lifecycle.

## Ownership

APR owns:
- desired enforcement-policy derivation;
- enforcement-policy quality/correspondence decisions needed to avoid silent over/under-permission;
- configured evidence interpretation for reconciliation;
- exact desired/configured set algebra;
- Policy Reconciliation and Required Semantic Change.

Upstream contexts retain their truth:
- Access Policy owns Access Rule identity/state/authorization and effective desired-policy selection;
- Resource Catalogue and Application Communication Catalogue own technical realization/catalogue facts;
- Network Enforcement Placement owns Logical Firewall, Enforcement Attachment and placement selection;
- Technical Access Evidence owns immutable source-qualified evidence/capture facts;
- Authority Management owns actor/action authority.

APR does not turn any upstream reference into its own authoritative peer entity.

## I18 consistency invariant

I20 reuses I18 Technical-to-Domain Access Resolution.

For the same Technical Access Predicate + effective RC/ACC knowledge + `asOf`, reconciliation must receive the same Domain Access Resolution as every other consumer.

I20 may interpret that shared result at policy level, but it must not introduce a reconciliation-specific matcher or change I18 correspondence/remainder semantics.

## Logical time

One reconciliation evaluation uses one explicit offset-aware `asOf`.

The first complete configured-evidence slice requires:
- selected evidence kind = `Configured`;
- selected Evidence Time = `Instant(asOf)`.

`RecordedAt` is never substituted for Evidence Time.

`Unknown`, `Window`, a different instant, “latest”, “nearest” or wall-clock currentness do not establish a complete I20 comparison. They produce an explicit temporal knowledge gap.

This is deliberately strict. A later source contract may add trustworthy validity/currentness semantics, but I20 first slice does not invent them.

## Desired enforcement source

APR consumes one coherent effective desired-policy snapshot for one Access Policy governance scope at `asOf`.

The snapshot must preserve:
- Access Rule identity and Rule Semantic Identity;
- source/destination technical endpoint realization;
- exact transport semantics;
- RC/ACC/Rule/decision provenance;
- proof that only effective desired Rules for the requested governance scope participate.

The first executable placement path requires exact source and destination IP addresses because the current NEP Traffic Relation is exact endpoint-pair scoped.

A desired row that cannot be translated to the accepted exact APR technical algebra is an explicit Unknown; no protocol/address/port widening is allowed.

## Desired domain correctness

An effective Access Rule authorizes one Domain Interaction, but a technical predicate may physically correspond to several Domain Interactions.

Before APR calls an enforcement policy business-correct, it evaluates each desired technical fragment with the shared I18 resolution algebra.

Let `DesiredInteractions` be the set of effective Rule Semantic Identities in the selected desired-policy scope.

A desired technical fragment is acceptable for enforcement only when:
- resolution knowledge is complete for that fragment;
- the fragment is fully covered by resolved Domain Interaction witnesses;
- every Domain Interaction that can occupy the fragment is in `DesiredInteractions`.

If one technical overlap maps to an interaction outside the effective desired set, the desired enforcement derivation is policy-level `Ambiguous`: network enforcement cannot distinguish only the authorized interaction in that technical region.

Several competing Domain Interactions do not remain a policy-level ambiguity when all of them are effective desired interactions; their identical technical access is desired and provenance may be merged.

Predicate-relevant I18 `Unknown` remains I20 `Unknown`. An unexplained desired technical remainder is also Unknown rather than silently permitted.

## Enforcement Target

The first I20 **Enforcement Target** is:

```text
LogicalFirewallId
+ EnforcementAttachmentId
```

Provider realization, path attachment reference and traversal position remain provenance/realization facts and are not target identity.

Rationale:
- one Logical Firewall may have several independently relevant Enforcement Attachments;
- collapsing all attachments to Logical Firewall alone could merge policies that are applied at different enforcement boundaries;
- provider realization may change without changing the Logical Firewall/Attachment semantic target.

If the same accepted Enforcement Attachment occurs more than once on a path, desired policy is not duplicated merely because traversal occurrence provenance is repeated; all occurrences remain explainable.

## Desired Enforcement Intent

A **Desired Enforcement Intent** is a derived value, not an aggregate.

It contains:
- Access Policy governance scope;
- Enforcement Target;
- exact APR Technical Region;
- action `Permit`;
- one-or-more contributing Access Rule / Domain Interaction provenance records;
- NEP placement provenance;
- explicit `asOf`.

Access Rule authorization means “this access may exist”; the first I20 enforcement intent therefore derives Permit semantics only.

I20 does not synthesize deny rules, default policy, zones, vendor objects or device ordering.

Equivalent/overlapping desired fragments for the same managed target are combined by exact canonical set union only. I20 does not claim globally minimum rule count or vendor-optimal representation.

## Desired Enforcement Policy derivation result

For one governance scope + `asOf`, APR produces:
- canonical Desired Enforcement Intents grouped by Enforcement Target;
- desired rows whose complete NEP outcome is `NoEnforcement`;
- desired rows whose complete NEP outcome is `NoForwardingPath`;
- placement ambiguities;
- knowledge gaps;
- derivation status.

Status:

```text
Derived
Ambiguous
Unknown
```

Precedence:

```text
Unknown > Ambiguous > Derived
```

`Derived` means the desired technical/domain interpretation and NEP results are complete under the accepted first-slice models. It may still contain explicit `NoEnforcement` or `NoForwardingPath` rows; those rows produce no guessed target.

`Ambiguous` means technical/domain or placement non-uniqueness prevents a unique business-correct enforcement policy.

`Unknown` means required technical/domain/placement knowledge is incomplete or unsupported.

Known witnesses may remain visible under Ambiguous/Unknown, but no complete enforcement-policy claim is made.

## Managed Reconciliation Scope

A **Managed Reconciliation Scope** is an APR-owned correlation value for one comparison:

```text
Access Policy governance scope
+ Enforcement Target
+ configured evidence source/scope contract
```

It is not an aggregate, Authority Management scope, TAE Source Scope or NEP identity.

A complete comparison requires an explicit trusted source/integration contract proving that:
1. the configured evidence is attributable to the same Enforcement Target;
2. its Source Scope represents exactly the configured policy partition managed for the selected Access Policy governance scope at that target;
3. policy material belonging to another governance/management partition is not silently mixed into this comparison.

String equality, shared names, provider IDs or “same firewall” are insufficient proof.

This boundary is required before `Remove` can be safe: configured access owned by another management scope must never be classified as removable merely because it is absent from one Access Policy governance scope.

## Configured Enforcement Snapshot

APR does not compare raw TAE entries directly.

The configured-evidence outer adapter produces an APR-owned **Configured Enforcement Snapshot** containing:
- Managed Reconciliation Scope;
- selected Evidence Set/source/scope/capture references;
- exact Evidence Time;
- canonical **effective Permit regions**;
- domain-attribution results from I18;
- source-contract/completeness provenance;
- knowledge gaps;
- `completeForManagedScope`.

TAE itself still does not claim universal currentness, completeness or Logical Firewall correspondence.

### First complete source semantics

The first slice may claim `completeForManagedScope = true` only when a trusted source contract establishes that the selected capture is a complete **effective Permit set** for the exact managed scope at `asOf`.

An empty complete effective-permit snapshot is therefore proof of zero configured permit access for that managed scope only because the consumer/source contract says so; an empty TAE set by itself remains only an empty evidence capture.

Raw `Block`, missing action, rule ordering, implicit/default allow/deny, zones or vendor evaluation behavior are not interpreted generically by APR.

A source requiring those semantics must first provide an exact source-specific projection to effective Permit regions. If it cannot, the configured snapshot is Unknown with an attributable evaluation gap.

The first local proof may use a source contract whose configured entries are already unordered effective Permit regions.

## Configured domain attribution

Every configured effective Permit predicate uses the existing I18 resolution capability at the same `asOf`.

APR preserves:
- exact/covered/partial/unresolved correspondences;
- ambiguity witnesses;
- unresolved remainder;
- RC/ACC/evidence provenance.

I18 `Unknown` makes complete I20 reconciliation Unknown.

I18 ambiguity relevant to configured access makes the policy result Ambiguous even if raw technical set equality could otherwise be computed: the same technical permit may represent more than one business interaction and a winner is not selected.

Partial/Unresolved configured-domain attribution remains explainable through exact witnesses; it does not authorize or erase the technical region.

## Reconciliation algebra

One complete Policy Reconciliation compares exactly one Managed Reconciliation Scope.

Let:
- `D` = canonical union of Desired Enforcement Intent Permit regions for that scope;
- `C` = canonical union of effective configured Permit regions for the same scope.

Then:

```text
common  = D ∩ C
missing = D - C
extra   = C - D
```

All operations use the exact APR Technical Region algebra. No CIDR widening, port widening, first-match approximation or vendor object grouping is permitted.

The result preserves exact canonical witnesses for `common`, `missing` and `extra`.

## Policy Reconciliation status

```text
Satisfied
Drift
Ambiguous
Unknown
```

Precedence:

```text
Unknown > Ambiguous > Drift / Satisfied
```

### Satisfied

Use `Satisfied` only when:
- desired derivation for the compared scope is complete;
- configured target/scope/time/effective-policy correlation is complete;
- configured domain attribution has no relevant ambiguity/Unknown;
- `missing` and `extra` are both empty.

### Drift

Use `Drift` when comparison is complete and either `missing` or `extra` is non-empty.

### Ambiguous

Use `Ambiguous` when known competing domain/placement meanings prevent one business interpretation, with no higher Unknown.

All competitors remain visible.

### Unknown

Use `Unknown` whenever a complete comparable result cannot be established, including:
- missing/uncertain Managed Reconciliation Scope correlation;
- incomplete configured capture;
- unsupported configured evaluation semantics;
- non-Instant or temporally mismatched evidence;
- desired technical/domain Unknown;
- NEP Unknown;
- configured I18 Unknown;
- corrupt/inconsistent owner data.

Known overlap/delta candidates may remain diagnostic, but they are not a complete Required Semantic Change.

## Required Semantic Change

For a complete non-ambiguous comparison:

```text
missing empty, extra empty     -> No-op
missing non-empty, extra empty -> Add
missing empty, extra non-empty -> Remove
missing non-empty, extra non-empty -> Replace
```

`Replace` is a scope-level semantic classification meaning both missing and extra technical regions exist.

It does **not** mean:
- one source rule can be atomically replaced;
- a vendor supports a replace command;
- target object identity should be preserved;
- remove-then-add or add-then-remove execution order.

Those mechanics belong to I21 rendering and I22 execution.

Exact `missing` and `extra` witnesses are authoritative; the enum is a compact interpretation.

## Persistence and lifecycle

Desired Enforcement Policy and Policy Reconciliation are derived on demand in the first I20 slice.

I20 introduces no APR aggregate identity, repository/table, edit lifecycle or current-result cache.

A persistence/read-model decision requires independent product/runtime evidence and does not follow automatically from having a result type.

## Consumer/API boundary

The first I20 slice requires no public HTTP/Web workflow and no new Authority Management action.

A later operator surface may expose the same APR result with separate accepted read authority without changing domain meaning.

## Non-goals

I20 does not:
- select latest/current evidence automatically;
- interpret arbitrary firewall rule order/default behavior;
- render vendor/device configuration;
- choose provider-native rule/object identity;
- apply, retry, roll back or verify device changes;
- mutate Access Policy, Connectivity Decision, TAE or NEP state;
- model I21 configuration rendering;
- model I22 network environment operations.
