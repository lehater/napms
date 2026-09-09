# Configuration Rendering architecture boundary

Status: `accepted I21 first-slice architecture`.

Date: 2026-09-10.

## Decision

Configuration Rendering remains a downstream capability inside **Access Policy Realization**. Current evidence does not establish a separate language, authority boundary, independent lifecycle or business identity that would justify a new Bounded Context.

APR owns the semantic contract: a successfully rendered artifact must be equivalent to the accepted Desired Enforcement Intent. Vendor syntax and target-specific representation live in outer adapters.

## Dependency shape

```text
APR Domain: DesiredEnforcementPolicy / DesiredEnforcementIntent
        <- APR Application: RenderConfiguration use case + consumer-owned Renderer port
            <- Cisco ASA renderer adapter
                -> rendered text + statement provenance

independent ASA subset parser/projector
        -> normalized rendered Permit regions
        -> equivalence comparison against desired regions
```

The Cisco adapter must not import device-management/execution dependencies.

## First target

The first executable target is Cisco Secure Firewall ASA CLI extended ACL syntax. The supported slice is intentionally narrow: IPv4, Permit, TCP/UDP, exact/inclusive port ranges and directly representable addresses.

This selection does not create a generic `Cisco` domain model and does not imply FMC/FTD compatibility.

## Contracts

The application layer owns a renderer port parameterized by an explicit renderer contract/version. The port consumes already-derived target-specific intents and returns one of `Rendered | Unsupported | Unknown`.

`Rendered` carries complete artifact content and statement-level provenance. Failure outcomes carry reasons but no partial artifact that could be mistaken for executable configuration.

The rendered artifact remains a derived value in I21. No repository/persistence port is introduced.

## Equivalence boundary

Correctness is established at normalized traffic-region level, not by string snapshots alone.

For the supported subset:
1. renderer maps desired fragments to ASA ACL statements;
2. an independent parser/projector maps emitted statements back to normalized Permit regions;
3. the resulting region multiset/set, under the accepted canonical algebra, equals the desired region set;
4. adversarial tests prove broadening, narrowing and omission are rejected.

The equivalence checker must not call the renderer's own formatting helpers to reconstruct expected semantics; otherwise the proof would repeat the same defect.

## Representation rules

- Numeric ports are emitted for deterministic meaning.
- Stable deterministic ACL/statement names or sequence positions may be derived from target + canonical intent ordering; they are representation identity only.
- Technical grouping is allowed only when exact equivalence and required provenance remain demonstrable.
- Unsupported address/protocol/port forms fail closed rather than being approximated.
- No implicit `any`, wildcard expansion or default behavior may broaden an explicitly bounded desired region.

## I22 boundary

I21 produces representation only. I22 owns:
- device/provider connection;
- reading current configuration;
- choosing/applying operational attachment mechanics where required;
- pre/post-check;
- mutation idempotency/concurrency;
- retry/recovery/rollback;
- execution audit/result.

A rendered artifact is therefore not evidence that a device has accepted or applied it.
