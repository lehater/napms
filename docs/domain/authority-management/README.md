# Authority Management

Target Bounded Context owning effective actor/action/scope authority and the assignment semantics used to derive it.

Canonical target authority:

- `tactical-model.md` — MVP Tactical DDD;
- `../semantic-ownership.md` — cross-context ownership summary;
- `../context-map.md` — public relationships;
- relevant accepted requirements under `docs/requirements/` define protected actions and consumer behavior.

Core target chain:

```text
Actor
-> Group Membership
-> Group Role Assignment @ ResponsibilityScope
-> Role permits Action
-> EffectiveAuthority(actor, action, scope, time)
```

Resource ownership/responsibility metadata never grants authority by itself. ResponsibilityScopeRef is shared correlation, not a new bounded context.
