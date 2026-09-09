# PLAN-017 — Technical Access Evidence Core

Status: `active`

Date: 2026-09-09.

## Goal

Establish the accepted Tactical DDD and first durable core for **Technical Access Evidence (TAE)** so NAPMS can persist and query source-qualified technical access material without treating evidence as authorization, desired policy, domain-valid access, enforcement placement or reconciliation truth.

The first useful end-to-end result is intentionally narrow:

```text
one source-qualified observation/import
    -> exact source-neutral normalization
    -> immutable evidence set + entries with provenance/time
    -> durable persistence
    -> explicit evidence query/readback
```

I18 Technical-to-Domain Access Resolution remains downstream.

## Inputs

- `docs/domain/strategic-model.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/ubiquitous-language.md`;
- `docs/domain/capabilities.md`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/process/domain-change-protocol.md`;
- `docs/process/decision-protocol.md`.

## Accepted starting truth

- Technical Access Evidence is already an accepted Bounded Context.
- It owns the claim that source X provided, or allowed NAPMS to derive, technical access material Y for scope/time T.
- Evidence kinds are `Configured | TrafficDerived | Imported`.
- A Technical Access Entry carries normalized technical predicate facts plus source/scope/time/provenance.
- Source-specific parsing and collection are outside TAE bounded-context meaning.
- Technical evidence is not authorization, desired policy or proof that an interaction is domain-valid.
- Technical-to-domain resolution belongs to Access Policy Realization in I18.

## Work packages

### WP0 — Tactical DDD and observable-contract closure — done

The proposal exists in:
- `docs/domain/technical-access-evidence/tactical-model.md`;
- `docs/requirements/technical-access-evidence-core.md`;
- `docs/requirements/technical-access-evidence-acceptance-examples.md`;
- `docs/architecture/technical-access-evidence-boundary.md`.

The proposal resolves:
- Evidence Set identity/lifecycle;
- Entry identity and duplicate preservation;
- evidence source/scope/capture references;
- `Configured | TrafficDerived | Imported` invariants;
- normalized technical predicate value semantics;
- source evidence time versus NAPMS recording time;
- provenance minimum;
- immutable retry/conflict semantics;
- explicit deferral of freshness / coverage / confidence;
- all-or-nothing first-slice normalization;
- source-adapter and dependency boundary.

Do not introduce:
- authorization or desired-policy conclusions;
- technical-to-domain mapping;
- enforcement placement;
- reconciliation status;
- vendor rendering/execution;
- generic ingestion-platform abstractions.

Exit:
the Tactical DDD + requirements/examples + architecture boundary are accepted together, with no blocking identity/time/provenance/normalization unknowns.

### WP1 — Domain/Application/Ports core — done

- implement framework-free TAE Domain and Application packages;
- encode WP0 invariants;
- expose TAE-owned persistence/query ports;
- accept only source-neutral drafts from outer source adapters;
- keep wall-clock/source/provider mechanics outside Domain;
- add architecture/core tests before infrastructure expansion.

Exit:
one evidence set can be constructed, validated, retried idempotently and queried through in-memory/domain-level ports without infrastructure.

### WP2 — PostgreSQL persistence — done

- add TAE-owned migration and repository;
- preserve immutable evidence history and source provenance;
- enforce source + capture identity;
- resolve identical retries versus conflicting same-capture content;
- fail closed on persistence uncertainty;
- integrate migration ordering without cross-module SQL.

Exit:
one accepted evidence set and its entries round-trip through PostgreSQL without loss of semantic/provenance facts.

### WP3 — Minimal source-adapter/runtime proof — done

- use the smallest source-adapter/application boundary justified by the accepted contract;
- provide an explicit local/import adapter as outer plumbing;
- preserve source provenance ownership;
- return normalization ambiguity/failure explicitly;
- do not expose a public human HTTP mutation/read API until authority/workflow semantics are accepted;
- avoid Web UI unless a concrete operator workflow is required to prove I17 exit.

Exit:
local composition can ingest/import and query durable TAE through an explicit source-qualified path.

### WP4 — End-to-end proof and closure

- prove Configured/TrafficDerived/Imported distinctions where supported by accepted examples;
- prove evidence never grants Access Policy authority;
- prove no I18 resolution/reconciliation semantics leaked into I17;
- run core/postgres/docker/harness/knowledge gates as applicable;
- absorb durable semantics into canonical domain/requirements/architecture/engineering truth;
- remove this active plan and promote I18 only after I17 exit criteria hold.

## Priority risks

### P0

- treating observed/configured/imported technical material as authorization or desired truth;
- losing source/time/provenance while normalizing;
- inventing domain interaction identity inside TAE;
- collapsing provider/parser artifacts into TAE semantic identity;
- implementing freshness/coverage/confidence with undefined business meaning;
- silently persisting partial normalized material as a complete source capture.

### P1

- unstable Evidence Set/Entry identity causing duplicate or mutable history;
- conflating source evidence time with NAPMS recording time;
- normalization broadening/narrowing technical predicates;
- allowing source-specific ordering/action semantics to become universal;
- creating human-facing authority semantics merely to expose a convenient API.

### P2

- premature generic ingestion framework;
- Web workspace before a proven operator need;
- pulling I18/I19/I20 semantics forward for convenience.

## Exit criteria

1. TAE Tactical DDD defines Evidence Set, Entry, source/provenance, time and normalized predicate semantics.
2. `Configured | TrafficDerived | Imported` are represented without implying authorization.
3. Freshness/coverage/confidence are precisely accepted or explicitly deferred with revisit triggers.
4. Domain/Application core is framework-free and source/provider mechanics stay behind adapters.
5. TAE-owned PostgreSQL persistence can store/query accepted evidence without semantic loss.
6. At least one explicit local/import source path proves ingestion and readback.
7. Failures/ambiguity are explicit; best-effort partial normalization is not silently successful.
8. No technical-to-domain resolution, enforcement placement, reconciliation, rendering or device execution is introduced.
9. Canonical truth is updated and this active plan is removed at closure.
10. I18 is promoted only after the above is complete.

## Blockers

None for WP4.

WP3 checkpoint evidence on `4da9e6519da1764d97a6a1c56391afc45fdadf04`:
- strict local JSON import adapter implemented outside TAE Domain/Application;
- adapter fixes source namespace to `local-import` and emits only `Imported` evidence;
- tcp/udp/IP protocol numbers, address/port constraints and explicit EvidenceTime normalize to accepted source-neutral TAE values;
- unknown/unsupported fields, duplicate JSON keys and unrepresentable service semantics fail before persistence;
- protocol Any + constrained ports remains rejected by Domain invariant;
- dedicated TAE PostgreSQL composition exposes record/get use cases without extending the general HTTP request scope;
- durable integration proves import -> normalize -> record -> new dedicated TAE scope -> readback -> identical retry resolves same immutable set;
- integration proves TAE record does not create Access Rules;
- hosted core gate #98 — success, 454 passed / 105 deselected;
- hosted postgres persistence gate #83 — success, 105 passed;
- hosted docker local runtime gate #59 — success;
- hosted harness gate #103 — success;
- hosted knowledge gate #67 — success.

No public TAE HTTP/Web, human Authority Management workflow, provider/device SDK or I18/I19/I20 semantic leakage exists.

## Next

Execute WP4 only: final end-to-end proof, architecture review, canonical knowledge absorption, final hosted gates, remove the active I17 plan and promote I18 only if all I17 exit criteria hold.
