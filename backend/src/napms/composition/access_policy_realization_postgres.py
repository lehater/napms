from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

from napms.contexts.access_policy.application.select_effective_policy import (
    SelectAccessPolicyEffectiveDesiredPolicy,
)
from napms.contexts.access_policy_realization.infrastructure.integrations.catalogues import (
    CatalogueDomainKnowledgeAdapter,
)
from napms.contexts.access_policy_realization.infrastructure.rendering.cisco_asa import (
    CiscoAsaAclRenderer,
)
from napms.contexts.access_policy_realization.infrastructure.integrations.configured_evidence import (
    ConfiguredEvidenceProjectionAdapter,
)
from napms.contexts.access_policy_realization.infrastructure.integrations.desired_policy import (
    EffectiveDesiredPolicyProjectionAdapter,
)
from napms.contexts.access_policy_realization.infrastructure.integrations.placement import (
    NetworkEnforcementPlacementProjectionAdapter,
)
from napms.contexts.access_policy_realization.application.realize import (
    BuildConfiguredEnforcementSnapshot,
    DeriveDesiredEnforcementFromOwners,
)
from napms.contexts.access_policy_realization.application.reconcile import (
    ReconcileEnforcementPolicy,
)
from napms.contexts.access_policy_realization.application.render import (
    RenderConfiguration,
)
from napms.composition.config import ApplicationConfig
from napms.composition.greenfield_postgres import (
    open_greenfield_scope,
)
from napms.composition.network_enforcement_placement_postgres import (
    open_network_enforcement_placement_scope,
)
from napms.composition.technical_access_evidence_postgres import (
    open_technical_access_evidence_scope,
)
from napms.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
)
from napms.policy_export.application.normalize_snapshot import (
    NormalizeExportSnapshot,
)


@dataclass(slots=True)
class AccessPolicyRealizationPostgresScope:
    derive_desired: DeriveDesiredEnforcementFromOwners
    build_configured: BuildConfiguredEnforcementSnapshot
    reconcile: ReconcileEnforcementPolicy
    render: RenderConfiguration


@contextmanager
def open_access_policy_realization_scope(
    config: ApplicationConfig,
    *,
    actor_id: str,
) -> Iterator[AccessPolicyRealizationPostgresScope]:
    with ExitStack() as stack:
        greenfield = stack.enter_context(
            open_greenfield_scope(config)
        )
        evidence = stack.enter_context(
            open_technical_access_evidence_scope(
                config
            )
        )
        placement = stack.enter_context(
            open_network_enforcement_placement_scope(
                config
            )
        )

        domain_knowledge = (
            CatalogueDomainKnowledgeAdapter(
                application_catalogue=(
                    greenfield.application_catalogue
                ),
                resource_catalogue=(
                    greenfield.resource_catalogue
                ),
                dcs_decoder=(
                    greenfield.dcs_decoder
                ),
            )
        )
        desired_policy = (
            EffectiveDesiredPolicyProjectionAdapter(
                selector=(
                    SelectAccessPolicyEffectiveDesiredPolicy(
                        authority=greenfield.authority,
                        rules=greenfield.access_rules,
                    )
                ),
                snapshot_assembler=(
                    AssembleExportSnapshot(
                        application_catalogue=(
                            greenfield.application_projection
                        ),
                        resource_catalogue=(
                            greenfield.resource_projection
                        ),
                    )
                ),
                normalizer=(
                    NormalizeExportSnapshot(
                        decoder=(
                            greenfield.dcs_decoder
                        )
                    )
                ),
                actor_id=actor_id,
            )
        )
        placement_projection = (
            NetworkEnforcementPlacementProjectionAdapter(
                select_enforcement=(
                    placement.select_enforcement
                )
            )
        )
        configured_evidence = (
            ConfiguredEvidenceProjectionAdapter(
                get_evidence_set=(
                    evidence.get_technical_access_evidence
                )
            )
        )

        yield AccessPolicyRealizationPostgresScope(
            derive_desired=(
                DeriveDesiredEnforcementFromOwners(
                    desired_policy=desired_policy,
                    domain_knowledge=domain_knowledge,
                    placement=placement_projection,
                )
            ),
            build_configured=(
                BuildConfiguredEnforcementSnapshot(
                    configured_evidence=(
                        configured_evidence
                    ),
                    domain_knowledge=(
                        domain_knowledge
                    ),
                )
            ),
            reconcile=(
                ReconcileEnforcementPolicy()
            ),
            render=(
                RenderConfiguration(
                    CiscoAsaAclRenderer()
                )
            ),
        )
