# Application Deployment

Target Bounded Context owning logical ApplicationDeployment identity/continuity and Component-to-Resource placement truth.

Current canonical owners:

- Strategic boundary: `boundary.md`
- MVP Tactical DDD: `tactical-model.md`
- Cross-context contracts: `../context-map.md`
- Strategic responsibility summary: `../strategic-model.md`

For the first MVP, `ComponentPlacement` is a relation value `(ComponentRef, ResourceRef)` inside the ApplicationDeployment placement set. A Component may have zero, one or many placements; AD does not impose exactly-one placement and does not own addresses/endpoints/runtime instances.

Richer deployment lifecycle and historical placement entities remain deferred because no accepted MVP behavior currently requires them.
