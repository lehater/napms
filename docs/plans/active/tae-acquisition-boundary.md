# TAE acquisition boundary clarification

Status: `active S2 affected-edge revalidation`.

## Goal

Record the accepted Technical Access Evidence acquisition/normalization ownership without turning collectors, device access or scheduling into new Bounded Contexts.

## Inputs

- accepted TAE Tactical model;
- current Context Map / Strategic model;
- ADR-021 provider interpretation boundary;
- stakeholder clarification 2026-09-15: TAE stores normalized technical facts; collection is initiated outside TAE by acquisition/collector application capabilities; NEO is not the read gateway.

## Scope

S2 only:

- TAE ownership of the canonical normalized evidence language/invariants;
- acquisition/collector capabilities as non-BC producers of TAE evidence;
- TAE non-ownership of polling/scheduling/retries/credentials/source transport;
- NEO remains controlled-mutation owner, not evidence-acquisition owner;
- consumers interpret TAE evidence without transferring semantic ownership to TAE.

The concrete shared device/provider access implementation between collectors and NEO is S3 Architecture and is not selected here.

## Exit criteria

- TAE Tactical model states the acquisition boundary explicitly;
- Context Map and strategic projection show acquisition/collector capability -> TAE rather than treating NEO as the read path;
- TAE/PPI and TAE/recognition interpretation responsibilities remain distinct;
- no new BC is introduced;
- affected S2 edge re-passes G2 with no P0/P1 contradiction.

## Blockers

None currently known.

## Next

Update the smallest canonical domain owners, revalidate the affected relationships, then park at S2 without entering Architecture or implementation.
