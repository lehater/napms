# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

## Completed milestones

- M1 — complete in `f0e281e`.
- M2 — complete in PR #74, squash merge `91eb009c2338697458ba3874836c93cc044f753a`.
- M3 — complete in PR #75, squash merge `18787e3f790368dec8d57078b47c7b6454e85b5d`.
- M4 — complete in PR #76, squash merge `a2caf39587c111fe97341686ff92fbeb9d30599d`; all required hosted gates passed.

## M5 — Capability-oriented internals

Status: `Application Catalogue implementation complete; awaiting architectural review` on branch `refactor/m5-capability-internals`.

M5 refines only application layers where actual change locality shows independent responsibilities. File size alone is not a reason to split. M5 is one milestone PR; each accepted context refinement is an atomic commit and hosted gates run once at the end.

### First accepted slice — Application Catalogue

Application Catalogue has sufficient evidence for capability decomposition: its application layer contains separate curation, discovery/read, and accepted I31 Application Catalogue Target responsibilities. The split is intentionally coarse; do not create one folder per use case.

Target application shape:

```text
contexts/application_catalogue/application/
  __init__.py
  ports.py
  curation/
  discovery/
  target/
```

`curation/` owns the pre-I31/general catalogue mutation use cases still retained for compatibility and shared catalogue truth.

`discovery/` owns catalogue/detail/participant/interaction discovery and resolve-oriented reads.

`target/` owns the accepted I31 Application Catalogue Target application contract and use cases. `target` is accepted requirement terminology, not a temporary generic bucket.

Mapping:

```text
curation.py                       -> curation/create_application.py
curation_mutation.py              -> curation/mutation.py
application_structure_curation.py -> curation/application_structure.py
component_structure_curation.py   -> curation/component_structure.py
dcs_curation.py                   -> curation/dcs.py
deployment_curation.py            -> curation/deployments.py
binding_curation.py               -> curation/bindings.py
structure_curation.py             -> curation/structure.py

curation_detail.py                -> discovery/catalogue_detail.py
curation_read.py                  -> discovery/catalogue.py
describe_interactions.py          -> discovery/describe_interactions.py
list_interactions.py              -> discovery/list_interactions.py
participant_discovery.py          -> discovery/participants.py
resolve.py                        -> discovery/resolve.py

target_curation.py                -> target/curation.py
target_metadata_curation.py       -> target/metadata.py
target_structure_curation.py      -> target/structure.py
target_binding_curation.py        -> target/bindings.py
target_lifecycle.py               -> target/lifecycle.py
target_retirement.py              -> target/retirement.py
target_read.py                    -> target/read.py
target_selection_read.py          -> target/selection.py
target_ports.py                   -> target/ports.py
```

Rules:
- preserve behavior and public application types; this slice is structural only;
- `application/ports.py` remains the context-wide application contract surface used by more than one capability;
- `target/` may depend on root `ports.py` and domain, but must not import `curation/` or `discovery/`;
- `curation/` and `discovery/` must not import `target/`;
- presentation/infrastructure/bootstrap consumers update directly to final imports; no compatibility facades;
- move matching unit tests into `tests/application_catalogue/curation`, `discovery`, or `target` where the ownership is unambiguous; integration tests remain under `tests/integration`;
- add architecture guards for the explicit capability boundaries.

Implementation evidence:
- application root contains only `__init__.py`, `ports.py`, and the three capability packages;
- all mapped flat modules are absent and all consumers use final imports;
- cross-capability dependency guards enforce the accepted direction;
- targeted Application Catalogue tests: 151 passed;
- architecture tests: 67 passed;
- `make test`: 810 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed.

### Re-evaluation after ACC

Resource Catalogue is the only current secondary candidate: `curation`, `realization`, and `responsibility/scope` appear to be separate change axes. Do not move it until the ACC slice is reviewed. Access Policy and the remaining contexts/workflows currently do not justify additional package depth.

## Exit criteria

M5 closes when every accepted capability split is behavior-preserving, newly explicit capability boundaries are protected by architecture/locality tests, full local/integration checks pass, and one final M5 PR passes required hosted gates.

## Blockers

None.

## Next

Review the Application Catalogue capability slice. Do not start Resource Catalogue, M6, or create a PR before that review.
