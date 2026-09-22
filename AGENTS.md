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
- `docs/harness-engineering-graph.yaml` — NAPMS-owned Authority/Capability/Consumer policy interpreted by the pinned canonical Harness runtime.
- `docs/harness-projection.yaml` — thin NAPMS mapping from canonical artifacts to Authority/Capability providers and Questions; it does not duplicate Harness evaluator semantics.
- `.harness-version` — the single immutable `lehater/harness` commit used by NAPMS design tooling and CI.
- `docs-generated/**` — generated non-canonical views.
- `docs/migration/revalidated/**` and `docs-legacy/**` — historical migration evidence.

Product code/tests are implementation/evidence. Never use them to invent or reconstruct missing product/domain/architecture semantics.

## Engineering-knowledge vertical

Engineering-design responsibility boundaries are checked by the pinned `lehater/harness` runtime using `docs/harness-engineering-graph.yaml`, `docs/harness-projection.yaml` and `docs/canonical-graph.yaml`. NAPMS does not implement a second Harness evaluator.

Keep three levels distinct:

- **Authority** — owns one kind of engineering decision/knowledge (for example Strategic DDD, System Architecture, Interface Design);
- **Artifact** — canonical or generated representation of that knowledge (for example context-map sources, C4 DSL, OpenAPI, persistence model);
- **subject matter** — Bounded Contexts, aggregates, modules, endpoints and other things described inside an artifact.

A Bounded Context or domain module is not a Harness Authority merely because it has semantic ownership inside DDD. The Context Map is an engineering artifact/projection owned by Strategic Domain Design; the contexts shown on it are its subject matter.

The model is about engineering-decision ownership and downstream knowledge needs, not workflow state:

- each selected canonical artifact belongs to one Authority;
- bindings declare the capabilities that artifact provides;
- contracts declare what a downstream responsibility needs;
- a missing capability is a design gap and must be routed to the owning Authority;
- `NOT_APPLICABLE` requires explicit canonical evidence;
- unresolved Questions block directly named artifacts and their downstream dependency closure;
- every node in the current canonical graph has exactly one Authority binding;
- every capability listed in `provides` is a public Authority output and must be consumed by another Authority/consumer or declared explicitly terminal with a reason;
- for every non-root Authority, the set of upstream Authorities in its input contract must equal the set implied by cross-Authority dependencies in `docs/canonical-graph.yaml`: neither hidden dependencies nor phantom contract inputs are allowed.
- the resulting engineering-Authority dependency graph must remain acyclic; a cycle is evidence that decision families were grouped incorrectly or dependencies are wrong.

Do not publish internal intermediate facts merely because a canonical artifact exists. Artifact ownership and public capability exposure are separate decisions.

### Authority boundary convergence

An engineering discipline/decision family is only a candidate Authority boundary. Recursively challenge it until all three checks pass:

1. **semantic cohesion** — the area owns one coherent family of authoritative decisions/facts rather than several independently meaningful owners;
2. **independent change** — its semantics/lifecycle/invariants can evolve without requiring knowledge of a peer's private model;
3. **stable public contract** — required inputs, public semantic outputs and Question routing are unambiguous.

If any check fails, split the engineering responsibility into smaller decision families and run the same checks again. Stop only when all three pass and the current canonical graph has no unowned node. Do not split by Bounded Context, aggregate, module, file, table, service, screen, package, technology or deployment unit unless that split also proves a distinct engineering-decision owner.

Use `make harness-bootstrap` to materialize the exact Harness commit from `.harness-version` into the ignored `.harness-tool/` checkout, then use `make design-check`. Every design command verifies that the checkout HEAD exactly matches the immutable pin. CI performs the same pinned checkout automatically.

Universal Harness semantics are owned only by `lehater/harness`. NAPMS owns project graph/projection data and project-specific checks. Any generally useful evaluator change must be implemented and accepted in Harness first, then adopted here by updating the immutable pin.

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

## Change and CI batching discipline

Treat commits and CI runs as checkpoints, not as a per-file feedback mechanism.

- Keep the pull request in draft while exploring, debugging or making a sequence of related fixes.
- Before committing after a failure, inspect all known failing jobs and related evidence, then batch the coherent fixes together.
- Prefer one commit per coherent checkpoint, not one commit per file or mechanical correction. When repository APIs would otherwise create one commit per file, use a multi-file tree/commit operation when available.
- During iteration, run the smallest deterministic checks that cover the changed surface. Run the full PR gate set only when a coherent checkpoint or final candidate is ready.
- Workflows triggered only by `ready_for_review` are final-checkpoint gates: mark ready only after the branch is stable. If they fail, return to draft, batch the fixes, then make one new ready transition.
- Do not change the branch head merely to poll or retrigger CI; rerun an existing workflow without content changes when the platform supports it.
- A merge candidate is one stable head for which every applicable required gate is green.

## Work

For work that creates or updates artifacts inside one engineering Authority, first prepare its bounded execution context:

```sh
make authority-context AUTHORITY=SYSTEM-ARCHITECTURE CAPABILITY=engineering.architecture.rules
```

The execution context is ephemeral routing data, not a canonical artifact, work item, approval or workflow state. It contains only:

- canonical provider artifacts for capabilities declared by that Authority's input contract;
- supporting dependency artifacts inside each provider's own Authority (same-Authority closure only);
- the Authority's own current artifacts;
- its permitted write paths and public outputs;
- blocking Questions or DESIGN_GAPs.

If its status is `BLOCKED`, do not produce or patch the target Authority's artifacts to compensate; resolve the upstream Question/gap first. If it is `READY`, use only the listed upstream inputs plus the Authority's own artifacts as engineering context and write only owned paths.

Before finalizing an Authority edit, the changed canonical paths can be checked against ownership:

```sh
python tools/prepare_authority_execution.py SYSTEM-ARCHITECTURE \
  --capability engineering.architecture.rules \
  --check-write docs/architecture/mvp-system-rules.yaml docs/architecture/mvp-module-contracts.yaml
```

Then rerun `make design-check` so published capabilities and downstream contracts are re-evaluated.

Canonical artifacts owned by the selected Authority must not reference canonical paths outside that execution context. A literal downstream canonical-path reference is treated as an ownership/dependency leak even when the canonical graph omitted that edge.

Change the smallest owning artifact set. Follow graph dependencies for downstream impact. Regenerate projections rather than editing generated diagrams.

Use `make design-check`, `make design-sync`, and `python tools/check_canonical_graph.py --affected <NODE-ID>`.

When a downstream consumer reports missing knowledge, route the gap to the engineering Authority that owns that kind of decision; do not route it merely to the Bounded Context or module mentioned by the missing fact. After canonical repair, rerun affected contracts and projections.

A Bounded Context is not automatically a service, process, database, team or deployment unit. Current MVP remains one browser frontend, one modular-monolith backend and one PostgreSQL database with module-owned persistence and in-process owner contracts.

Implementation readiness is not implementation authorization. Product implementation/product-test changes require separate explicit authorization. Never commit directly to `main`; use a branch and PR. Merge remains separately authorized.

Historical H/CM records are provenance/resume material, not the normal workflow. Do not invent H21 or extra CM phases outside an explicit workstream.
