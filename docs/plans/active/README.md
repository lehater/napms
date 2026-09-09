# Active execution

Current: `PLAN-018-i18-technical-domain-access-resolution.md`

Goal: implement I18 Technical-to-Domain Access Resolution as one consumer-independent APR capability over effective RC + ACC knowledge.

Current task: WP1 — Domain/Application/Ports core.

Working mode: implement-slice + execute-work-package.

## Working set

Read first:
- `docs/domain/access-policy-realization/tactical-model.md`
- `docs/requirements/technical-domain-access-resolution-acceptance-examples.md`
- `docs/architecture/access-policy-realization-resolution-boundary.md`
- `docs/plans/active/PLAN-018-i18-technical-domain-access-resolution.md`

Expand only if needed into:
- current TAE normalized predicate model for adapter compatibility only;
- architecture tests and package patterns;
- RC/ACC contracts after the WP1 core gate.

## Recovery facts

- WP0 Tactical DDD + requirements/examples + architecture boundary are accepted.
- Pairwise correspondence is Exact | Covers | CoveredBy | PartialOverlap | None.
- Resolution status is Exact | Covered | Partial | Ambiguous | Unresolved | Unknown.
- Supported complete first algebra requires an exact IP protocol number.
- Protocol Any remains explicit Unknown; no guessed protocol expansion is permitted.
- Remainder is exact set difference for supported complete knowledge.
- APR Domain/Application own consumer ports and import no RC/ACC/TAE peer types.
- No APR persistence/runtime, I19 placement or I20 reconciliation is in scope.

## Blockers

None for WP1.

## Gate

WP1 passes only when:
- pure region intersection/containment/difference is executable;
- ambiguity has no winner path;
- exact remainder is preserved;
- ResolveTechnicalAccess is deterministic for a supplied APR-owned DomainKnowledgeSnapshot;
- core/architecture tests prove framework/peer-context independence;
- all P0/P1 core findings are closed.

Peer-context adapters and infrastructure remain closed until this gate passes.

## Next

Implement and review WP1. Stop before RC/ACC/TAE adapters if the core gate is not green.
