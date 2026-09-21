from __future__ import annotations

from dataclasses import dataclass
import os

from fastapi import FastAPI

from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.application_communication_catalogue.application.service import (
    ApplicationCommunicationCatalogue,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCommunicationCatalogue,
)
from napms.contexts.application_deployment.application.service import ApplicationDeploymentService
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresComponentDeploymentRepository,
)
from napms.contexts.business_connectivity.application.service import BusinessConnectivityService
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessProcessRepository,
)
from napms.contexts.authority_management.application.service import RequireScopedAuthority
from napms.contexts.resource_catalogue.application.commands import ResourceCatalogueApplication
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceCatalogueRepository,
)
from napms.platform.database.access_request_decision import PostgresAccessRequestDecision
from napms.platform.database.access_request_submission import PostgresAccessRequestSubmission
from napms.platform.database.idempotency import PostgresIdempotencyStore
from napms.platform.database.policy_materialization import PostgresPolicyMaterialization
from napms.platform.database.policy_rule_justification import PostgresPolicyRuleJustification
from napms.platform.database.policy_rule_operation import PostgresPolicyRuleOperation
from napms.platform.http.app import HttpDependencies, create_app
from napms.platform.security.oidc import OidcConfig, OidcIdentityValidator


@dataclass(frozen=True)
class RuntimeConfig:
    database_dsn: str
    oidc_issuer: str
    oidc_audience: str
    oidc_algorithms: tuple[str, ...]
    oidc_permissions_claim: str = "permissions"
    oidc_authority_claim: str = "authority"

    @classmethod
    def from_environment(cls) -> RuntimeConfig:
        algorithms = tuple(
            item.strip()
            for item in os.environ.get("NAPMS_OIDC_ALGORITHMS", "RS256").split(",")
            if item.strip()
        )
        return cls(
            database_dsn=_required("NAPMS_DATABASE_DSN"),
            oidc_issuer=_required("NAPMS_OIDC_ISSUER"),
            oidc_audience=_required("NAPMS_OIDC_AUDIENCE"),
            oidc_algorithms=algorithms,
            oidc_permissions_claim=os.environ.get("NAPMS_OIDC_PERMISSIONS_CLAIM", "permissions"),
            oidc_authority_claim=os.environ.get("NAPMS_OIDC_AUTHORITY_CLAIM", "authority"),
        )


def build_app(config: RuntimeConfig) -> FastAPI:
    identity = OidcIdentityValidator(
        config=OidcConfig(
            issuer=config.oidc_issuer,
            audience=config.oidc_audience,
            allowed_algorithms=config.oidc_algorithms,
            permissions_claim=config.oidc_permissions_claim,
            authority_claim=config.oidc_authority_claim,
        )
    )
    authority = RequireScopedAuthority()
    return create_app(
        HttpDependencies(
            identity=identity,
            access_requests=PostgresAccessRequestSubmission(
                dsn=config.database_dsn,
                authority=authority,
            ),
            access_request_decisions=PostgresAccessRequestDecision(dsn=config.database_dsn),
            policy_rule_justifications=PostgresPolicyRuleJustification(dsn=config.database_dsn),
            policy_rule_operations=PostgresPolicyRuleOperation(dsn=config.database_dsn),
            policy_materialization=PostgresPolicyMaterialization(dsn=config.database_dsn),
            policy_rules=PostgresAccessPolicyRepository(config.database_dsn),
            idempotency=PostgresIdempotencyStore(dsn=config.database_dsn),
            application_deployment=ApplicationDeploymentService(
                deployments=PostgresComponentDeploymentRepository(config.database_dsn),
                components=PostgresApplicationCommunicationCatalogue(config.database_dsn),
                resources=PostgresResourceCatalogueRepository(config.database_dsn),
            ),
            business_connectivity=BusinessConnectivityService(
                processes=PostgresBusinessProcessRepository(config.database_dsn),
                interactions=PostgresApplicationCommunicationCatalogue(config.database_dsn),
            ),
            application_catalogue=ApplicationCommunicationCatalogue(
                applications=PostgresApplicationCommunicationCatalogue(config.database_dsn),
                interactions=PostgresApplicationCommunicationCatalogue(config.database_dsn),
                components=PostgresApplicationCommunicationCatalogue(config.database_dsn),
            ),
            resource_catalogue=ResourceCatalogueApplication(
                resources=PostgresResourceCatalogueRepository(config.database_dsn)
            ),
        )
    )


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required")
    return value
