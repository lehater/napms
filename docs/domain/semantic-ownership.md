# Semantic Ownership

Status: `S2 globally revalidated at Strategic level; Tactical work remains active where recorded`.

This file defines semantic ownership, not runtime/service ownership.

Canonical relationship map: `context-map.md`.

## Ownership map

| Knowledge / decision | Semantic owner | Primary result |
|---|---|---|
| Business Process / Connectivity Need | **Business Connectivity** | Need / justification |
| bilateral request/consent/grant/withdrawal | **Access Governance** | governance history / Authorization Granted or Withdrawn |
| effective actor/action/scope authority | **Authority Management** | Effective Authority |
| current semantic authorization | **Access Policy** | Policy Rule / effective authorized policy |
| Resource/Endpoint/current corporate-visible address | **Resource Catalogue** | current/historical realization |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** | effective scope-affiliation and operational responsibility/contact facts |
| ComponentDeployment/Interaction traffic contract | **Application Communication Catalogue** | deployed Interaction subject |
| normalized required technical predicates / target required policy | **non-peer Required Policy Materialization** | TargetRequiredPolicy or unresolved |
| candidate enforcement target/policy locator | **Network Enforcement Placement** | candidate target/locator |
| source-qualified technical evidence | **Technical Access Evidence** | TechnicalAccessEvidenceSet |
| provider-native configured policy -> normalized effective configured policy | **provider interpretation adapter/integration capability** | ConfiguredEffectivePolicySnapshot |
| required-vs-configured comparison, delta, vendor-neutral change design, proposed-result semantic verification | **Access Policy Realization** | Assessment / Delta / VerifiedChangeIntent |
| verified vendor-neutral intent -> provider target representation | **provider rendering adapter/integration capability** | TargetPolicyArtifact |
| controlled provider/device mutation lifecycle | **Network Environment Operations** | NetworkOperation result/provenance |

## Responsibility-scope correlation

`ResponsibilityScopeRef` is a stable correlation value, not a separate aggregate/Bounded Context in the current target.

Independent truths share that reference:

```text
Resource Catalogue
    Resource -> effective Resource Scope Affiliation -> ResponsibilityScopeRef

Authority Management
    Actor + Action + ResponsibilityScopeRef + Time -> Effective Authority
```

Access Governance may consume Resource Catalogue affiliation facts to establish/correlate source and destination governance obligations, then consume Authority Management admission for the corresponding actor/action/scope/time. Resource affiliation does not imply actor authority, and authority does not manufacture Resource affiliation.

Resource Responsibility, owner and administrator/contact facts are operational/business responsibility facts and never substitute for Access Governance approval authority.

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

Network Environment Operations is a target Bounded Context. It owns execution identity, mutation authority admission, concurrency/preconditions, apply outcome and operation provenance for the supplied artifact. NEO does not reinterpret policy meaning or re-decide placement.

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
