# Application Communication Catalogue domain

## Accepted target

The accepted ACC target is defined by:

- `../../decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md` — normative domain decision: Component is the deployment unit; interaction traffic is an atomic immutable contract; ACC publishes the concrete directed-interaction identity;
- `target-model.md` — canonical target domain model and ERD;
- `../../requirements/application-catalogue-domain-target.md` — target requirements and acceptance invariants;
- `../../engineering/application-catalogue-domain-migration-roadmap.md` — implementation migration gates.

The target is **accepted but not yet implemented**. Implementation work must conform to ADR-015 and the target model rather than extending the I31 `ApplicationDeployment` / `DeploymentInteraction` model.

## Current implemented runtime

`tactical-model.md` describes the currently implemented I31 write/read model. It remains current-state/runtime documentation until migration is completed; it is **not** the target domain design.

Historical I31 decisions and product/architecture contracts are retained to explain the existing implementation:

- `../../decisions/ADR-012-application-definition-deployment-model.md`;
- `../../decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`;
- `../../requirements/application-catalogue-target.md`;
- `../../architecture/application-catalogue-target-boundary.md`;
- `../../ui/application-catalogue-target.md`.

ADR-015 supersedes those documents where they prescribe `ApplicationDeployment`, `DeploymentInteraction`, interaction-scoped Resource sets, or the I31 compatibility projection as future target semantics.

Pre-I31/I31 Component Deployment, DCS revision and Deployment Resource Binding facts remain valid runtime/history where existing references require them. Migration must preserve referenced historical truth.

Strategic ownership remains in:

- `../strategic-model.md`;
- `../semantic-ownership.md`;
- `../ubiquitous-language.md`.
