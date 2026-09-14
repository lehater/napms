# Semantic Ownership

Status: `S2 revalidated through provider-policy boundaries`.

This file defines semantic ownership, not runtime/service ownership.

## Ownership map

| Knowledge / decision | Semantic owner | Primary result |
|---|---|---|
| Business Process / Connectivity Need | **Business Connectivity** | Need / justification |
| bilateral request/consent/grant/withdrawal | **Access Governance** | governance history / Authorization Granted or Withdrawn |
| effective actor/action/scope authority | **Authority Management** | Effective Authority |
| current semantic authorization | **Access Policy** | Policy Rule / effective authorized policy |
| Resource/Endpoint/current corporate-visible address | **Resource Catalogue** | current realization |
| ComponentDeployment/Interaction traffic contract | **Application Communication Catalogue** | deployed Interaction subject |
| normalized required technical predicates / target required policy | **non-peer Required Policy Materialization** | TargetRequiredPolicy or unresolved |
| candidate enforcement target/policy locator | **Network Enforcement Placement** | candidate target/locator |
| source-qualified technical evidence | **Technical Access Evidence** | TechnicalAccessEvidenceSet |
| provider-native configured policy -> normalized effective configured policy | **provider interpretation adapter/integration capability** | ConfiguredEffectivePolicySnapshot |
| required-vs-configured comparison, delta, vendor-neutral change design, proposed-result semantic verification | **Access Policy Realization** | Assessment / Delta / VerifiedChangeIntent |
| verified vendor-neutral intent -> provider target representation | **provider rendering adapter/integration capability** | TargetPolicyArtifact |
| controlled provider/device mutation lifecycle | **Network Environment Operations** | NetworkOperation result/provenance |

## Provider interpretation ownership

Provider interpretation owns representation translation, not business/domain truth:

```text
ProviderPolicyState
+ ProviderSemantics
+ comparison scope
    -> ConfiguredEffectivePolicySnapshot
```

It must exactly account for supported provider-specific ordering, deny/default behavior, objects/groups, protocol/service aliases and other constructs that affect effective access. It fails closed when exact interpretation cannot be established.

The projection carries comparable target/policy scope, source-neutral effective permit space, provenance/time, explicit completeness, interpreter identity/version and unsupported-semantics outcome.

`Complete` is a source/interpreter contract for the explicit comparison scope. `Incomplete | Unknown` cannot be interpreted as an empty configured policy.

## TAE boundary

TAE owns immutable source-qualified evidence. It may persist provider-derived normalized entries, but it does not own:

- current configured-policy selection for APR;
- completeness for an APR comparison unit;
- provider effective-policy evaluation across ordered/default/object semantics;
- target/policy comparison correlation.

Configured-effective-policy publication is therefore not a TAE aggregate/lifecycle.

## APR ownership

APR consumes:

```text
TargetRequiredPolicy
ConfiguredEffectivePolicySnapshot
```

and owns the source-neutral semantic relationship:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

APR also owns vendor-neutral change design and semantic verification of the proposed resulting effective policy.

APR does not own provider syntax/evaluation mechanics or provider rendering implementation.

## Provider rendering ownership

Provider rendering translates already verified vendor-neutral intent:

```text
VerifiedChangeIntent
+ provider/target capabilities
+ base target revision/correlation
    -> TargetPolicyArtifact
```

It owns representation translation/capability checks only. It cannot redefine desired semantics.

A successful renderer must establish semantic equivalence for the supported provider semantics. If that cannot be established, rendering fails closed. The architecture may prove equivalence by deterministic construction, round-trip interpretation, simulation or another mechanism later; S2 owns the guarantee, not the mechanism.

## NEO boundary

NEO owns execution identity, mutation authority admission, concurrency/preconditions, apply outcome and operation provenance for the supplied artifact. NEO does not reinterpret policy meaning.

Apply success does not imply convergence. Subsequent provider state is observed/interpreted again and compared against required policy.

## Independent truth dimensions

```text
Observed
Recognized
Needed
Requested / bilateral consent
Authorized Policy Rule
Required technical policy materialized/unresolved
Configured effective policy complete/incomplete/unknown
Realization common/missing/excess
Vendor-neutral change designed
Proposed semantic result verified
Provider artifact rendered / unsupported
Network operation attempted
Subsequent convergence observed
```

No dimension silently becomes another context's authoritative truth.
