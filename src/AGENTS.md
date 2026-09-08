# Source-code scope

Apply root `AGENTS.md` first.

## Dependency direction

- Domain depends only on language/runtime primitives and domain code.
- Application depends on Domain and port abstractions owned by the consuming module.
- Infrastructure/adapters depend inward; core never imports them.
- Framework, persistence, transport, configuration, logging and DI-container types do not enter Domain.

## Change order

For semantic behavior changes:
1. confirm the accepted requirement/domain meaning;
2. update the highest affected truth layer when needed;
3. change Domain/Application/Ports;
4. add/update executable tests;
5. run `make test`.

Do not add production infrastructure while the active plan keeps the infrastructure gate closed.

## Review

Before considering a slice complete, check:
- invariants and semantic identity;
- fail-closed outcomes;
- idempotency/concurrency claims are no stronger than tested;
- port ownership and dependency direction;
- P0/P1 findings are closed.
