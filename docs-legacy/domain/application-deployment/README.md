# Application Deployment

Target Bounded Context owning concrete `ComponentDeployment` identity/lifecycle and exact Component-to-Resource deployment truth.

Current canonical owners:

- Strategic boundary: `boundary.md`
- MVP Tactical DDD: `tactical-model.md`
- Cross-context contracts: `../context-map.md`
- Strategic responsibility summary: `../strategic-model.md`

For the first MVP, one `ComponentDeployment` is one concrete independently addressable instance of one ACC Component deployed on exactly one RC Resource. Deploying the same Component on another Resource creates another ComponentDeployment identity.

The target has no whole-Application deployment aggregate or mutable Component placement set in the policy path.

Application Deployment does not own Resource AddressSpace/scope/responsibility, ACC Interaction semantics, Policy Rule state or provider runtime/container identity.

The current implemented ACC runtime may still use compatibility `ComponentDeployment` identities with different ownership/meaning. Those remain as-built reconstruction truth and must not be conflated with this target concept.
