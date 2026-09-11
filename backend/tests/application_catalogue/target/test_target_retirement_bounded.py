from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.application_catalogue.application.target.curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target.lifecycle import (
    RetireApplicationDefinitionCommand,
    RetirementDependencyKind,
    RetirementMutationResult,
)
from napms.contexts.application_catalogue.application.target.ports import ActiveDependencyReference
from napms.contexts.application_catalogue.application.target.retirement import (
    BoundedRetirementService,
    RetirementSubjectKind,
    TargetRetirementDependencyGroup,
)
from napms.contexts.application_catalogue.domain.model import Application, CatalogueLifecycleState


NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-00000000c001")


class Authority:
    def __init__(self, outcome):
        self.outcome = outcome

    def check_curation(self, *, actor_id, effective_time):
        return ApplicationCatalogueAuthorityCheck(
            outcome=self.outcome,
            authority_reference=(
                "authority:catalogue"
                if self.outcome is ApplicationCatalogueAuthorityOutcome.PERMITTED
                else None
            ),
        )


class DependencyReader:
    def __init__(self, groups=()):
        self.groups = groups
        self.calls = 0

    def summarize(self, **kwargs):
        self.calls += 1
        return self.groups


class Delegate:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def execute(self, command):
        self.calls += 1
        return self.result


def _command():
    return RetireApplicationDefinitionCommand(
        application_id=APP,
        expected_version=1,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key="retire-app",
    )


def _service(*, authority, dependencies, delegate):
    return BoundedRetirementService(
        authority=authority,
        subject_kind=RetirementSubjectKind.APPLICATION_DEFINITION,
        subject_id_attribute="application_id",
        dependencies=dependencies,
        delegate=delegate,
    )


def test_denied_retirement_does_not_disclose_dependency_projection():
    dependencies = DependencyReader(
        (
            TargetRetirementDependencyGroup(
                RetirementDependencyKind.COMPONENTS,
                total=327,
                references=(ActiveDependencyReference("component:1"),),
            ),
        )
    )
    delegate = Delegate(None)

    result = _service(
        authority=Authority(ApplicationCatalogueAuthorityOutcome.DENIED),
        dependencies=dependencies,
        delegate=delegate,
    ).execute(_command())

    assert result.outcome is TargetMutationOutcome.AUTHORITY_DENIED
    assert dependencies.calls == 0
    assert delegate.calls == 0


def test_permitted_retirement_returns_exact_bounded_preflight_without_mutation():
    dependencies = DependencyReader(
        (
            TargetRetirementDependencyGroup(
                RetirementDependencyKind.COMPONENTS,
                total=327,
                references=(
                    ActiveDependencyReference("component:1"),
                    ActiveDependencyReference("component:2"),
                ),
            ),
        )
    )
    delegate = Delegate(None)

    result = _service(
        authority=Authority(ApplicationCatalogueAuthorityOutcome.PERMITTED),
        dependencies=dependencies,
        delegate=delegate,
    ).execute(_command())

    assert result.outcome is TargetMutationOutcome.DEPENDENCY_BLOCKED
    assert result.dependencies[0].count == 327
    assert len(result.dependencies[0].references) == 2
    assert dependencies.calls == 1
    assert delegate.calls == 0


def test_dependency_free_retirement_delegates_to_existing_lifecycle_service():
    dependencies = DependencyReader(())
    retired = Application(
        APP,
        "CRM",
        "prov:app",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:retire",
        version=2,
    )
    delegate = Delegate(
        RetirementMutationResult(
            outcome=TargetMutationOutcome.UPDATED,
            subject=retired,
        )
    )

    result = _service(
        authority=Authority(ApplicationCatalogueAuthorityOutcome.PERMITTED),
        dependencies=dependencies,
        delegate=delegate,
    ).execute(_command())

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert result.subject == retired
    assert dependencies.calls == 1
    assert delegate.calls == 1
