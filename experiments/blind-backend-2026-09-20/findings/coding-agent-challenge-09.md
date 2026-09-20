# Coding-Agent Challenge 09

Status: FAILED — runtime/data completion details require repair

## CAC-019 — P1 — materialization evaluationAt clock not tied to database snapshot

The design requires one evaluation time coherent with one PostgreSQL REPEATABLE READ snapshot but did not pin the clock source/order.

Repair:
- `runReadSnapshot` starts a read-only REPEATABLE READ transaction;
- its first database statement establishes the snapshot and returns database `transaction_timestamp()` as `evaluationAt`;
- this exact timestamp is used for PolicyRule effective-window evaluation and response output;
- application wall clock is not independently sampled for materialization effectiveness.

## CAC-020 — P1 — idempotency replay persistence/retention ambiguous

`response_body_or_result_ref` allowed an implementation to reconstruct a replay from current state, which could differ from the original committed response.

Repair:
- idempotency record stores exact canonical response JSON bytes (excluding current correlation header), original status, Location and ETag needed for replay;
- replay returns those exact committed semantics plus the retry request's correlation id;
- no reconstruction from current mutable aggregate state;
- idempotency records have no expiry/TTL in selected MVP because no accepted idempotency window exists;
- later retention/expiry requires an explicit Data/Interface change.

## CAC-021 — P1 — migration execution/startup ownership unspecified for multiple replicas

A server that auto-applies migrations on every startup needs cross-instance coordination; an external migrator needs a different deployment contract.

Repair:
- the same binary exposes a dedicated `migrate` mode/command and a `serve` mode;
- `migrate` connects to PostgreSQL, acquires an exclusive database advisory lock, validates immutable migration checksums and applies pending ordered migrations transactionally;
- concurrent migrators serialize on that lock;
- `serve` never applies pending migrations; before listener start it verifies the database is exactly at the expected migration set/checksums and fails startup on missing/pending/unknown/changed migration state;
- fresh-start verification runs migrate first, then serve;
- no CLI option overrides application configuration values; the mode selects process action only.

## CAC-022 — P1 — JWT kid behavior left to library

Repair:
- bearer JWT must contain a non-empty string `kid`;
- missing/wrong-type kid -> 401 malformed/invalid credential with no refresh;
- unknown kid may trigger the bounded single-flight refresh;
- if refresh succeeds and the kid is still absent -> 401 invalid credential;
- if refresh cannot complete and validity cannot be established -> 503 under existing dependency rules.

## CAC-023 — P2 — Engineering Policy contradicted canonical port normalization

One line required sorted/merged canonical ranges while another said non-overlapping representation was optional.

Repair: canonical sorted, merged overlapping/directly adjacent ranges are mandatory at the domain/persistence/API boundary.

Freeze remains prohibited until the repairs propagate and Challenge 10 passes.
