# Active execution

Current: `PLAN-I26-traffic-analysis-checker.md`.

I25 Product Completion, Operator UX and Acceptance is complete and absorbed into canonical current-state/architecture/roadmap truth for the supported local target.

I26 Traffic Analysis Checker is the selected next product increment.

Accepted behavior:
- `docs/requirements/traffic-analysis-checker.md`;
- technical tuple (`source`, `destination`, `protocol`, `port`, `asOf`) is the Checker entry point;
- Checker composes domain/policy context, Network Context candidates, evidence-backed technical rules and resource ownership/contact information;
- current Network Context must not be presented as a proven ordered path;
- configured rules are read from stored Technical Access Evidence snapshots, never synchronously from live firewalls/devices.

Durable implementation roadmap:
- `docs/engineering/traffic-analysis-checker-roadmap.md`.

Active plan:
- `docs/plans/active/PLAN-I26-traffic-analysis-checker.md`.

Current next action: execute WP0 semantic re-entry for the I19 ordered-path versus Network Context candidate-set mismatch, then start the Checker Web fixture slice.

Canonical restart points:
- `docs/requirements/traffic-analysis-checker.md`;
- `docs/engineering/traffic-analysis-checker-roadmap.md`;
- `docs/plans/active/PLAN-I26-traffic-analysis-checker.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`.
