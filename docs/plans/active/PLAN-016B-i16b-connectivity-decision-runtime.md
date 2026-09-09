# PLAN-016B — Connectivity Decision Runtime and Workflow

Status: `active`

Date: 2026-09-09.

## Goal

Replace the transitional `local-dev:allowed` Decision provider with the accepted Connectivity Decision bounded-context runtime and integrate final Decision truth into the existing I16A resource-centric Connectivity workspace.

The first useful end-to-end result is:

```text
exact proposal subject + governance scope + logical time
    -> durable effective Connectivity Decision
    -> Access Policy materialization selection
    -> Scoped Connectivity Decision summary
```

Only after that path is trustworthy should participant HTTP/Web workflow be expanded.

## Inputs

- `docs/domain/connectivity-decision-model.md`;
- `docs/requirements/connectivity-decision-core.md`;
- `docs/requirements/connectivity-decision-acceptance-examples.md`;
- `docs/architecture/connectivity-decision-boundary.md`;
- `docs/decisions/ADR-005-connectivity-decision-bounded-context.md`;
- `docs/requirements/scoped-connectivity-inventory.md`;
- `docs/architecture/scoped-connectivity-inventory.md`;
- `docs/requirements/web-ui-requirements.md`.

## Historical implementation donor

PR #26 (`i16/connectivity-decision-runtime`, last reviewed head `5b87a49642efb0a96f1dd0680f2b19294d6081e3`) contains substantial pre-I16A implementation work.

It is an implementation donor, not a merge baseline.

Rules:

- do not merge/rebase PR #26 into this branch;
- port by current semantic contract, not by old commit history;
- do not overwrite I16A composition, Scoped Connectivity runtime, current Web IA or canonical docs;
- preserve the old branch until I16B closes so historical implementation detail remains inspectable.

## Extraction map from PR #26

| Historical area | Current action | Reason |
| --- | --- | --- |
| `src/napms/connectivity_decision/domain/model.py` | port with invariant review | Implements the accepted immutable Decision aggregate, validity, reason/provenance and supersession model. |
| `src/napms/connectivity_decision/application/{ports,record,read,select,options}.py` | port and revalidate | Closely matches I15 contracts; application outcomes and failure semantics must remain fail-closed. |
| `src/napms/connectivity_decision/adapters/postgres/**` | port with concurrency/schema review | Append-only persistence, immutable history, supersession constraints and advisory locking are valuable implementation evidence. |
| `src/napms/authority_management/adapters/connectivity_decision.py` | port/adapt | Correct direction: Decision consumes AM application semantics for independent Decide/Read authority. |
| `src/napms/application_catalogue/adapters/connectivity_decision.py` | port/adapt | Keeps ACC validation/discovery behind an outer adapter without cross-BC domain imports. |
| `src/napms/access_policy/adapters/connectivity_decision.py` | port/adapt | Correct consumer-owned projection from Decision selection into Access Policy. |
| `src/napms/access_policy/application/ports.py` Decision projection | apply surgically | Main has newer inventory APIs; only evolve Decision lookup to subject + governance scope + asOf and required projection fields. |
| `src/napms/access_policy/application/materialize_rule.py` | apply surgically | Preserve current main behavior while binding Decision selection to exact subject/scope/time and validity. |
| `src/napms/composition/postgres_migrations.py` | integrate manually | Add Decision migration without losing I16A Resource Scope Affiliation migration ordering. |
| `src/napms/composition/greenfield_postgres.py` | rewrite integration on current main | Historical composition predates Scoped Connectivity Inventory and would regress I16A if copied. |
| `src/napms/runtime/http_api.py` | reimplement against current runtime | Reuse endpoint/use-case intent only; current HTTP surface includes I16A contracts absent from the donor. |
| old `web/src/App.tsx`, `AppShell.tsx`, preview/navigation changes | do not port wholesale | Historical IA predates primary Connectivity workspace and contextual Request access. |
| old UI requirement/design docs | discard as source | Current canonical UI/requirements documents supersede them. |
| PR #26 Playwright/browser quality-gate work | separate concern | Useful historical work, but testing-system evolution is outside this I16B implementation plan. |
| PR #26 Decision core/PostgreSQL/adapter tests | selectively port | Preserve executable invariant/concurrency evidence while adapting fixtures/composition to current main. |

## Work packages

### WP0 — Donor extraction and contract revalidation — done

- port the Decision package and narrow cross-context adapters into this branch;
- reconcile names/types with current main without pulling old composition/UI;
- compare each ported invariant against I15 canonical requirements;
- remove obsolete references such as historical ADR numbering;
- establish a small core gate before runtime integration.

Exit:
Decision Domain/Application compiles and its accepted semantic examples pass on current main structure.

### WP1 — Durable Decision persistence and selection — done

- register Decision-owned PostgreSQL migration after current main migrations;
- port append-only repository;
- enforce immutable history and same-subject/same-scope supersession;
- preserve explicit persistence-unknown/current-conflict outcomes;
- prove exact effective selection by subject + governance scope + asOf.

Exit:
one durable effective Decision can be recorded and selected without Access Policy or Web involvement.

### WP2 — Minimal end-to-end Access Policy integration — done

- evolve the Access Policy consumer port to request Decision by exact subject + proposal governance scope + proposal logical time;
- translate Decision BC output through the Access Policy-owned projection;
- fail closed on missing, ambiguous, expired or mismatched Decision;
- materialize only from effective `Allowed`;
- return `NotAllowed` as a valid business non-materialization result.

Exit:
proposal -> durable Decision -> Access Rule works on current main without `local-dev:allowed` for that path.

### WP3 — I16A Scoped Connectivity integration — done

- replace `DeferredConnectivityDecisionSummaryAdapter` with a real Decision summary adapter;
- preserve independent protected Decision detail authority;
- expose only the coarse Decision summary permitted by the Scoped Connectivity contract;
- keep unavailable/inaccessible/ambiguous data explicit rather than inventing Pending.

Exit:
the primary Connectivity workspace receives real `Allowed | NotAllowed | NoFinalDecision | Unknown` summary truth.

### WP4 — Decision participant HTTP/runtime boundary

- add authorized scope discovery for `DecideConnectivity` and `ReadConnectivityDecision`;
- add exact subject discovery/validation through ACC;
- expose direct final Allowed/NotAllowed recording;
- expose authorized list/detail with reason, provenance, validity and supersession;
- keep actor/time/authority provenance server-owned;
- do not introduce a pending approval queue.

Exit:
an authorized participant can record and inspect durable final Decisions through the current authenticated runtime.

### WP5 — Current Web integration

- implement Decisions as a specialized workspace under the current I16A information architecture;
- present final outcome, reason/provenance, validity and history;
- integrate contextual Request access with the real Decision path where product semantics permit;
- preserve Connectivity as the primary post-login workspace;
- do not resurrect old Compose-first navigation or roadmap preview shell.

Exit:
the current product journey can reach and explain real Decision behavior without exposing BC mechanics as mandatory navigation.

### WP6 — Local composition and demo closure

- seed usable Decide/Read authority for the local demo;
- seed or drive at least one durable Allowed and one NotAllowed journey;
- remove `local-dev:allowed` from normal local composition;
- retain deterministic adapters only as explicit test plumbing if still useful;
- prove Docker/public endpoint journeys against durable Decision persistence.

Exit:
the normal local product no longer depends on deterministic allow plumbing.

### WP7 — Closure

- run architecture/security/knowledge/harness gates relevant to this increment;
- verify no old PR #26 UI/composition/doc regression was reintroduced;
- absorb durable I16B outcome into canonical current-state/roadmap/API docs;
- remove this active plan;
- promote I17.

## Priority risks

### P0

- copying historical composition and losing I16A Scoped Connectivity behavior;
- trusting Decision without exact governance scope and logical time;
- leaking protected Decision detail through coarse Connectivity inventory;
- treating missing/ambiguous/persistence-unknown Decision as Allowed;
- reintroducing caller-controlled actor/authority provenance.

### P1

- supersession/concurrency allowing multiple trustworthy current Decisions;
- Decision expiry/supersession silently mutating existing Access Rules;
- old Web IA displacing the accepted resource-centric primary workflow;
- mixing browser-test-system refactoring into I16B product semantics.

### P2

- premature richer work-queue lifecycle before a concrete accepted owner/semantics exists;
- retaining duplicated historical docs instead of canonical current truth.

## Exit criteria

1. Durable Connectivity Decision runtime is present on current architecture.
2. Effective Decision selection is exact by subject + governance scope + asOf.
3. Access Policy consumes Decision through its own projection and fails closed.
4. Scoped Connectivity shows real coarse Decision summary without protected-detail leakage.
5. Authorized final Decision record/read HTTP and Web workflows are executable.
6. `local-dev:allowed` is absent from the normal local product journey.
7. Allowed/NotAllowed reason, provenance, validity and supersession remain explainable.
8. I16A resource-centric workflow and ownership boundaries remain intact.
9. Canonical docs are updated and this active plan is removed at closure.
10. I17 is promoted only after the above is complete.

## Blockers

None at the semantic/design level. Gate failures discovered during implementation must be fixed on this branch before advancing beyond the durable record/select slice.

## Next

Execute WP4 Decision participant HTTP/runtime boundary. Keep Web work out of scope until the authorized record/list/detail runtime is green.
