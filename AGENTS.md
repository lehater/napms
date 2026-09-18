# NAPMS repository agent map

## Start

For non-trivial design, architecture or implementation-planning work:

1. read this file;
2. read `docs/canonical-graph.yaml` to find the current semantic owner and direct dependencies;
3. read `docs/meta/current-workstream.yaml`; if active, follow the referenced workstream state/resume protocol;
4. load only affected canonical artifacts.

Repository state, not chat history, determines where work resumes.

## Current design authority

- `docs/model/**` — strategic/tactical/domain/use-case truth.
- `docs/architecture/structurizr/workspace.dsl` — structural C4/deployment architecture.
- `docs/architecture/mvp-system-rules.yaml` — non-C4 architecture constraints.
- `docs/architecture/persistence/mvp-persistence.yaml` — physical persistence design.
- `docs/contracts/http/napms.openapi.yaml` — HTTP contract.
- `docs/plans/**` — implementation-readiness and verification intent.
- `docs/canonical-graph.yaml` — routing/dependency metadata only.
- `docs-generated/**` — generated non-canonical views.
- `docs/migration/revalidated/**` and `docs-legacy/**` — historical migration evidence.

Product code/tests are implementation/evidence. Never use them to invent or reconstruct missing product/domain/architecture semantics.

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

A Bounded Context is not automatically a service, process, database, team or deployment unit. Current MVP remains one browser frontend, one modular-monolith backend and one PostgreSQL database with module-owned persistence and in-process owner contracts.

Implementation readiness is not implementation authorization. Product implementation/product-test changes require separate explicit authorization. Never commit directly to `main`; use a branch and PR. Merge remains separately authorized.

Historical H/CM records are provenance/resume material, not the normal workflow. Do not invent H21 or extra CM phases outside an explicit workstream.
