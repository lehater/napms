# Tactical domain — Application Deployment

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Aggregate: ComponentDeployment

Identity: `DeploymentRef`.

State:
- ComponentRef;
- ResourceRef;
- createdAt.

Invariants:
- one Deployment refers to exactly one Component and one Resource;
- Resource address/IP is never copied into Deployment identity;
- two concrete deployed instances of the same Component are different DeploymentRefs;
- ComponentRef/ResourceRef are immutable after registration;
- update, relocation, retirement and deletion are outside the selected MVP;
- materially different placement is represented by a distinct Deployment unless future product input defines migration identity.

Operations:
- RegisterDeployment
- ReadDeployment

No independent display label/metadata is introduced without a product need; human presentation can resolve the referenced Component/Resource.

## Consistency boundary

One ComponentDeployment creation is atomic. Component/Resource existence is validated through owner contracts before registration; their internal state is not copied.
