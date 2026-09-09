# Configuration Rendering requirements

Status: `accepted I21 first-slice behavior`.

Date: 2026-09-10.

## Purpose

Define how NAPMS translates accepted vendor-neutral Desired Enforcement Intent into a concrete target representation without changing the traffic semantics established by Access Policy Realization.

The first selected vendor is **Cisco**. The first executable representation is **Cisco Secure Firewall ASA CLI extended ACL** because it provides an explicit textual permit-rule surface matching the current exact IPv4/TCP/UDP first slice. Other Cisco surfaces such as Secure Firewall Threat Defense/FMC are separate renderer contracts and are not implied by this choice.

## Input

Rendering consumes only a successfully derived `DesiredEnforcementPolicy` whose status is `Derived`.

For each `DesiredEnforcementIntent`, the renderer receives:
- `EnforcementTarget = Logical Firewall + Enforcement Attachment`;
- normalized technical region fragment;
- Access Rule references;
- Domain Interaction references;
- placement provenance;
- explicit render target/dialect contract.

Rendering must not recompute authorization, domain resolution, placement or reconciliation.

## Output

A successful render returns a complete deterministic rendered artifact for one Enforcement Target and one renderer contract/version, plus provenance sufficient to trace every emitted permit statement back to the contributing desired intents.

The first slice is derived on demand. Rendering introduces no durable business identity/lifecycle or persistence requirement.

## Exact semantics preservation

A successful rendered artifact must represent exactly the same supported Permit region as its input intents.

The renderer must not:
- broaden source/destination address space;
- broaden protocol;
- broaden source/destination port space;
- omit a desired region;
- merge regions when the merge would lose required provenance or broaden traffic.

Ordering, line numbering, object names and grouping are target representation mechanics and do not redefine Access Rule, Domain Interaction, Logical Firewall or Enforcement Attachment identity.

## First Cisco ASA slice

Supported input:
- IPv4 source/destination CIDR or host regions representable by ASA extended ACL address arguments;
- TCP and UDP;
- exact ports and inclusive port ranges representable by ASA `eq` / `range` operators;
- Permit semantics only.

The first slice emits numeric ports, not service-name aliases, to avoid environment-dependent interpretation.

Unsupported or unproven constructs fail closed. Examples include protocol semantics outside the accepted slice, target features whose effective Permit meaning cannot be proven, or a fragment requiring an approximation.

## Failure semantics

Rendering is all-or-nothing per artifact.

Result status is:
- `Rendered` — every input region was represented exactly;
- `Unsupported` — at least one input region is outside the renderer contract;
- `Unknown` — correctness cannot be established because required target/render knowledge is incomplete or internally inconsistent.

`Unsupported` or `Unknown` returns no executable-looking partial artifact as successful output.

## Determinism

For identical ordered semantic input, target identity, renderer contract/version and naming policy, the produced artifact bytes must be identical.

Determinism is a rendering invariant, not an execution/idempotency claim.

## Provenance

Every emitted statement must be traceable to:
- Enforcement Target;
- contributing desired technical region;
- Access Rule references;
- Domain Interaction references;
- placement provenance;
- renderer name and contract/version.

## Equivalence proof

The implementation must include an independent parser/semantic projector for the supported emitted ASA ACL subset. Tests compare the parsed normalized Permit regions with the input desired regions.

Positive equality alone is insufficient: tests must also demonstrate detection of deliberate broadening, narrowing and omission.

## Non-goals

- applying configuration to a Cisco device;
- discovering current device configuration;
- selecting interface/direction attachment or deployment mechanics beyond the accepted Enforcement Attachment mapping;
- rollback/retry/concurrency;
- FMC/FTD API payload generation;
- deny/block policy modeling;
- multi-vendor abstraction beyond the smallest stable port needed by the Cisco first slice.
