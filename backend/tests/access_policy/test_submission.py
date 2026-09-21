from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.application.submission import (
    AccessRequestSubmissionRejected,
    AccessRequestSubmissionService,
)
from napms.contexts.access_policy.domain.model import AccessRequest, AccessSubject, PolicyRule
from napms.contexts.application_communication_catalogue.application.ports import (
    ResolvedInteractionRevision,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Interaction,
    InteractionRevision,
    TrafficClause,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.authority_management.application.service import RequireScopedAuthority
from napms.contexts.authority_management.domain.model import AuthorityGrant, Principal
from napms.contexts.business_connectivity.domain.model import ConnectivityNeed
from napms.contexts.resource_catalogue.application.ports import AuthorityScopeResolver


NOW = datetime(2026, 9, 21, 16, 0, tzinfo=timezone.utc)


class Requests:
    def __init__(self) -> None:
        self.values: dict[UUID, AccessRequest] = {}

    def add_request(self, request: AccessRequest) -> None:
        self.values[request.request_ref] = request

    def get_request(self, request_ref: UUID) -> AccessRequest | None:
        return self.values.get(request_ref)

    def save_request(self, request: AccessRequest, *, expected_version: int) -> None:
        raise AssertionError("not used")


class Rules:
    def find_rule_by_subject(self, subject: AccessSubject) -> PolicyRule | None:
        return None

    def add_rule(self, rule: PolicyRule) -> None:
        raise AssertionError("not used")

    def save_rule(self, rule: PolicyRule, *, expected_version: int) -> None:
        raise AssertionError("not used")

    def get_rule(self, rule_ref: UUID) -> PolicyRule | None:
        return None


class Needs:
    def __init__(self, need: ConnectivityNeed | None, version: int = 1) -> None:
        self.need = need
        self.version = version

    def lock_current_need(self, need_ref: UUID):
        if self.need is None or self.need.need_ref != need_ref:
            return None
        return self.need, self.version


class Deployments:
    def __init__(self, *values: ComponentDeployment) -> None:
        self.values = {item.deployment_ref: item for item in values}

    def add(self, deployment: ComponentDeployment) -> None:
        raise AssertionError("not used")

    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None:
        return self.values.get(deployment_ref)


class Revisions:
    def __init__(self, value: ResolvedInteractionRevision) -> None:
        self.value = value

    def resolve_revision(self, revision_ref: UUID) -> ResolvedInteractionRevision | None:
        if self.value.revision.revision_ref == revision_ref:
            return self.value
        return None


class Interactions:
    def __init__(self, value: Interaction) -> None:
        self.value = value

    def get_interaction(self, interaction_ref: UUID) -> Interaction | None:
        return self.value if self.value.interaction_ref == interaction_ref else None


class Scopes(AuthorityScopeResolver):
    def __init__(self, values: dict[UUID, str]) -> None:
        self.values = values

    def resolve_authority_scope(self, resource_ref: UUID) -> str | None:
        return self.values.get(resource_ref)


class Refs:
    def __init__(self, *values: UUID) -> None:
        self.values = iter(values)

    def __call__(self) -> UUID:
        return next(self.values)


def fixture_service():
    interaction = Interaction.create(
        interaction_ref=UUID(int=20),
        source_component_ref=UUID(int=21),
        destination_component_ref=UUID(int=22),
        purpose="orders",
    )
    revision = InteractionRevision(
        revision_ref=UUID(int=23),
        revision_no=1,
        traffic_clauses=(TrafficClause(ip_protocol=1),),
        created_by_subject="subject:author",
    )
    need = ConnectivityNeed.declare(
        need_ref=UUID(int=24),
        interaction_ref=interaction.interaction_ref,
        participant_component_ref=interaction.source_component_ref,
        business_basis="orders",
        created_by_subject="subject:business",
    )
    source = ComponentDeployment(
        deployment_ref=UUID(int=25),
        component_ref=interaction.source_component_ref,
        resource_ref=UUID(int=27),
    )
    destination = ComponentDeployment(
        deployment_ref=UUID(int=26),
        component_ref=interaction.destination_component_ref,
        resource_ref=UUID(int=28),
    )
    requests = Requests()
    refs = Refs(UUID(int=30), UUID(int=31), UUID(int=32))
    policy = AccessPolicyService(requests=requests, rules=Rules(), new_ref=refs)
    service = AccessRequestSubmissionService(
        policy=policy,
        needs=Needs(need, version=7),
        deployments=Deployments(source, destination),
        revisions=Revisions(
            ResolvedInteractionRevision(
                interaction_ref=interaction.interaction_ref,
                revision=revision,
            )
        ),
        interactions=Interactions(interaction),
        resource_scopes=Scopes(
            {
                source.resource_ref: "scope:source",
                destination.resource_ref: "scope:destination",
            }
        ),
        authority=RequireScopedAuthority(),
        new_ref=refs,
    )
    return service, requests, source, destination, revision, need


def test_submission_requires_every_distinct_resource_scope_and_persists_exact_evidence() -> None:
    service, requests, source, destination, revision, need = fixture_service()
    principal = Principal(
        subject="subject:alice",
        authority_grants=(
            AuthorityGrant(action="access.request", scope="scope:source"),
            AuthorityGrant(action="access.request", scope="scope:destination"),
        ),
    )

    request = service.submit(
        principal=principal,
        source_deployment_ref=source.deployment_ref,
        destination_deployment_ref=destination.deployment_ref,
        interaction_revision_ref=revision.revision_ref,
        need_ref=need.need_ref,
        admission_at=NOW,
    )

    assert request.validated_business_process_version == 7
    assert {item.scope_ref for item in request.authority_evidence} == {
        "scope:source",
        "scope:destination",
    }
    assert all(item.evaluated_at == NOW for item in request.authority_evidence)
    assert requests.values[request.request_ref] == request


def test_submission_rejects_deployment_pair_that_does_not_realize_interaction() -> None:
    service, _, source, destination, revision, need = fixture_service()
    principal = Principal(
        subject="subject:alice",
        authority_grants=(
            AuthorityGrant(action="access.request", scope="scope:source"),
            AuthorityGrant(action="access.request", scope="scope:destination"),
        ),
    )
    wrong_source = UUID(int=999)

    with pytest.raises(AccessRequestSubmissionRejected):
        service.submit(
            principal=principal,
            source_deployment_ref=wrong_source,
            destination_deployment_ref=destination.deployment_ref,
            interaction_revision_ref=revision.revision_ref,
            need_ref=need.need_ref,
            admission_at=NOW,
        )
