# Operability boundary validation — NAPMS

Status: research evidence; not canonical methodology.

## Purpose

Validate the Harness OPERABILITY-DESIGN responsibility boundary on a runtime shape materially different from the Nutrition pilot. This experiment uses accepted NAPMS design only. Product implementation and legacy implementation mechanics are not design evidence.

## Runtime shape

NAPMS first MVP is a long-running HTTP backend in a modular-monolith topology with browser requests, server-side session identity and PostgreSQL as a required runtime dependency. System Architecture explicitly excludes asynchronous messaging for this MVP.

This differs materially from the Nutrition local synchronous CLI pilot: request correlation crosses an HTTP boundary, the process has persistent lifecycle state, and liveness/readiness have an operational consumer.

## Observed ownership split

The experiment confirms that "runtime design" is too broad to be one Authority.

- Product/domain/application own accepted outcomes and complete-vs-Unresolved semantics.
- System Architecture owns long-running process topology, HTTP/application boundary, in-process module interaction and the absence of asynchronous messaging.
- Interface Design owns HTTP/public failure representation.
- Security owns session identity, admission and disclosure constraints.
- Data Design owns PostgreSQL persistence semantics.
- Product/Quality own whether numeric SLI/SLO targets exist. For this MVP numeric latency, throughput, availability and scale targets are explicitly not required.
- Operability owns correlation, runtime completion evidence, dependency diagnosability and liveness/readiness evidence.
- Implementation owns libraries, formatters, framework hooks, private exception classes and physical telemetry realization.

## Atomicity result

### Semantic cohesion

Correlation, completion evidence, dependency failure visibility and health-state evidence all answer one public question: what must be observable to diagnose accepted runtime behavior and determine whether the runtime is able to serve its accepted purpose.

### Independent change

The evidence schema/signal projection can evolve without changing domain outcomes, HTTP semantics, persistence ownership or logging/telemetry technology.

### Public producer/consumer contract

Upstream inputs are accepted architecture, interface, security, data, quality and application semantics. Output is `engineering.operability.runtime-evidence`, consumed by Implementation Design, Verification Design and IMPLEMENTATION.

Result: PASS for OPERABILITY-DESIGN when kept narrow.

## Important negative results

The experiment does not justify Logging Design, Error Design, Configuration Design, Resilience Design or a broad Runtime Design Authority.

Logging remains a signal projection of runtime evidence. Failure semantics remain distributed among domain/application/interface/architecture owners. Configuration source/precedence/mutability would need its owning architecture/interface/security decision before Operability consumes it. Retry/backoff remains a semantic runtime policy decision and cannot be introduced by Operability or coding defaults.

## Long-running-service-specific evidence

Unlike Nutrition, NAPMS demonstrates that liveness/readiness can belong to Operability without moving dependency topology into it:

- liveness answers whether the process/runtime is alive and must not traverse PostgreSQL;
- readiness answers whether the backend can serve accepted PostgreSQL-backed use cases and therefore reflects that required dependency;
- the fact that PostgreSQL is required comes from Architecture/Data Design, not from Operability.

This separation is the strongest second-case evidence for the Authority boundary.

## SLI/SLO and alertability

NAPMS has an explicit product decision that numeric latency, throughput, availability and scale targets are not required for the first MVP. Therefore Operability must not invent production SLOs, metrics infrastructure, dashboards or alerts. If Product/Quality later accepts such objectives, Operability becomes the owner of the runtime evidence needed to measure/diagnose them, while alert policy may be a downstream operational consumer.

## Configuration result

No independent Configuration Authority is demonstrated. Operability explicitly refuses to create environment variables, config files, precedence, hot reload, feature flags or secret sources. A future configuration control plane could justify an independent boundary, but this project does not provide that evidence.

## Resilience result

No general retry/backoff Authority is demonstrated. Automatic retry can change authoritative mutation semantics under uncertain persistence outcomes, so retryability must be accepted by the owner of the operation/runtime policy. Operability records/diagnoses the resulting state; it does not authorize recovery behavior.

## Core impact

No Harness Core entity or algorithm change is required. Authority/Capability/CanonicalArtifact/Question/prerequisite closure already express the result.

## Cross-project conclusion

Nutrition (local synchronous CLI) and NAPMS (long-running HTTP modular monolith) both produce the same residual responsibility boundary despite different runtime shapes.

The common capability is not "observability tooling"; it is **runtime evidence / diagnosability**.

This is sufficient evidence to promote the refined OPERABILITY-DESIGN responsibility from a one-project hypothesis to a reusable conditional Authority model. It is not evidence that every project must instantiate it. Projects with trivial runtime evidence needs may merge the responsibility into System Architecture or Verification Design according to the catalog merge guidance.

A distributed/multi-process case would still be useful to validate trace propagation and dependency fan-out, but is no longer required to establish the atomic Authority boundary itself.
