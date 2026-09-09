from dataclasses import dataclass
from enum import Enum

from napms.access_policy_realization.domain.realization import EnforcementTarget


class RenderStatus(str, Enum):
    RENDERED = "Rendered"
    UNSUPPORTED = "Unsupported"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class RenderedStatement:
    text: str
    rule_references: tuple[str, ...]
    interaction_references: tuple[str, ...]
    placement_provenance_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RenderedConfiguration:
    status: RenderStatus
    target: EnforcementTarget
    renderer_name: str
    renderer_contract_version: str
    content: str | None = None
    statements: tuple[RenderedStatement, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status is RenderStatus.RENDERED:
            if self.content is None:
                raise ValueError("Rendered result requires content")
            if self.reason is not None:
                raise ValueError("Rendered result cannot carry failure reason")
            return
        if self.content is not None or self.statements:
            raise ValueError("failed render must not expose partial artifact")
        if not self.reason or not self.reason.strip():
            raise ValueError("failed render requires reason")
