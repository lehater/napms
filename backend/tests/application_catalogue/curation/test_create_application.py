from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.curation.create_application import (
    CreateApplication,
    CreateApplicationCommand,
    CreateApplicationOutcome,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    CatalogueIdempotencyConflict,
)
from napms.contexts.application_catalogue.domain.model import Application


NOW = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000002001")
WINNER_ID = UUID("00000000-0000-0000-0000-000000002002")


class FakeAuthority:
    def __init__(self, outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED):
        self.outcome = outcome
        self.calls = []

    def check_curation(self, **kwargs):
        self.calls.append(kwargs)
        return ApplicationCatalogueAuthorityCheck(
            outcome=self.outcome,
            authority_reference=(
                "auth-acc"
                if self.outcome is ApplicationCatalogueAuthorityOutcome.PERMITTED
                else None
            ),
        )


class FakeApplications:
    def __init__(self):
        self.items = {}
        self.receipts = {}
        self.add_calls = []
        self.commit_count = 0

    def get_application(self, application_id):
        return self.items.get(application_id)

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def add_application(self, application):
        self.add_calls.append(application)
        self.items[application.application_id] = application

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


class RacingApplications(FakeApplications):
    def commit(self):
        self.commit_count += 1
        ((key, attempted_receipt),) = tuple(self.receipts.items())
        winner = Application(
            application_id=WINNER_ID,
            display_name="Checkout",
            provenance_reference="winner:provenance",
        )
        self.items = {WINNER_ID: winner}
        self.receipts = {
            key: ApplicationCatalogueCommandReceipt(
                command_kind=attempted_receipt.command_kind,
                request_fingerprint=attempted_receipt.request_fingerprint,
                result_id=WINNER_ID,
                result_version=winner.version,
            )
        }
        raise CatalogueIdempotencyConflict


class FakeIdentities:
    def __init__(self):
        self.count = 0

    def new_application_id(self):
        self.count += 1
        return APPLICATION_ID


class FakeProvenance:
    def __init__(self):
        self.calls = []

    def for_application(self, **kwargs):
        self.calls.append(kwargs)
        return "local:curation:application"


def service(*, authority=None, applications=None, identities=None, provenance=None):
    authority = authority or FakeAuthority()
    applications = applications or FakeApplications()
    identities = identities or FakeIdentities()
    provenance = provenance or FakeProvenance()
    return (
        CreateApplication(
            authority=authority,
            applications=applications,
            identities=identities,
            provenance=provenance,
        ),
        authority,
        applications,
        identities,
        provenance,
    )


def command(*, display_name="Checkout", key="cmd-1"):
    return CreateApplicationCommand(
        display_name=display_name,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_application_uses_server_identity_and_provenance():
    use_case, authority, applications, identities, provenance = service()

    result = use_case.execute(command(display_name="  Checkout  "))

    assert result.outcome is CreateApplicationOutcome.CREATED
    assert result.application is not None
    assert result.application.application_id == APPLICATION_ID
    assert result.application.display_name == "Checkout"
    assert result.application.provenance_reference == "local:curation:application"
    assert identities.count == 1
    assert provenance.calls == [
        {
            "application_id": APPLICATION_ID,
            "actor_id": "actor-1",
            "authority_reference": "auth-acc",
            "effective_time": NOW,
        }
    ]
    assert applications.commit_count == 1
    assert authority.calls == [{"actor_id": "actor-1", "effective_time": NOW}]


def test_denied_authority_has_no_write_or_identity_allocation():
    use_case, _, applications, identities, provenance = service(
        authority=FakeAuthority(ApplicationCatalogueAuthorityOutcome.DENIED)
    )

    result = use_case.execute(command())

    assert result.outcome is CreateApplicationOutcome.AUTHORITY_DENIED
    assert applications.add_calls == []
    assert applications.commit_count == 0
    assert identities.count == 0
    assert provenance.calls == []


def test_equivalent_retry_returns_original_application_without_second_write():
    use_case, _, applications, identities, _ = service()

    first = use_case.execute(command(display_name="Checkout", key="same-key"))
    second = use_case.execute(command(display_name="  Checkout ", key="same-key"))

    assert first.outcome is CreateApplicationOutcome.CREATED
    assert second.outcome is CreateApplicationOutcome.RESOLVED
    assert second.application is not None
    assert second.application.application_id == APPLICATION_ID
    assert len(applications.add_calls) == 1
    assert applications.commit_count == 1
    assert identities.count == 1


def test_concurrent_equivalent_create_resolves_to_authoritative_winner():
    applications = RacingApplications()
    use_case, _, _, identities, _ = service(applications=applications)

    result = use_case.execute(command(display_name="Checkout", key="race-key"))

    assert result.outcome is CreateApplicationOutcome.RESOLVED
    assert result.application is not None
    assert result.application.application_id == WINNER_ID
    assert identities.count == 1


def test_same_idempotency_key_with_different_semantics_conflicts():
    use_case, _, applications, identities, _ = service()

    first = use_case.execute(command(display_name="Checkout", key="same-key"))
    second = use_case.execute(command(display_name="Orders", key="same-key"))

    assert first.outcome is CreateApplicationOutcome.CREATED
    assert second.outcome is CreateApplicationOutcome.IDEMPOTENCY_CONFLICT
    assert len(applications.add_calls) == 1
    assert identities.count == 1


def test_unknown_authority_fails_closed():
    use_case, _, applications, identities, _ = service(
        authority=FakeAuthority(ApplicationCatalogueAuthorityOutcome.UNKNOWN)
    )

    result = use_case.execute(command())

    assert result.outcome is CreateApplicationOutcome.AUTHORITY_UNKNOWN
    assert applications.add_calls == []
    assert identities.count == 0
