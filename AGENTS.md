# NAPMS repository agent map

## Start

For non-trivial design, architecture or implementation-planning work:

1. read this file;
2. read `docs/canonical-graph.yaml` to find the current semantic owner and direct dependencies;
3. read `docs/meta/current-workstream.yaml`; if active, follow the referenced workstream state/resume protocol;
4. load only affected canonical artifacts.

Repository state, not chat history, determines where work resumes.

## Current design authority

- `docs/requirements/**` — accepted product intent, behavior, scope and acceptance truth.
- `docs/model/**` — strategic/tactical/domain/use-case truth.
- `docs/architecture/structurizr/workspace.dsl` — structural C4/deployment architecture.
- `docs/architecture/mvp-system-rules.yaml` — application-boundary, module-interaction, consistency and integration-boundary architecture.
- `docs/architecture/mvp-security-architecture.yaml` — authentication identity boundary and protected-action admission architecture.
- `docs/architecture/mvp-module-contracts.yaml` — canonical in-process module/application contracts.
- `docs/architecture/mvp-technical-representation.yaml` — technical conventions shared by multiple concrete contracts.
- `docs/architecture/persistence/mvp-persistence.yaml` — physical persistence design.
- `docs/architecture/mvp-quality-requirements.yaml` — architecture-significant quality constraints.
- `docs/architecture/mvp-threat-model.yaml` — first-MVP threat model.
- `docs/architecture/mvp-observability.yaml` — diagnostic/observability requirements.
- `docs/contracts/http/napms.openapi.yaml` — HTTP contract.
- `docs/plans/**` — implementation design/readiness and verification intent.
- `docs/canonical-graph.yaml` — routing/dependency metadata only.
- `docs/harness-core.yaml` — NAPMS-owned Authority/Capability/Question/consumer-contract projection over the canonical graph; it never owns artifact paths, dependencies or product/domain/architecture semantics.
- `docs-generated/**` — generated non-canonical views.
- `docs/migration/revalidated/**` and `docs-legacy/**` — historical migration evidence.

Product code/tests are implementation/evidence. Never use them to invent or reconstruct missing product/domain/architecture semantics.

## Documentation vertical

For the first-MVP pilot, responsibility boundaries are checked through `docs/harness-core.yaml`.

The model is about decision ownership and downstream knowledge needs, not workflow state:

- each selected canonical artifact belongs to one Authority;
- bindings declare the capabilities that artifact provides;
- contracts declare what a downstream responsibility needs;
- a missing capability is a design gap and must be routed to the owning Authority;
- `NOT_APPLICABLE` requires explicit canonical evidence;
- unresolved Questions block directly named artifacts and their downstream dependency closure;
- every node in the current canonical graph has exactly one Authority binding;
- every capability listed in `provides` is a public Authority output and must be consumed by another Authority/consumer or declared explicitly terminal with a reason;
- for every non-root Authority, the set of upstream Authorities in its input contract must equal the set implied by cross-Authority dependencies in `docs/canonical-graph.yaml`: neither hidden dependencies nor phantom contract inputs are allowed.

Do not publish internal intermediate facts merely because a canonical artifact exists. Artifact ownership and public capability exposure are separate decisions.

### Authority boundary convergence

A stage, folder, artifact family or familiar discipline name is only a candidate Authority boundary. Recursively challenge it until all three checks pass:

1. **semantic cohesion** — the area owns one coherent family of authoritative decisions/facts rather than several independently meaningful owners;
2. **independent change** — its semantics/lifecycle/invariants can evolve without requiring knowledge of a peer's private model;
3. **stable public contract** — required inputs, public semantic outputs and Question routing are unambiguous.

If any check fails, split the candidate into smaller Authorities and run the same checks again. Stop only when all three pass and the current canonical graph has no unowned node. Do not split merely by file, table, service, screen, package, technology or deployment unit.

Use `python tools/check_harness_vertical.py` for the real first-MVP contracts and `python tools/test_harness_vertical.py` for acceptance/regression behavior.

This repository does not import, pin or call the separate `lehater/harness` repository. The local files are NAPMS-owned copies/adaptations of the ideas being piloted here.

## Semantic harvesting during elicitation

When asking a user or stakeholder a question, do not treat the answer only as a value for that one question. Also notice any additional product/domain semantics stated or implied strongly enough to matter, including:

- requirement or constraint;
- use case, user journey, journey step, actor or goal;
- business rule or invariant;
- domain term or meaning distinction;
- capability/responsibility/boundary clue;
- contradiction, exception or unresolved question.

Discovered does not mean accepted. Keep observation, interpretation and acceptance separate.

If the additional semantic point is explicitly confirmed or otherwise becomes accepted in the exchange, persist it in the smallest current canonical owner found through `docs/canonical-graph.yaml`, then revalidate only affected downstream nodes.

If it is still only a candidate but is important enough to survive the conversation, preserve it as evidence/candidate/question in the nearest relevant discovery artifact or active workstream state. Do not insert an unaccepted candidate into a canonical domain/use-case/architecture model as if it were decided truth.

Harvesting is secondary to the user's current task: do not derail an interview by opening every side topic immediately. Capture material side findings and continue the current line unless a contradiction blocks it.

For explicit evidence synthesis or substantial harvesting across one or more stakeholder answers, use the `stakeholder-evidence-synthesis` Skill.

## Work

Change the smallest owning artifact set. Follow graph dependencies for downstream impact. Regenerate projections rather than editing generated diagrams.

Use `make design-check`, `make design-sync`, and `python tools/check_canonical_graph.py --affected <NODE-ID>`.

When a downstream consumer reports missing knowledge, do not patch another Authority's canonical artifact opportunistically. Route the gap to the Authority that may decide it; after canonical repair, rerun affected contracts and projections.

A Bounded Context is not automatically a service, process, database, team or deployment unit. Current MVP remains one browser frontend, one modular-monolith backend and one PostgreSQL database with module-owned persistence and in-process owner contracts.

Implementation readiness is not implementation authorization. Product implementation/product-test changes require separate explicit authorization. Never commit directly to `main`; use a branch and PR. Merge remains separately authorized.

Historical H/CM records are provenance/resume material, not the normal workflow. Do not invent H21 or extra CM phases outside an explicit workstream.
