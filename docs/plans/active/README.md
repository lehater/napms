# Active execution

Current: Web UI Component Composition Migration (`#90`).

Execution source: `docs/engineering/web-ui-component-composition-roadmap.md`.

Working branch: `docs/web-ui-component-composition-roadmap`.

Integration rule: execute M1-M7 as sequential commits on this single branch and keep PR #91 draft while work is accumulating. Perform one final hosted PR gate after the complete migration, then squash merge the branch into `main`.

Current stage: M1 — establish reusable generic composition base.

Recovery order for this increment:
1. `AGENTS.md`;
2. this file;
3. `web/AGENTS.md`;
4. `docs/ui/component-composition.md`;
5. `docs/ui/design-system.md`;
6. `docs/engineering/web-ui-component-composition-roadmap.md`;
7. only the feature files required by the current milestone.

Preserve accepted product/domain semantics. This increment changes Web UI ownership/composition boundaries, not business behavior.
