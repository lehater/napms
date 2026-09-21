from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ComponentDeployment:
    deployment_ref: UUID
    component_ref: UUID
    resource_ref: UUID
