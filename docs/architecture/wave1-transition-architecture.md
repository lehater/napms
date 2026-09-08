# Wave-1 Transitional Architecture — PLAN-027 WP-09

Status: `accepted G3 transition baseline`.

Date: 2026-09-08.

## Principle

Target Architecture is the modular NAPM application described by ADR-001. Legacy SSSR_XLAM is evidence and, where required, a temporary transition source/bridge. Temporary mechanisms do not become target semantic ownership.

## Dependency treatments

| Legacy/dependency area | Target destination | Transition treatment | Status | Recovery/cutover principle | Retirement trigger |
|---|---|---|---|---|---|
| Word/Excel/XUIT request intake | domain-backed Access Rule Proposal | do not carry into Wave-1 target by default; add adapter only if migration/operations require it | deferred/optional bridge | old intake may remain operational outside target until selected | all required proposals originate through target/domain-backed channel or compatibility explicitly dropped |
| Legacy request/package identity and technical row model | Access Policy Rule semantic identity | translate only at migration boundary where mapping can be proven; never use as target identity | temporary migration adapter if needed | unmappable records remain diagnostic/manual, not silently converted | required authoritative Rules migrated/recreated with accepted provenance |
| Legacy SQL/application catalogue/resource facts | catalogue semantic ports | adapter/ACL translating source-specific schema to stable identity/version/effective facts | temporary or replaced by enterprise authoritative source | fail closed where target-required identity/validity cannot be established | authoritative target/enterprise source serves required contracts and Legacy adapter has no consumers |
| Legacy/external approval/decision indication | Connectivity Decision port | adapter/manual bridge emitting exact-subject Allowed/NotAllowed + reference only where correlation is trustworthy | temporary | uncertain/mismatched decision does not materialize Rule | selected durable Decision provider/process supplies stable contract |
| Legacy normalized/export behavior | target logical Export Snapshot + normalizer | no reuse of best-effort success semantics; use Legacy only as comparison/characterization evidence | replace | target export must pass G2 acceptance before cutover | target export accepted and downstream consumers no longer require Legacy output |
| firewall placement/routing split | future Network Enforcement Placement | keep outside Wave 1 | retained Legacy/external capability | no target claim of placement correctness | later selected wave implements/accepts placement capability |
| vendor config generation | future Configuration Rendering | keep outside Wave 1 | retained Legacy/manual/external capability | normalized export is handoff; no target rendering claim | later renderer accepted and consumers migrated |
| device/provider mutation | future Network Environment Operations | keep outside Wave 1 | retained operational process | no target execution claim | later execution capability accepted/cut over |

## Coexistence rules

1. Target Rule identity/state is authoritative only after target materialization; Legacy request/row IDs never overwrite it.
2. Every Legacy-derived fact entering a target semantic port retains source/provenance and is translated explicitly.
3. Missing or ambiguous mapping is diagnostic/manual work, not guessed target truth.
4. Target successful export uses G2 fail-closed semantics even while some inputs originate through Legacy adapters.
5. Legacy and target may coexist by capability; no big-bang replacement is required.
6. Adapter code belongs at infrastructure/integration edges and has an explicit retirement trigger.

## Cutover sequence

1. Stand up target semantic core and ports with test/double/manual adapters.
2. Establish trustworthy catalogue/authority/decision adapters needed for the selected operational environment.
3. Validate proposal -> Allowed -> Active Rule and normalized export against accepted examples.
4. Migrate/recreate only required authoritative policy where semantic mapping is demonstrable; keep ambiguous Legacy material outside authoritative target state.
5. Switch selected consumers to target Normalized Policy Export.
6. Retire Legacy intake/export dependencies independently when their replacement criteria are met.
7. Leave placement/rendering/execution on existing operational path until later waves explicitly replace them.

## Recovery

Because Wave 1 stops before device mutation, rollback primarily means stop target proposal/export consumption and continue the pre-existing downstream/manual/Legacy operational path. Target-created Rule history is not erased merely because a consumer rolls back; any cleanup/migration correction must preserve audit/provenance.