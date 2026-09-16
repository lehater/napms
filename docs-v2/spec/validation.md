# Validation specification

Status: SKELETON — M5 owns completion.

## Purpose

Define cheap deterministic checks first, then semantic/gate checks where automation is justified.

## Validation layers

1. structure — expected paths, identifiers, references and metadata;
2. syntax — PlantUML, YAML, OpenAPI/AsyncAPI, JSON Schema and other native formats;
3. consistency — references, ownership, traceability and duplicate canonical truth;
4. gate evidence — required/conditional artifacts applicable to the current change exist and are current;
5. implementation validation — contracts, tests, migrations and journey/E2E evidence agree with accepted upstream truth.

## M5 must define

Which checks run locally, in Harness, in CI and at gates; failure severity; applicability rules; generated-artifact checks; drift detection; and how checks consume the future machine-readable specification.

Prefer deterministic validation over agent judgment whenever the rule can be expressed mechanically.