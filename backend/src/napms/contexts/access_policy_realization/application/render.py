from typing import Protocol

from napms.contexts.access_policy_realization.domain.realization import (
    DesiredDerivationStatus,
    DesiredEnforcementPolicy,
    EnforcementTarget,
)
from napms.contexts.access_policy_realization.domain.rendering import (
    RenderedConfiguration,
    RenderStatus,
)


class ConfigurationRenderer(Protocol):
    name: str
    contract_version: str

    def render_target(
        self,
        *,
        target: EnforcementTarget,
        policy: DesiredEnforcementPolicy,
    ) -> RenderedConfiguration: ...


class RenderConfiguration:
    def __init__(self, renderer: ConfigurationRenderer) -> None:
        self._renderer = renderer

    def execute(
        self,
        policy: DesiredEnforcementPolicy,
    ) -> tuple[RenderedConfiguration, ...]:
        targets = tuple(
            sorted(
                {intent.target for intent in policy.intents},
                key=lambda item: (
                    str(item.logical_firewall_id),
                    str(item.enforcement_attachment_id),
                ),
            )
        )
        if policy.status is not DesiredDerivationStatus.DERIVED:
            return tuple(
                RenderedConfiguration(
                    status=RenderStatus.UNKNOWN,
                    target=target,
                    renderer_name=self._renderer.name,
                    renderer_contract_version=self._renderer.contract_version,
                    reason=(
                        "desired enforcement policy is not completely derived"
                    ),
                )
                for target in targets
            )
        return tuple(
            self._renderer.render_target(
                target=target,
                policy=policy,
            )
            for target in targets
        )
