from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from napms.contexts.access_policy.application.service import AccessPolicyService
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    RequestAuthorityEvidence,
)
from napms.contexts.application_communication_catalogue.application.ports import (
    InteractionResolver,
    InteractionRevisionResolver,
)
from napms.contexts.application_deployment.application.ports import (
    ComponentDeploymentRepository,
)
from napms.contexts.authority_management.application.service import RequireScopedAuthority
from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.business_connectivity.application.ports import CurrentNeedLocker
from napms.contexts.resource_catalogue.application.ports import AuthorityScopeResolver


ACCESS_REQUEST_ACTION = "access.request"


class AccessRequestSubmissionRejected(Exception):
    pass


class AccessRequestSubmissionService:
    def __init__(
        self,
        *,
        policy: AccessPolicyService,
        needs: CurrentNeedLocker,
        deployments: ComponentDeploymentRepository,
        revisions: InteractionRevisionResolver,
        interactions: InteractionResolver,
        resource_scopes: AuthorityScopeResolver,
        authority: RequireScopedAuthority,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._policy = policy
        self._needs = needs
        self._deployments = deployments
        self._revisions = revisions
        self._interactions = interactions
        self._resource_scopes = resource_scopes
        self._authority = authority
        self._new_ref = new_ref

    def submit(
        self,
        *,
        principal: Principal,
        source_deployment_ref: UUID,
        destination_deployment_ref: UUID,
        interaction_revision_ref: UUID,
        need_ref: UUID,
        admission_at: datetime,
    ) -> AccessRequest:
        locked = self._needs.lock_current_need(need_ref)
        if locked is None:
            raise AccessRequestSubmissionRejected("need is not current")
        need, process_version = locked

        source = self._deployments.resolve_deployment(source_deployment_ref)
        destination = self._deployments.resolve_deployment(destination_deployment_ref)
        if source is None or destination is None:
            raise AccessRequestSubmissionRejected("deployment reference is unresolved")

        resolved_revision = self._revisions.resolve_revision(interaction_revision_ref)
        if resolved_revision is None:
            raise AccessRequestSubmissionRejected("interaction revision is unresolved")

        interaction = self._interactions.get_interaction(resolved_revision.interaction_ref)
        if interaction is None:
            raise AccessRequestSubmissionRejected("owning interaction is unresolved")

        if need.interaction_ref != interaction.interaction_ref:
            raise AccessRequestSubmissionRejected("need does not justify the selected interaction")
        if source.component_ref != interaction.source_component_ref:
            raise AccessRequestSubmissionRejected(
                "source deployment does not realize interaction source"
            )
        if destination.component_ref != interaction.destination_component_ref:
            raise AccessRequestSubmissionRejected(
                "destination deployment does not realize interaction destination"
            )
        if need.participant_component_ref not in (
            interaction.source_component_ref,
            interaction.destination_component_ref,
        ):
            raise AccessRequestSubmissionRejected("need participant is not an interaction endpoint")

        source_scope = self._resource_scopes.resolve_authority_scope(source.resource_ref)
        destination_scope = self._resource_scopes.resolve_authority_scope(destination.resource_ref)
        if source_scope is None or destination_scope is None:
            raise AccessRequestSubmissionRejected("resource authority scope is unresolved")
        scopes = tuple(dict.fromkeys((source_scope, destination_scope)))

        authority_evidence = self._authority.require(
            principal=principal,
            action=ACCESS_REQUEST_ACTION,
            scopes=scopes,
            evaluated_at=admission_at,
        )
        persisted_evidence = tuple(
            RequestAuthorityEvidence(
                evidence_ref=self._new_ref(),
                scope_ref=item.scope,
                action=item.action,
                grant_effective_from=item.effective_from,
                grant_effective_until=item.effective_until,
                evaluated_at=item.evaluated_at,
            )
            for item in sorted(authority_evidence, key=lambda value: (value.scope, value.action))
        )

        return self._policy.submit_validated_request(
            access_subject=AccessSubject(
                source_deployment_ref=source_deployment_ref,
                destination_deployment_ref=destination_deployment_ref,
                interaction_revision_ref=interaction_revision_ref,
            ),
            initial_need_ref=need_ref,
            validated_business_process_version=process_version,
            submitter_subject=principal.subject,
            submitted_at=admission_at,
            authority_evidence=persisted_evidence,
        )
