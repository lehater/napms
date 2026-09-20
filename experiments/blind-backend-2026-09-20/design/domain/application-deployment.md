# Tactical domain — Application Deployment

Status: ACCEPTED candidate

## Aggregate: ComponentDeployment

Identity: `DeploymentRef`.

State:
- ComponentRef;
- ResourceRef;
- display label/metadata needed for human distinction;
- createdAt;
- retiredAt?;
- version.

Invariants:
- one Deployment refers to exactly one Component and one Resource.
- Resource address/IP is never copied into Deployment identity.
- two concrete deployed instances of the same Component are different DeploymentRefs.
- a retired Deployment remains resolvable for historical policy provenance.
- in-place move semantics between Resources are outside the current MVP contract; create a distinct Deployment for materially different placement unless product input later defines migration identity.

Operations:
- RegisterDeployment
- RetireDeployment
- ReadDeployment

## Consistency boundary

One ComponentDeployment lifecycle mutation is atomic. Component/Resource existence is validated through owner contracts before registration; their internal state is not copied.
