# Active execution

Current: Web UI Component Composition Migration (`#90`).

Execution source: `docs/engineering/web-ui-component-composition-roadmap.md`.

Working branch: `docs/web-ui-component-composition-roadmap`.

Integration rule: M0-M7 execute as sequential commits on this single branch and PR #91 remains draft while work changes. After implementation/docs are complete, request one final hosted PR gate and squash merge only after all applicable checks pass.

Current stage: final integration gate. M0-M7 implementation is complete on the working branch; no intermediate merge has occurred.

Recovery order for this increment:
1. `AGENTS.md`;
2. this file;
3. `web/AGENTS.md`;
4. `docs/ui/component-composition.md`;
5. `docs/ui/design-system.md`;
6. `docs/engineering/web-ui-component-composition-roadmap.md`;
7. PR #91 hosted gate status/logs.

Next transition:
1. mark PR #91 ready for review;
2. inspect Web and Harness gate results/logs;
3. if a material fix is required, return to draft and fix on the same branch;
4. once gates pass, squash merge PR #91 into `main` and close #90.

Preserve accepted product/domain semantics. This increment changes Web UI ownership/composition boundaries, not business behavior.
