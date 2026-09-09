# Access Policy Realization — Configuration Rendering tactical model

Status: `accepted I21 first-slice Tactical DDD`.

Date: 2026-09-10.

## Responsibility

Configuration Rendering is a downstream capability of **Access Policy Realization**.

APR already owns the meaning of vendor-neutral Desired Enforcement Intent. I21 adds the responsibility to prove that a target-specific representation preserves that intent exactly for a selected renderer contract.

Current evidence does not justify a new Bounded Context: rendering has no independent business authority, lifecycle, aggregate identity or language boundary. Vendor syntax is representation knowledge implemented by adapters.

## Inputs

The rendering capability consumes only:
- a `DesiredEnforcementPolicy` with status `Derived`;
- one `EnforcementTarget`;
- the `DesiredEnforcementIntent` values for that target;
- an explicit renderer contract/version.

It does not consume Access Rules, Decisions, catalogue facts, NEP facts or TAE directly. Their accepted meaning is already captured in the derived intents and provenance.

## Result

`RenderedConfiguration` is a derived value with:
- status `Rendered | Unsupported | Unknown`;
- Enforcement Target;
- renderer identity and contract version;
- complete rendered content only for `Rendered`;
- statement-level provenance sufficient to trace output to desired intent.

The first I21 slice gives `RenderedConfiguration` no durable identity or lifecycle.

## Invariants

1. `Rendered` means every supported input region is represented with exact Permit semantics.
2. `Unsupported` means a known renderer-contract boundary prevents exact representation.
3. `Unknown` means correctness cannot be established from available rendering knowledge.
4. Failed rendering exposes no partial configuration as a successful artifact.
5. Rendering cannot create, broaden, narrow or reinterpret authorized access.
6. Representation identity such as ACL name, line order or object grouping does not redefine upstream domain identity.
7. Rendering is deterministic for the same canonical semantic input and renderer contract/version.

## Equivalence

The semantic correctness relation is:

```text
normalize(project(render(desired regions))) == normalize(desired regions)
```

for the exact supported first-slice algebra.

The projector is independent from renderer formatting logic so equivalence evidence does not merely reproduce renderer decisions.

## First renderer contract

Selected first adapter: **Cisco Secure Firewall ASA CLI extended ACL**, contract version `1`.

Supported semantic subset:
- IPv4;
- Permit;
- TCP / UDP;
- exact or inclusive source/destination port ranges;
- exact IPv4 address ranges decomposable into one or more exact CIDR/host statements.

The renderer may expand one desired region into multiple ACL statements when required for exact address-range representation. Such expansion changes representation cardinality, not semantic identity.

## Boundaries

I21 owns representation/equivalence only.

I22 owns operational acquisition and mutation, including device connectivity, current-configuration reads, apply, pre/post-check, retry, rollback and execution audit.
