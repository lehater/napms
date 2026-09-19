# Current Harness consumer pilot

This directory is non-canonical integration metadata for evaluating the current
`lehater/harness` agent layer against NAPMS.

NAPMS canonical truth remains in `docs/**`:

- `docs/canonical-graph.yaml` owns artifact routing/dependencies;
- `docs/harness-core.yaml` owns the NAPMS engineering Authority/capability/consumer contracts;
- semantic truth remains in the canonical artifact paths referenced by that graph.

The pilot must not copy those graphs into a second persistent model. CI projects
them in memory through the external Harness adapter.

Two NAPMS-owned policy sources are evaluated without becoming new Harness truth:

- consumer/input contracts in `docs/harness-core.yaml` define which engineering
  knowledge capabilities downstream responsibilities need;
- `docs/engineering-knowledge-completeness.yaml` plus explicit artifact
  `knowledge_coverage` metadata define which domain subjects require coverage.

The pilot derives transient Design Profiles from those sources. A broad
consumer capability is not treated as proof of per-subject coverage; the coverage
adapter uses subject-scoped capability IDs for that check.
