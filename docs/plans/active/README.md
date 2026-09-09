# Active execution

Current: `PLAN-018-i18-technical-domain-access-resolution.md`

Goal: implement I18 Technical-to-Domain Access Resolution as one consumer-independent APR capability over effective RC + ACC knowledge.

Current task: WP2 — RC + ACC + TAE outer adapters.

Working mode: implement-slice + architecture-review + execute-work-package.

## Working set

Read first:
- `docs/architecture/access-policy-realization-resolution-boundary.md`
- `src/napms/access_policy_realization/domain/model.py`
- `src/napms/access_policy_realization/application/ports.py`
- current RC/ACC/TAE Domain/Application contracts needed by adapters only.

## Recovery facts

- WP0 semantic gate is closed.
- WP1 pure APR core is implemented and locally exercised across Exact/Covered/Partial/Ambiguous/Unresolved/Unknown scenarios.
- APR Domain/Application import no RC/ACC/TAE peer contexts.
- DomainKnowledgePort is predicate-aware.
- Current ACC projection protocol tokens are representation facts; APR Domain uses exact IP protocol numbers.
- Unsupported address-relevant ACC transport must become explicit Unknown; unrelated disjoint facts must not poison the result.
- TAE adapter direction is TAE -> APR projection only; RecordedAt never supplies asOf.

## Blockers

None for WP2.

## Gate

WP2 passes only when:
- RC + ACC adapter consumes owner APIs/repositories rather than peer SQL;
- effective bindings/realizations are evaluated at explicit asOf;
- tcp/udp exact translation is explicit and unsupported relevant tokens fail closed;
- predicate-disjoint unsupported DCS facts do not create global Unknown;
- TAE projection preserves evidence provenance without importing APR into TAE;
- no APR persistence/public workflow/I19/I20 leakage appears.

## Next

Implement and review WP2, then open WP3 integration proof only if adapter tests are green.
