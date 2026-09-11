from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.composition.config import ApplicationConfig
from napms.composition.greenfield_postgres import open_greenfield_scope
from napms.network_enforcement_placement.application.network_context import ReadNetworkContext
from napms.resource_catalogue.adapters.local_responsibility import (
    LocalDemoResourceResponsibilityAdapter,
)
from napms.resource_catalogue.application.resolve_address import (
    ResolveResourcesByTechnicalAddress,
)
from napms.resource_catalogue.application.responsibility import (
    ReadResourceResponsibilities,
)
from napms.contexts.technical_access_evidence.infrastructure.persistence.postgres import (
    PostgresTechnicalAccessEvidenceRepository,
)
from napms.traffic_analysis.adapters.local_network_context import (
    LocalDemoNetworkContextKnowledgeAdapter,
    NetworkEnforcementPlacementTrafficAnalysisAdapter,
)
from napms.traffic_analysis.adapters.resource_catalogue import (
    ResourceCatalogueTrafficEndpointAdapter,
)
from napms.traffic_analysis.adapters.responsibility import (
    ResourceResponsibilityTrafficAnalysisAdapter,
)
from napms.traffic_analysis.adapters.scoped_policy import (
    ScopedConnectivityTrafficPolicyAdapter,
)
from napms.traffic_analysis.adapters.technical_evidence import (
    TechnicalAccessEvidenceTrafficAnalysisAdapter,
)
from napms.traffic_analysis.application.read import ReadTrafficAnalysis


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
