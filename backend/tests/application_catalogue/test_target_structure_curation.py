from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    CatalogueIdempotencyConflict,
)
from napms.contexts.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target_structure_curation import (
    CreateTargetComponent,
    CreateTargetComponentCommand,
)
from napms.contexts.application_catalogue.domain.model import Application, Component


NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-00000000d001")
LOSER_COMPONENT = UUID("00000000-0000-0000-0000-00000000d002")
WINNER_COMPONENT = UUID("00000000-0000-0000-0000-00000000d003")


class Authority:
    def check_curation(self, *, actor_id, effective_time):
        return ApplicationCatalogueAuthorityCheck(
            ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="authority:catalogue",
        )


class Identities:
    def new_component_id(self):
        return LOSER_COMPONENT


class Provenance:
    def for_component(self, **kwargs):
        return f"prov:component:{kwargs['component_id']}"


class CollisionRepository:
    def __init__(self):
        self.application = Application(APP, "CRM", "prov:app")
        self.winner = Component(
            WINNER_COMPONENT,
            APP,
            "Web",
            "prov:winner",
            component_type="Service",
            description="Web tier",
        )
        self.receipt = None
        self.pending_receipt = None
        self.added = None
        self.commit_calls = 0

    def get_application(self, application_id):
        return self.application if application_id == APP else None

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipt

    def get_component(self, component_id):
        return self.winner if component_id == WINNER_COMPONENT else None

    def add_component(self, component):
        self.added = component

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.pending_receipt = receipt

    def commit(self):
        self.commit_calls += 1
        # Simulate another transaction winning the same actor/key between the
        # initial receipt read and this commit.
        assert self.pending_receipt is not None
        self.receipt = ApplicationCatalogueCommandReceipt(
            command_kind=self.pending_receipt.command_kind,
            request_fingerprint=self.pending_receipt.request_fingerprint,
            result_id=WINNER_COMPONENT,
            result_version=1,
        )
        raise CatalogueIdempotencyConflict()


def test_concurrent_same_target_component_command_resolves_winning_receipt():
    repository = CollisionRepository()
    use_case = CreateTargetComponent(
        authority=Authority(),
        catalogue=repository,
        identities=Identities(),
        provenance=Provenance(),
    )

    result = use_case.execute(
        CreateTargetComponentCommand(
            application_id=APP,
            display_name="Web",
            component_type="Service",
            description="Web tier",
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="component-create-1",
        )
    )

    assert result.outcome is TargetMutationOutcome.RESOLVED
    assert result.component == repository.winner
    assert repository.added.component_id == LOSER_COMPONENT
    assert repository.commit_calls == 1
