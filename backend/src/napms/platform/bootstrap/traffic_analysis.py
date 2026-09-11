from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import JsonDcsProjectionCodec
from napms.platform.bootstrap.config import ApplicationConfig
from napms.platform.bootstrap.greenfield import open_greenfield_scope
from napms.contexts.network_enforcement_placement.application.network_context import ReadNetworkContext
from napms.contexts.resource_catalogue.infrastructure.local.responsibility import (
    LocalDemoResourceResponsibilityAdapter,
)
from napms.contexts.resource_catalogue.application.resolve_address import (
    ResolveResourcesByTechnicalAddress,
)
from napms.contexts.resource_catalogue.application.responsibility import (
    ReadResourceResponsibilities,
)
from napms.contexts.technical_access_evidence.infrastructure.persistence.postgres import (
    PostgresTechnicalAccessEvidenceRepository,
)
from napms.workflows.traffic_analysis.infrastructure.integrations.network_enforcement_placement import (
    NetworkEnforcementPlacementTrafficAnalysisAdapter,
)
from napms.workflows.traffic_analysis.infrastructure.local.network_context import (
    LocalDemoNetworkContextKnowledgeAdapter,
)
from napms.workflows.traffic_analysis.infrastructure.integrations.resource_catalogue import (
    ResourceCatalogueTrafficEndpointAdapter,
)
from napms.workflows.traffic_analysis.infrastructure.integrations.responsibility import (
    ResourceResponsibilityTrafficAnalysisAdapter,
)
from napms.workflows.traffic_analysis.infrastructure.integrations.scoped_policy import (
    ScopedConnectivityTrafficPolicyAdapter,
)
from napms.workflows.traffic_analysis.infrastructure.integrations.technical_evidence import (
    TechnicalAccessEvidenceTrafficAnalysisAdapter,
)
from napms.workflows.traffic_analysis.application.read import ReadTrafficAnalysis


@dataclass(slots=True)
class TrafficAnalysisPostgresScope:
    read: ReadTrafficAnalysis


@contextmanager
def open_traffic_analysis_scope(
    config: ApplicationConfig,
) -> Iterator[TrafficAnalysisPostgresScope]:
    with ExitStack() as stack:
        greenfield = stack.enter_context(open_greenfield_scope(config))
        evidence_connection = stack.enter_context(psycopg.connect(config.postgres.dsn))
        evidence_connection.execute(
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
        )

        endpoints = ResourceCatalogueTrafficEndpointAdapter(
            resolver=ResolveResourcesByTechnicalAddress(
                catalogue=greenfield.resource_catalogue
            ),
            catalogue=greenfield.application_catalogue,
        )
        policy = ScopedConnectivityTrafficPolicyAdapter(
            discover=greenfield.scoped_connectivity_scopes,
            inventory=greenfield.scoped_connectivity_inventory,
            catalogue=greenfield.application_catalogue,
            decoder=JsonDcsProjectionCodec(),
        )
        network_context = NetworkEnforcementPlacementTrafficAnalysisAdapter(
            reader=ReadNetworkContext(
                knowledge=LocalDemoNetworkContextKnowledgeAdapter()
            )
        )
        evidence = TechnicalAccessEvidenceTrafficAnalysisAdapter(
            evidence_sets=PostgresTechnicalAccessEvidenceRepository(evidence_connection)
        )
        responsibilities = ResourceResponsibilityTrafficAnalysisAdapter(
            reader=ReadResourceResponsibilities(
                responsibilities=LocalDemoResourceResponsibilityAdapter()
            )
        )

        yield TrafficAnalysisPostgresScope(
            read=ReadTrafficAnalysis(
                endpoints=endpoints,
                policy=policy,
                network_context=network_context,
                evidence=evidence,
                responsibilities=responsibilities,
            )
        )
