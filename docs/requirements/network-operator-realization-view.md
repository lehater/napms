# Network Operator Realization View

Status: `accepted I25 product-completion requirement`.

Date: 2026-09-10.

## Purpose

Give an authenticated network/security operator one truthful read view of how the current desired Access Policy relates to enforcement placement, configured technical evidence, reconciliation, rendered configuration and controlled execution evidence.

The view is an owner-preserving projection. It is not a new authoritative business object and does not transfer ownership from Access Policy, NEP, TAE, APR or NEO.

## Operator question

For one governance scope and logical time, the product must be able to answer:

```text
What access is desired?
Where would it be enforced?
What configured evidence do we actually have?
Does configured state match desired state?
What target configuration can be rendered?
What controlled operation evidence actually exists?
Why is any stage unavailable or unknown?
```

## Required projection

For a requested governance scope and `as_of`, return one overall projection containing:
- desired-policy derivation status and contributing Access Rule references;
- selected enforcement targets and placement provenance where derivation is available;
- configured-evidence identity/provenance only when an actual configured evidence selection exists;
- reconciliation status and required semantic change only when both configured evidence and a complete managed-scope contract are available;
- rendered artifact metadata/content only when APR can render the desired target semantics;
- NEO operation identity/outcome/pre/apply/post evidence only when an actual operation result exists for the requested target/artifact context;
- explicit gaps/diagnostics for unavailable, ambiguous or unknown stages.

## Availability semantics

Absence must not be converted into a positive domain fact.

The presentation layer may use these projection-level availability states:
- `Available`: authoritative/derived data required for the stage is present and the stage produced a determinate result;
- `NotAvailable`: no selected input/result exists for the stage in the current local runtime, without implying that the underlying real-world fact is absent;
- `Unknown`: required input exists but cannot be interpreted/selected deterministically, including ambiguous or incomplete knowledge.

Examples:
- no selected configured TAE evidence => reconciliation `NotAvailable`, not `Satisfied` and not `NoDrift`;
- incomplete managed-scope contract => reconciliation `Unknown`, not `Satisfied`;
- rendered artifact with no NEO operation => operation `NotAvailable`, not `Verified`;
- transport acceptance without matching post-check => operation uses the NEO-owned non-Verified outcome, never presentation-inferred success.

## Authority

Reading this operator view requires explicit read admission. Existing business actions remain owned by their contexts; reading the view does not grant mutation authority.

I25 must not introduce generic IAM roles merely to label a user as a network operator. Runtime admission should use an explicit action/scope check through Authority Management.

## Ownership and provenance

- Access Policy owns Rule identity/state and effective desired policy.
- NEP owns enforcement placement knowledge/selection.
- TAE owns recorded technical evidence.
- APR owns desired/configured reconciliation and rendering semantics.
- NEO owns operation identity/outcome/pre/apply/post evidence.
- the operator view owns only composition/presentation state.

Every available stage must retain enough owner reference/provenance to explain its source. Cross-context data is not copied into a new authoritative table.

## Local-first runtime

The supported local target may use deterministic technical fixtures/stubs to make the complete product journey executable where no real device/source is selected. Such fixtures are explicitly demo/bootstrap data and prove only NAPMS semantics.

No real Cisco transport, external CMDB/IdP, enterprise source or HA infrastructure is required by this requirement.

## First-slice constraints

The first executable operator read slice should be deliberately narrow:
- one governance scope;
- one logical `as_of`;
- read-only;
- no bulk execution;
- no generic CRUD for NEP/TAE/APR/NEO;
- no new authoritative persistence;
- no inference of configured or executed state from desired/rendered state.

## Acceptance

The requirement is satisfied when executable tests prove:
- available desired/placement/rendering facts preserve owner references;
- missing configured-evidence selection yields explicit `NotAvailable` reconciliation;
- incomplete/ambiguous configured inputs yield `Unknown` rather than a convenient conclusion;
- absent operation evidence yields `NotAvailable` rather than `Verified`;
- supplied real NEO result is represented without reinterpreting its outcome;
- HTTP/Web presentation cannot broaden authority or semantic certainty beyond the projection.
