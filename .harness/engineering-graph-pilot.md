# Engineering Graph v0 pilot

This branch projects existing NAPMS engineering policy into the experimental
Harness Engineering Graph without creating a second persistent canonical graph.

Inputs remain NAPMS-owned:

- `docs/canonical-graph.yaml` — artifact/dependency routing;
- `docs/harness-core.yaml` — Authority, capability and consumer contracts;
- `docs/engineering-knowledge-completeness.yaml` plus explicit
  `knowledge_coverage` — subject coverage policy.

`.harness/derive_engineering_graph.py` composes those sources into one transient
producer/consumer Engineering Graph and augments the transient Core projection
with subject-scoped coverage capabilities.

The pilot checks:

- IMPLEMENTATION -> COMPLETE;
- missing Resource Detail UI -> one producer CREATE;
- missing Resource Catalogue tactical coverage -> one scoped CREATE;
- unresolved Interface Question -> WAIT.

No NAPMS canonical policy is copied into a new persistent Harness graph.
