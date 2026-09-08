# Wave-1 semantic/data ownership — PLAN-027 WP-07

Status: `accepted G3 ownership/consistency baseline`.

Date: 2026-09-08.

| Information | Semantic owner | Wave-1 authoritative source | Consumers | History/provenance | Freshness/consistency |
|---|---|---|---|---|---|
| Access Rule ID, semantic identity, Active/Inactive, declarative properties, decision correlation | Access Policy | NAPM Access Policy module/store | proposal/materialization/export | state transitions + decision/business provenance | strong uniqueness/transactional mutation |
| action authority for scope/time | Authority Management | authority/responsibility source through port | proposal, mutation, export | effective assignment/provenance for action | evaluated for action/effective time; unknown fails permission |
| Application/Component/Deployment/DCS structure + time-qualified ComponentDeployment -> Resource references | Application Communication Catalogue | catalogue source through owned model/adapter | proposal, snapshot/export | stable identity/version; DCS revision and binding provenance | proposal requires exact structural validity; snapshot requires binding valid for as-of where temporal |
| Resource/Endpoint technical realization for stable Resource references | Resource Catalogue | resource catalogue source through owned model/adapter | snapshot/export | realization identity/version/effective validity/source | must be provably valid for snapshot/export as-of |
| Connectivity Decision result/reference | deferred Decision Domain | external/manual/Legacy/later provider through port | Access Policy | exact subject + opaque decision/provenance reference | subject immutable; no silent reinterpretation |
| logical Export Snapshot | application composition | assembled from owner facts | normalizer/serializer | correlations to every contributing fact + as-of | immutable per attempt; complete/coherent or assembly fails |
| Normalized Policy Export | application composition/output | derived from successful snapshot | human/downstream renderer | row -> Rule/decision/source correlations | complete for selected effective subset at declared as-of |

## Physical persistence rule

One physical database may host multiple module-owned datasets initially. This does not transfer semantic ownership. Cross-module direct table access is prohibited as an architectural shortcut; use module/port contracts so later extraction remains possible and invariants stay owned.

## External-source capture rule

Where an authoritative external source cannot answer historical/as-of queries directly, its adapter must provide an evidence-preserving capture/version mechanism sufficient for ADR-002. Exact storage/event/snapshot mechanism is PLAN-028 detail.

## Transition-source rule

Legacy may temporarily supply or bridge catalogue/decision facts only with explicit translation and provenance. Legacy tables/files/modules do not become target semantic owners.