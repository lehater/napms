from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from typing import NoReturn
from uuid import UUID, uuid5

import psycopg

from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    PermissionDecision,
    RuleEffectState,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.contexts.application_communication_catalogue.application.service import (
    ApplicationCommunicationCatalogue,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    PortRange,
    TrafficClause,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCommunicationCatalogue,
)
from napms.contexts.application_deployment.application.service import (
    ApplicationDeploymentService,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresComponentDeploymentRepository,
)
from napms.contexts.authority_management.application.service import (
    RequireScopedAuthority,
)
from napms.contexts.authority_management.domain.model import AuthorityGrant, Principal
from napms.contexts.business_connectivity.application.service import (
    BusinessConnectivityService,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessProcessRepository,
)
from napms.contexts.resource_catalogue.application.commands import (
    MutationContext,
    ResourceCatalogueApplication,
)
from napms.contexts.resource_catalogue.domain.model import (
    AddressRealization,
    Resource,
    ResponsibilityRole,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceCatalogueRepository,
)
from napms.platform.database.access_request_decision import (
    PostgresAccessRequestDecision,
)
from napms.platform.database.access_request_submission import (
    PostgresAccessRequestSubmission,
)
from napms.platform.database.policy_rule_operation import PostgresPolicyRuleOperation


DEMO_NAMESPACE = UUID("8da3ea14-e20e-4df7-84f8-1da55b08d7c4")
DEMO_SUBJECT = "subject:demo-seed"
DEMO_APPROVER = "subject:demo-approver"


class DemoDataConflict(RuntimeError):
    pass


def demo_ref(kind: str, key: str) -> UUID:
    return uuid5(DEMO_NAMESPACE, f"{kind}:{key}")


@dataclass(frozen=True)
class NodeSpec:
    key: str
    application_name: str
    component_name: str
    resource_name: str
    authority_scope: str
    address: str
    site_key: str
    owner_key: str


@dataclass(frozen=True)
class InteractionSpec:
    key: str
    source_key: str
    destination_key: str
    purpose: str
    protocol: int
    destination_port: int


@dataclass(frozen=True)
class ProcessSpec:
    key: str
    interaction_key: str
    name: str
    description: str
    criticality: str
    organization_ref: str
    organization_name: str
    business_basis: str


@dataclass(frozen=True)
class RequestSpec:
    key: str
    process_key: str
    interaction_key: str
    decision: PermissionDecision | None
    inactive_rule: bool = False


NODES = (
    NodeSpec(
        "customer",
        "Demo Network Communication Profile",
        "Customer Web",
        "edge-customer-01",
        "scope:customer",
        "10.20.1.11",
        "fra",
        "digital",
    ),
    NodeSpec(
        "identity",
        "Demo Network Communication Profile",
        "Identity API",
        "app-identity-01",
        "scope:identity",
        "10.20.2.21",
        "fra",
        "identity",
    ),
    NodeSpec(
        "orders",
        "Demo Network Communication Profile",
        "Order API",
        "app-orders-01",
        "scope:orders",
        "10.20.3.21",
        "fra",
        "commerce",
    ),
    NodeSpec(
        "payments",
        "Demo Network Communication Profile",
        "Payment API",
        "app-payments-01",
        "scope:payments",
        "10.20.4.21",
        "fra",
        "payments",
    ),
    NodeSpec(
        "inventory",
        "Demo Network Communication Profile",
        "Inventory API",
        "app-inventory-01",
        "scope:inventory",
        "10.20.5.21",
        "ber",
        "supply",
    ),
    NodeSpec(
        "notifications",
        "Demo Network Communication Profile",
        "Notification API",
        "app-notifications-01",
        "scope:notifications",
        "10.20.6.21",
        "fra",
        "digital",
    ),
    NodeSpec(
        "reporting",
        "Demo Network Communication Profile",
        "Reporting API",
        "app-reporting-01",
        "scope:reporting",
        "10.20.7.21",
        "ber",
        "analytics",
    ),
    NodeSpec(
        "crm",
        "Demo Network Communication Profile",
        "CRM Adapter",
        "worker-crm-01",
        "scope:crm",
        "10.20.8.21",
        "fra",
        "sales",
    ),
    NodeSpec(
        "admin",
        "Demo Network Communication Profile",
        "Admin API",
        "app-admin-01",
        "scope:admin",
        "10.20.9.21",
        "fra",
        "platform",
    ),
    NodeSpec(
        "observability",
        "Demo Network Communication Profile",
        "Metrics Collector",
        "obs-collector-01",
        "scope:observability",
        "10.20.10.21",
        "ber",
        "platform",
    ),
)

INTERACTIONS = (
    InteractionSpec(
        "customer-identity",
        "customer",
        "identity",
        "Authenticate customer sessions",
        6,
        443,
    ),
    InteractionSpec(
        "customer-orders",
        "customer",
        "orders",
        "Submit and query customer orders",
        6,
        443,
    ),
    InteractionSpec(
        "orders-payments",
        "orders",
        "payments",
        "Authorize order payment",
        6,
        443,
    ),
    InteractionSpec(
        "orders-inventory",
        "orders",
        "inventory",
        "Reserve inventory for an order",
        6,
        443,
    ),
    InteractionSpec(
        "orders-notifications",
        "orders",
        "notifications",
        "Request transactional customer notification",
        6,
        443,
    ),
    InteractionSpec(
        "reporting-orders",
        "reporting",
        "orders",
        "Read order reporting data",
        6,
        443,
    ),
    InteractionSpec(
        "crm-customer",
        "crm",
        "customer",
        "Synchronize customer account data",
        6,
        443,
    ),
    InteractionSpec(
        "admin-customer",
        "admin",
        "customer",
        "Administer customer portal settings",
        6,
        443,
    ),
    InteractionSpec(
        "customer-metrics",
        "customer",
        "observability",
        "Publish portal metrics",
        17,
        8125,
    ),
    InteractionSpec(
        "payments-reporting",
        "payments",
        "reporting",
        "Publish payment reporting data",
        6,
        443,
    ),
)

PROCESSES = (
    ProcessSpec(
        "customer-sign-in",
        "customer-identity",
        "Customer sign-in",
        "Authenticate customers before protected portal actions.",
        "HIGH",
        "ORG-DIGITAL",
        "Digital Channels",
        "Customers must authenticate before protected self-service actions.",
    ),
    ProcessSpec(
        "order-placement",
        "customer-orders",
        "Order placement",
        "Capture customer orders through the public portal.",
        "CRITICAL",
        "ORG-COMMERCE",
        "Commerce",
        "Customer orders must reach the order management capability.",
    ),
    ProcessSpec(
        "payment-authorization",
        "orders-payments",
        "Payment authorization",
        "Authorize payment for an accepted order.",
        "CRITICAL",
        "ORG-PAYMENTS",
        "Payments",
        "Accepted orders require payment authorization.",
    ),
    ProcessSpec(
        "inventory-reservation",
        "orders-inventory",
        "Inventory reservation",
        "Reserve stock for accepted customer orders.",
        "HIGH",
        "ORG-SUPPLY",
        "Supply Chain",
        "Accepted orders require inventory reservation.",
    ),
    ProcessSpec(
        "customer-notification",
        "orders-notifications",
        "Customer notification",
        "Deliver transactional notifications for order events.",
        "MEDIUM",
        "ORG-DIGITAL",
        "Digital Channels",
        "Order events require customer notification.",
    ),
    ProcessSpec(
        "management-reporting",
        "reporting-orders",
        "Management reporting",
        "Produce management reports from order data.",
        "MEDIUM",
        "ORG-ANALYTICS",
        "Analytics",
        "Management reporting requires current order data.",
    ),
    ProcessSpec(
        "crm-synchronization",
        "crm-customer",
        "CRM synchronization",
        "Synchronize customer account data with CRM.",
        "MEDIUM",
        "ORG-SALES",
        "Sales",
        "Customer account changes must be synchronized with CRM.",
    ),
    ProcessSpec(
        "service-administration",
        "admin-customer",
        "Service administration",
        "Provide authenticated administrative control.",
        "HIGH",
        "ORG-PLATFORM",
        "Platform Engineering",
        "Operators require administrative access to customer portal settings.",
    ),
    ProcessSpec(
        "platform-monitoring",
        "customer-metrics",
        "Platform monitoring",
        "Publish portal metrics to the observability platform.",
        "HIGH",
        "ORG-PLATFORM",
        "Platform Engineering",
        "Platform health monitoring requires current portal metrics.",
    ),
    ProcessSpec(
        "payment-reporting",
        "payments-reporting",
        "Payment reporting",
        "Publish payment data for operational reporting.",
        "MEDIUM",
        "ORG-PAYMENTS",
        "Payments",
        "Operational reporting requires payment outcome data.",
    ),
)

SITES = {
    "fra": ("Frankfurt", "Demo Frankfurt site"),
    "ber": ("Berlin", "Demo Berlin site"),
}

RESPONSIBILITY_GROUPS = {
    "digital": ("Digital Channels", "ORG-DIGITAL"),
    "identity": ("Identity", "ORG-IDENTITY"),
    "commerce": ("Commerce", "ORG-COMMERCE"),
    "payments": ("Payments", "ORG-PAYMENTS"),
    "supply": ("Supply Chain", "ORG-SUPPLY"),
    "analytics": ("Analytics", "ORG-ANALYTICS"),
    "sales": ("Sales", "ORG-SALES"),
    "platform": ("Platform Engineering", "ORG-PLATFORM"),
}

REQUESTS = (
    RequestSpec(
        "customer-sign-in",
        "customer-sign-in",
        "customer-identity",
        PermissionDecision.ALLOWED,
    ),
    RequestSpec(
        "order-placement",
        "order-placement",
        "customer-orders",
        PermissionDecision.ALLOWED,
    ),
    RequestSpec(
        "payment-authorization",
        "payment-authorization",
        "orders-payments",
        PermissionDecision.ALLOWED,
    ),
    RequestSpec(
        "inventory-reservation",
        "inventory-reservation",
        "orders-inventory",
        PermissionDecision.ALLOWED,
    ),
    RequestSpec(
        "customer-notification",
        "customer-notification",
        "orders-notifications",
        PermissionDecision.ALLOWED,
    ),
    RequestSpec(
        "payment-reporting",
        "payment-reporting",
        "payments-reporting",
        PermissionDecision.ALLOWED,
        inactive_rule=True,
    ),
    RequestSpec(
        "management-reporting",
        "management-reporting",
        "reporting-orders",
        PermissionDecision.DENIED,
    ),
    RequestSpec(
        "crm-synchronization",
        "crm-synchronization",
        "crm-customer",
        PermissionDecision.DENIED,
    ),
    RequestSpec(
        "service-administration",
        "service-administration",
        "admin-customer",
        None,
    ),
    RequestSpec(
        "platform-monitoring",
        "platform-monitoring",
        "customer-metrics",
        None,
    ),
)


class _Refs:
    def __init__(self, values: Iterable[UUID]) -> None:
        self._values = iter(values)

    def __call__(self) -> UUID:
        try:
            return next(self._values)
        except StopIteration as exc:
            raise RuntimeError("demo reference sequence exhausted") from exc


def _fixed(value: UUID) -> Callable[[], UUID]:
    return lambda: value


def _application_ref(key: str) -> UUID:
    return demo_ref("application", key)


def _component_ref(key: str) -> UUID:
    return demo_ref("component", key)


def _resource_ref(key: str) -> UUID:
    return demo_ref("resource", key)


def _interaction_ref(key: str) -> UUID:
    return demo_ref("interaction", key)


def _revision_ref(key: str) -> UUID:
    return demo_ref("interaction-revision", key)


def _deployment_ref(key: str) -> UUID:
    return demo_ref("deployment", key)


def _process_ref(key: str) -> UUID:
    return demo_ref("process", key)


def _need_ref(key: str) -> UUID:
    return demo_ref("need", key)


class LocalDemoSeeder:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._catalogue_repository = PostgresApplicationCommunicationCatalogue(dsn)
        self._resource_repository = PostgresResourceCatalogueRepository(dsn)
        self._deployment_repository = PostgresComponentDeploymentRepository(dsn)
        self._process_repository = PostgresBusinessProcessRepository(dsn)
        self._policy_repository = PostgresAccessPolicyRepository(dsn)
        self._resource_context = MutationContext(
            principal=Principal(
                subject=DEMO_SUBJECT,
                instance_permissions=frozenset({"resource.write"}),
            ),
            effective_at=datetime.now(timezone.utc),
        )
        self._nodes = {item.key: item for item in NODES}
        self._interactions = {item.key: item for item in INTERACTIONS}

    def seed(self) -> None:
        self._seed_reference_data()
        self._seed_nodes()
        self._seed_interactions()
        self._seed_processes()
        self._seed_access_requests()

    def _seed_reference_data(self) -> None:
        with psycopg.connect(self._dsn) as connection:
            for key, (name, description) in SITES.items():
                site_ref = demo_ref("site", key)
                row = connection.execute(
                    """
                    SELECT name, description
                    FROM resource_catalogue.site
                    WHERE site_ref = %s
                    """,
                    (site_ref,),
                ).fetchone()
                if row is None:
                    connection.execute(
                        """
                        INSERT INTO resource_catalogue.site (site_ref, name, description)
                        VALUES (%s, %s, %s)
                        """,
                        (site_ref, name, description),
                    )
                elif row != (name, description):
                    self._conflict(f"site {key} differs from demo definition")

            for key, (display_name, external_reference) in RESPONSIBILITY_GROUPS.items():
                group_ref = demo_ref("organization", key)
                row = connection.execute(
                    """
                    SELECT display_name, external_reference
                    FROM resource_catalogue.responsibility_group
                    WHERE group_ref = %s
                    """,
                    (group_ref,),
                ).fetchone()
                if row is None:
                    connection.execute(
                        """
                        INSERT INTO resource_catalogue.responsibility_group
                            (group_ref, display_name, external_reference)
                        VALUES (%s, %s, %s)
                        """,
                        (group_ref, display_name, external_reference),
                    )
                elif row != (display_name, external_reference):
                    self._conflict(f"responsibility group {key} differs from demo definition")

    def _catalogue(self, ref: UUID) -> ApplicationCommunicationCatalogue:
        return ApplicationCommunicationCatalogue(
            applications=self._catalogue_repository,
            interactions=self._catalogue_repository,
            components=self._catalogue_repository,
            new_ref=_fixed(ref),
        )

    def _resource_application(self, ref: UUID) -> ResourceCatalogueApplication:
        return ResourceCatalogueApplication(
            resources=self._resource_repository,
            new_ref=_fixed(ref),
        )

    def _deployment_service(self, ref: UUID) -> ApplicationDeploymentService:
        return ApplicationDeploymentService(
            deployments=self._deployment_repository,
            components=self._catalogue_repository,
            resources=self._resource_repository,
            new_ref=_fixed(ref),
        )

    def _process_service(self, ref: UUID) -> BusinessConnectivityService:
        return BusinessConnectivityService(
            processes=self._process_repository,
            interactions=self._catalogue_repository,
            new_ref=_fixed(ref),
        )

    def _seed_nodes(self) -> None:
        for spec in NODES:
            self._ensure_application(spec)
            self._ensure_resource(spec)
            self._ensure_deployment(spec)

    def _ensure_application(self, spec: NodeSpec) -> None:
        application_ref = _application_ref(spec.application_name)
        application = self._catalogue_repository.get_application(application_ref)
        if application is None:
            application = self._catalogue(application_ref).create_application(
                name=spec.application_name
            )
        elif application.name != spec.application_name:
            self._conflict(f"application {spec.key} differs from demo definition")

        component_ref = _component_ref(spec.key)
        existing = next(
            (item for item in application.components if item.component_ref == component_ref),
            None,
        )
        if existing is not None:
            if existing.name != spec.component_name:
                self._conflict(f"component {spec.key} differs from demo definition")
            return
        self._catalogue(component_ref).add_component(
            application_ref=application_ref,
            name=spec.component_name,
            expected_version=application.version,
        )

    def _ensure_resource(self, spec: NodeSpec) -> None:
        resource_ref = _resource_ref(spec.key)
        resource = self._resource_repository.get(resource_ref)
        if resource is None:
            resource = self._resource_application(resource_ref).register_resource(
                display_name=spec.resource_name,
                authority_scope_ref=spec.authority_scope,
                context=self._resource_context,
            )
        elif (
            resource.display_name != spec.resource_name
            or resource.authority_scope_ref != spec.authority_scope
        ):
            self._conflict(f"resource {spec.key} differs from demo definition")

        site_ref = demo_ref("site", spec.site_key)
        if resource.current_site is None:
            resource = self._resource_application(demo_ref("site-fact", spec.key)).set_site(
                resource_ref=resource_ref,
                site_ref=site_ref,
                expected_version=resource.version,
                context=self._resource_context,
            )
        elif resource.current_site.site_ref != site_ref:
            self._conflict(f"resource {spec.key} site was changed")

        endpoint_ref = demo_ref("endpoint", spec.key)
        endpoint = next(
            (item for item in resource.endpoints if item.endpoint_ref == endpoint_ref),
            None,
        )
        if endpoint is None:
            resource = self._resource_application(endpoint_ref).add_endpoint(
                resource_ref=resource_ref,
                expected_version=resource.version,
                context=self._resource_context,
            )
            endpoint = next(
                item for item in resource.endpoints if item.endpoint_ref == endpoint_ref
            )

        expected_address = AddressRealization.host(spec.address)
        if endpoint.current_address is None:
            resource = self._resource_application(
                demo_ref("address-fact", spec.key)
            ).set_endpoint_address(
                resource_ref=resource_ref,
                endpoint_ref=endpoint_ref,
                address=expected_address,
                expected_version=resource.version,
                context=self._resource_context,
            )
        elif endpoint.current_address.address != expected_address:
            self._conflict(f"resource {spec.key} address was changed")

        resource = self._ensure_responsibility(
            resource,
            role=ResponsibilityRole.OWNER,
            group_ref=demo_ref("organization", spec.owner_key),
            fact_ref=demo_ref("responsibility-owner-fact", spec.key),
            key=spec.key,
        )
        self._ensure_responsibility(
            resource,
            role=ResponsibilityRole.ADMINISTRATOR,
            group_ref=demo_ref("organization", "platform"),
            fact_ref=demo_ref("responsibility-admin-fact", spec.key),
            key=spec.key,
        )

    def _ensure_responsibility(
        self,
        resource: Resource,
        *,
        role: ResponsibilityRole,
        group_ref: UUID,
        fact_ref: UUID,
        key: str,
    ) -> Resource:
        existing = next(
            (item for item in resource.responsibilities if item.role is role),
            None,
        )
        if existing is not None:
            if existing.group_ref != group_ref:
                self._conflict(f"resource {key} {role.value.lower()} was changed")
            return resource
        return self._resource_application(fact_ref).set_responsibility(
            resource_ref=resource.resource_ref,
            role=role,
            group_ref=group_ref,
            expected_version=resource.version,
            context=self._resource_context,
        )

    def _ensure_deployment(self, spec: NodeSpec) -> None:
        deployment_ref = _deployment_ref(spec.key)
        existing = self._deployment_repository.resolve_deployment(deployment_ref)
        if existing is None:
            self._deployment_service(deployment_ref).register_component_deployment(
                component_ref=_component_ref(spec.key),
                resource_ref=_resource_ref(spec.key),
            )
            return
        if existing.component_ref != _component_ref(
            spec.key
        ) or existing.resource_ref != _resource_ref(spec.key):
            self._conflict(f"deployment {spec.key} differs from demo definition")

    def _seed_interactions(self) -> None:
        for spec in INTERACTIONS:
            interaction_ref = _interaction_ref(spec.key)
            interaction = self._catalogue_repository.get_interaction(interaction_ref)
            if interaction is None:
                interaction = self._catalogue(interaction_ref).create_interaction(
                    source_component_ref=_component_ref(spec.source_key),
                    destination_component_ref=_component_ref(spec.destination_key),
                    purpose=spec.purpose,
                )
            elif (
                interaction.source_component_ref != _component_ref(spec.source_key)
                or interaction.destination_component_ref != _component_ref(spec.destination_key)
                or interaction.purpose != spec.purpose
            ):
                self._conflict(f"interaction {spec.key} differs from demo definition")

            revision_ref = _revision_ref(spec.key)
            clause = TrafficClause(
                ip_protocol=spec.protocol,
                destination_ports=(PortRange(spec.destination_port, spec.destination_port),),
            )
            revision = next(
                (item for item in interaction.revisions if item.revision_ref == revision_ref),
                None,
            )
            if revision is not None:
                if revision.traffic_clauses != (clause,):
                    self._conflict(f"interaction revision {spec.key} was changed")
                continue
            if interaction.revisions:
                self._conflict(f"interaction {spec.key} has unexpected revisions")
            self._catalogue(revision_ref).publish_interaction_revision(
                interaction_ref=interaction_ref,
                traffic_clauses=(clause,),
                expected_version=interaction.version,
                subject=DEMO_SUBJECT,
            )

    def _seed_processes(self) -> None:
        for spec in PROCESSES:
            process_ref = _process_ref(spec.key)
            process = self._process_repository.get_process(process_ref)
            if process is None:
                process = self._process_service(process_ref).register_business_process(
                    name=spec.name,
                    description=spec.description,
                    criticality_label=spec.criticality,
                )
            elif (
                process.name != spec.name
                or process.description != spec.description
                or process.criticality_label != spec.criticality
            ):
                self._conflict(f"business process {spec.key} differs from demo definition")

            if process.organization_external_reference is None:
                process = self._process_service(
                    demo_ref("process-update", spec.key)
                ).set_responsible_organization(
                    process_ref=process_ref,
                    external_reference=spec.organization_ref,
                    display_name=spec.organization_name,
                    expected_version=process.version,
                )
            elif (
                process.organization_external_reference != spec.organization_ref
                or process.organization_display_name != spec.organization_name
            ):
                self._conflict(f"business process {spec.key} organization was changed")

            need_ref = _need_ref(spec.key)
            need = next(
                (item for item in process.needs if item.need_ref == need_ref),
                None,
            )
            interaction = self._interactions[spec.interaction_key]
            if need is not None:
                if (
                    need.interaction_ref != _interaction_ref(spec.interaction_key)
                    or need.participant_component_ref != _component_ref(interaction.source_key)
                    or need.business_basis != spec.business_basis
                ):
                    self._conflict(f"connectivity need {spec.key} differs from demo definition")
                continue
            self._process_service(need_ref).declare_need(
                process_ref=process_ref,
                interaction_ref=_interaction_ref(spec.interaction_key),
                participant_component_ref=_component_ref(interaction.source_key),
                business_basis=spec.business_basis,
                subject=DEMO_SUBJECT,
                expected_version=process.version,
            )

    def _seed_access_requests(self) -> None:
        principal = Principal(
            subject=DEMO_SUBJECT,
            authority_grants=tuple(
                AuthorityGrant(action="access.request", scope=scope)
                for scope in sorted({item.authority_scope for item in NODES})
            ),
        )
        for spec in REQUESTS:
            request_ref = demo_ref("access-request", spec.key)
            request = self._policy_repository.get_request(request_ref)
            interaction = self._interactions[spec.interaction_key]
            if request is None:
                source_scope = self._nodes[interaction.source_key].authority_scope
                destination_scope = self._nodes[interaction.destination_key].authority_scope
                scopes = sorted({source_scope, destination_scope})
                refs = [
                    demo_ref(
                        "request-authority-evidence",
                        f"{spec.key}:{scope}",
                    )
                    for scope in scopes
                ]
                refs.append(request_ref)
                request = PostgresAccessRequestSubmission(
                    dsn=self._dsn,
                    authority=RequireScopedAuthority(),
                    new_ref=_Refs(refs),
                ).submit(
                    principal=principal,
                    source_deployment_ref=_deployment_ref(interaction.source_key),
                    destination_deployment_ref=_deployment_ref(interaction.destination_key),
                    interaction_revision_ref=_revision_ref(spec.interaction_key),
                    need_ref=_need_ref(spec.process_key),
                )
            self._verify_request(spec, request, interaction)
            self._ensure_decision(spec, request)

    def _verify_request(
        self,
        spec: RequestSpec,
        request: AccessRequest,
        interaction: InteractionSpec,
    ) -> None:
        subject = request.access_subject
        if (
            subject.source_deployment_ref != _deployment_ref(interaction.source_key)
            or subject.destination_deployment_ref != _deployment_ref(interaction.destination_key)
            or subject.interaction_revision_ref != _revision_ref(spec.interaction_key)
            or request.initial_need_ref != _need_ref(spec.process_key)
        ):
            self._conflict(f"access request {spec.key} differs from demo definition")
        if request.decision_result is not None and request.decision_result is not spec.decision:
            self._conflict(f"access request {spec.key} decision was changed")

    def _ensure_decision(
        self,
        spec: RequestSpec,
        request: AccessRequest,
    ) -> None:
        if spec.decision is None:
            if request.decision_result is not None:
                self._conflict(f"access request {spec.key} is expected to remain pending")
            return

        rule_ref = demo_ref("policy-rule", spec.key)
        if request.decision_result is None:
            refs: tuple[UUID, ...] = ()
            if spec.decision is PermissionDecision.ALLOWED:
                refs = (
                    demo_ref("authorization-evidence", spec.key),
                    demo_ref("justification", spec.key),
                    rule_ref,
                    demo_ref("policy-history", f"{spec.key}:created"),
                )
            _, rule = PostgresAccessRequestDecision(
                dsn=self._dsn,
                new_ref=_Refs(refs),
            ).decide(
                request_ref=request.request_ref,
                result=spec.decision,
                decided_by_subject=DEMO_APPROVER,
                expected_version=request.version,
                external_decision_ref=f"demo-decision:{spec.key}",
            )
            if spec.decision is PermissionDecision.ALLOWED and (
                rule is None or rule.rule_ref != rule_ref
            ):
                self._conflict(f"policy rule {spec.key} did not receive stable demo identity")

        if spec.decision is PermissionDecision.DENIED:
            return

        rule = self._policy_repository.get_rule(rule_ref)
        if rule is None:
            self._conflict(f"policy rule {spec.key} is missing for allowed request")
        desired_state = RuleEffectState.INACTIVE if spec.inactive_rule else RuleEffectState.ACTIVE
        if rule.effect_state is desired_state:
            return
        if desired_state is RuleEffectState.ACTIVE:
            self._conflict(f"policy rule {spec.key} was deactivated after seeding")
        PostgresPolicyRuleOperation(
            dsn=self._dsn,
            new_ref=_fixed(demo_ref("policy-history", f"{spec.key}:inactive")),
        ).set_state(
            rule_ref=rule.rule_ref,
            effect_state=RuleEffectState.INACTIVE,
            effective_window=rule.effective_window,
            changed_by_subject=DEMO_APPROVER,
            expected_version=rule.version,
        )

    @staticmethod
    def _conflict(message: str) -> NoReturn:
        raise DemoDataConflict(
            f"{message}; reset the local database or restore the demo object before reseeding"
        )


def seed_local_demo(dsn: str) -> None:
    if not dsn.strip():
        raise ValueError("dsn must be non-empty")
    LocalDemoSeeder(dsn).seed()


def run() -> None:
    if os.environ.get("NAPMS_ENVIRONMENT", "").strip() != "local-dev":
        raise SystemExit("napms-seed-local is restricted to NAPMS_ENVIRONMENT=local-dev")
    dsn = os.environ.get("NAPMS_DATABASE_DSN", "").strip()
    if not dsn:
        raise SystemExit("NAPMS_DATABASE_DSN is required")
    seed_local_demo(dsn)
    allowed = sum(item.decision is PermissionDecision.ALLOWED for item in REQUESTS)
    print(
        "NAPMS demo data ready: "
        f"applications={len({item.application_name for item in NODES})}, resources={len(NODES)}, "
        f"interactions={len(INTERACTIONS)}, deployments={len(NODES)}, "
        f"business_processes={len(PROCESSES)}, "
        f"access_requests={len(REQUESTS)}, policy_rules={allowed}"
    )
