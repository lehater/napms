# PLAN — I21 Configuration Rendering

Status: `S1-S4 implemented; S5 final gate next`.

## Goal

Translate accepted vendor-neutral `DesiredEnforcementIntent` into a target-specific configuration representation while preserving the exact desired traffic semantics and provenance established by Access Policy Realization.

## Accepted S1 decisions

1. **Semantic ownership:** rendering remains a downstream capability inside Access Policy Realization; no new Bounded Context is justified.
2. **First concrete target:** Cisco Secure Firewall ASA CLI extended ACL, renderer contract version `1`.
3. **Artifact lifecycle:** rendered configuration is derived on demand in I21; no independent persistence/aggregate lifecycle.
4. **Equivalence:** correctness is proven by independent projection of rendered ASA Permit statements back into normalized technical regions and comparison with desired regions.
5. **First representation slice:** IPv4 + Permit + TCP/UDP + numeric exact/inclusive source/destination port ranges + exact CIDR/host decomposition.
6. **Failure:** `Rendered | Unsupported | Unknown`; failed rendering exposes no partial executable-looking artifact.
7. **Provenance:** statement output preserves target, rule, interaction, placement and renderer-contract references.

Canonical owners:
- `docs/domain/access-policy-realization/rendering-tactical-model.md`;
- `docs/requirements/configuration-rendering.md`;
- `docs/architecture/configuration-rendering-boundary.md`.

## Guardrails

- Rendering is downstream of I20 vendor-neutral realization semantics.
- Target grouping/order/object identity is technical representation and does not redefine Access Rule, Domain Interaction, Logical Firewall or Enforcement Attachment identity.
- No provider/device acquisition or mutation enters I21; those belong to I22.
- No target-specific apply/remove/retry/rollback semantics enter I21 except representation mechanics strictly required to express the artifact.
- No cross-context SQL or ownership shortcuts.
- Unsupported target semantics fail closed rather than approximating traffic.

## Execution stages

### S1 — Domain/requirements/architecture re-entry

Status: `done`.

Accepted rendering ownership, Cisco ASA first target, derived artifact lifecycle, equivalence, failure and provenance contracts.

### S2 — Framework-free contracts and core

Status: `implemented; final gate pending`.

Implemented:
- APR `RenderStatus` / `RenderedConfiguration` / statement provenance model;
- application-owned `ConfigurationRenderer` port;
- `RenderConfiguration` use case;
- Cisco ASA extended ACL outer adapter;
- deterministic target/intents ordering;
- fail-closed unsupported protocol/representation behavior.

### S3 — Semantics-equivalence proof

Status: `implemented; final gate pending`.

Implemented:
- independent ASA supported-subset semantic projector;
- positive exact-region test;
- adversarial broadening detection;
- unsupported-protocol no-partial-artifact proof.

### S4 — Provenance/composition proof

Status: `implemented; final gate pending`.

Implemented:
- existing PostgreSQL-backed APR owner composition now exposes `RenderConfiguration` wired to the Cisco ASA renderer;
- rendering consumes the already-derived I20 `DesiredEnforcementPolicy` and adds no peer-owner persistence access;
- PostgreSQL integration proof derives desired intent from Access Policy/RC/ACC/NEP owner state, renders Cisco ASA ACL, projects the result back into normalized regions and requires exact equality;
- integration proof requires statement-level rule/interaction/placement provenance and verifies Access Rule, NEP capture and TAE evidence counts remain unchanged by derive+render.

Local test execution is not available from the current connector environment; hosted PR CI remains the executable gate.

### S5 — Final gate and absorption

Status: `next`.

Run hosted final PR gate. If green, absorb durable outcomes into canonical engineering/roadmap state, remove this completed PLAN, update the active capsule, mark I21 complete and promote I22 without selecting it.

## Explicitly out of scope

- device/provider login, fetch, apply or post-check;
- retry, rollback, idempotent mutation or concurrency control;
- production credentials/secrets;
- FMC/FTD rendering in this first slice;
- multi-vendor abstraction beyond the smallest stable port needed by the Cisco ASA first slice;
- operator UI unless an accepted I21 requirement specifically needs a render preview.

## Immediate next action

Open the I21 PR, mark it ready for the hosted final gate, resolve any gate failures on the branch, then perform S5 absorption and squash merge.