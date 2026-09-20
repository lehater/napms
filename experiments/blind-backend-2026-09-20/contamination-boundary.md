# Contamination boundary

## Allowed read set during blind reconstruction

- this experiment's `source-corpus.yaml`;
- current Harness repository and its reusable catalog/skills/research;
- NAPMS repository instructions/build metadata only when required for implementation-environment constraints and only if they do not encode prior product/domain/design semantics;
- new artifacts created under this experimental workspace.

## Forbidden semantic read set until freeze

Existing NAPMS outputs of engineering analysis/design, including:

- Bounded Contexts, context maps, domain/tactical models and design decisions;
- NAPMS Harness/Core/Engineering Graph projections and Authorities;
- application/system/module/component architecture;
- OpenAPI and other prior interface contracts;
- persistence models, transactions and migrations;
- security architecture, threat models and authorization design;
- observability/operability/reliability design;
- implementation/readiness/component design;
- verification/test design;
- UI/backend design contracts;
- source code and tests as semantic authority.

A file may be discovered by path/search for classification purposes without importing its semantic content. If a search snippet accidentally exposes derived semantics, those semantics are tainted and must not be used in the blind design unless independently present in `source-corpus.yaml`.

## Contamination incidents

- CI-001: repository search exposed fragments from current S0/domain/design files while locating source candidates.
  Disposition: all such semantic details are excluded. Only statements independently admitted into the frozen source corpus may influence reconstruction.

## Rule after freeze

The blind design becomes immutable with respect to old NAPMS. Comparison may classify differences but may not repair the frozen result retrospectively.
