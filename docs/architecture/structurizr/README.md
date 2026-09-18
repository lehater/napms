# NAPMS architecture workspace

`workspace.dsl` is the canonical C4 structural/deployment model. It does not own domain semantics, HTTP schemas or relational schema details.

Run `make architecture` to regenerate all current diagram projections, start a loopback PlantUML server on port 8081 and Structurizr Local on port 8080. The workspace then shows both native C4 views and generated image views.

Native C4 views:
- `SystemContext`
- `Containers`
- `BackendComponents`
- `MVPDeployment`

Generated views:
- DDD Context Map and Strategic Collaboration Map;
- Resource Catalogue domain and process;
- ACC, Application Deployment, Business Connectivity and Access Policy domain projections;
- first-MVP policy-export journey;
- physical persistence ERD.

Generated PlantUML lives under `docs-generated/architecture/` and is disposable. Its semantic owners are listed in `docs/canonical-graph.yaml`; never edit generated files to change design.

Use `make design-sync` to regenerate projections without starting the viewer. Use `make architecture-check` for Structurizr validation with the same generated inputs.

Manual layout state may be stored in `workspace.json`. Styling/layout are presentation only. Structural C4 truth stays in `workspace.dsl`.
