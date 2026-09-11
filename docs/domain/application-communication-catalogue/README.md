# Application Communication Catalogue domain

Canonical Tactical DDD for the current implemented catalogue write/read model:

- `tactical-model.md` — I31 Application Definition / Component / Interaction Definition / Application Deployment / Deployment Interaction semantics, lifecycle, interaction-scoped Resource binding and downstream compatibility projection.

Canonical supporting decisions and product contracts:

- `../../decisions/ADR-012-application-definition-deployment-model.md` — Application Definition / Application Deployment boundary, selectable interaction subset and interaction-scoped Resource bindings;
- `../../decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md` — compatibility projection, reference/metadata semantics and active-dependency rules;
- `../../requirements/application-catalogue-target.md` — current observable Application Catalogue behavior;
- `../../architecture/application-catalogue-target-boundary.md` — current I31 architecture boundary;
- `../../ui/application-catalogue-target.md` — current catalogue UX and scaling rules.

Pre-I31 Component Deployment, DCS revision and Deployment Resource Binding facts remain valid legacy ACC/downstream truth where historical references require them. They are compatibility/history concepts, not the current Application authoring model.

Strategic ownership remains in:

- `../strategic-model.md`;
- `../semantic-ownership.md`;
- `../ubiquitous-language.md`.
