# Current Harness consumer pilot

This directory is non-canonical integration metadata for evaluating the current
`lehater/harness` agent layer against NAPMS.

NAPMS canonical truth remains in `docs/**`:

- `docs/canonical-graph.yaml` owns artifact routing/dependencies;
- `docs/harness-core.yaml` owns the NAPMS engineering Authority/capability/consumer contracts;
- semantic truth remains in the canonical artifact paths referenced by that graph.

The pilot must not copy those graphs into a second persistent model. CI projects
them in memory through the external Harness adapter and derives a transient Design
Profile from the existing NAPMS consumer contract.
