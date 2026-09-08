# NAPMS initial extraction provenance

Date: 2026-09-08.

NAPMS was created as a curated greenfield product repository from accepted target knowledge in `lehater/sssr_xlam`.

## Source points

- accepted pre-implementation baseline on old repository `main`: `d1abb6fac6b4147e28abce9c934ceffbba25570f`;
- Access Policy I1 implementation source branch: `implementation/wave1-i1-core`;
- accepted Strategic DDD baseline: `DDD-BDM-010`.

## Extraction rule

Copied:
- accepted current product requirements and acceptance examples;
- living Strategic/Tactical DDD meaning;
- accepted architecture and ADRs;
- engineering policies required before infrastructure;
- new Access Policy core and executable tests.

Not copied:
- Legacy source/code/data artifacts;
- old FastAPI/MSSQL prototype;
- reverse-engineering/reconstruction evidence;
- intermediate/superseded DDD scorer artifacts;
- historical execution plans and harness-specific methodology.

The extraction is semantic, not a Git-history migration. NAPMS is authoritative for future product code and current target documentation; the old repository remains provenance/evidence for reconstruction history.
