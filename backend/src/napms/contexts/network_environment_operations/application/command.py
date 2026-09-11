from dataclasses import dataclass

from napms.contexts.network_environment_operations.domain.model import OperationTarget


@dataclass(frozen=True, slots=True)
class ExecuteNetworkOperationCommand:
    operation_id: str
    target: OperationTarget
    renderer_name: str
    renderer_contract_version: str
    artifact_content: str
    artifact_digest: str
    actor_id: str
    authority_scope: str
    expected_pre_revision: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("operation_id", self.operation_id),
            ("renderer_name", self.renderer_name),
            ("renderer_contract_version", self.renderer_contract_version),
            ("artifact_digest", self.artifact_digest),
            ("actor_id", self.actor_id),
            ("authority_scope", self.authority_scope),
        ):
            if not value or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not self.artifact_content:
            raise ValueError("artifact_content must be non-empty")
