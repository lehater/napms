# NAPMS Harness Scenario Suite experiment

This branch validates NAPMS as an independent real-project consumer of the
generic Harness Scenario Suite.

The ordinary NAPMS control plane remains unchanged: `.harness-version` still
pins the immutable mainline Harness SHA used by `make design-check`.

The experiment workflow separately checks out
`lehater/harness:experiment/scenario-suite` and runs only generic built-in
Scenario Suite drivers against NAPMS-owned canonical data.

Initial proofs:

- current canonical graph/projection alignment;
- BACKEND-IMPLEMENTATION remains COMPLETE;
- FRONTEND-IMPLEMENTATION remains READY at the current two-capability HCD
  frontier;
- an injected hidden cross-Authority project dependency is rejected;
- an injected provider Authority mismatch is diagnosed by Graph Doctor.

No scenario mutates canonical repository files; mutations are in-memory copies.
