import pytest
from psycopg import Error as PsycopgError

from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.transactional_curation_repository import (
    TransactionalPostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueCommandReceipt,
    ResourceCataloguePersistenceError,
    ResourceCataloguePersistenceOutcomeUnknown,
)


class Connection:
    def __init__(self, *, execute_error=None, commit_error=None):
        self.execute_error = execute_error
        self.commit_error = commit_error
        self.rollbacks = 0
        self.commits = 0

    def execute(self, *_args, **_kwargs):
        if self.execute_error is not None:
            raise self.execute_error
        return object()

    def commit(self):
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self):
        self.rollbacks += 1


def repository(connection):
    value = TransactionalPostgresResourceCatalogueCurationRepository(connection)
    value.record_command_receipt(
        actor_id="actor-1",
        idempotency_key="request-1",
        receipt=ResourceCatalogueCommandReceipt(
            command_kind="CreateResource",
            request_fingerprint="fingerprint",
            result_reference="resource:1",
            result_version=1,
        ),
    )
    return value


def test_receipt_insert_failure_is_known_persistence_failure_before_commit():
    connection = Connection(execute_error=PsycopgError("insert failed"))

    with pytest.raises(ResourceCataloguePersistenceError) as caught:
        repository(connection).commit()

    assert not isinstance(caught.value, ResourceCataloguePersistenceOutcomeUnknown)
    assert connection.rollbacks == 1
    assert connection.commits == 0


def test_commit_acknowledgement_failure_is_outcome_unknown():
    connection = Connection(commit_error=PsycopgError("commit acknowledgement failed"))

    with pytest.raises(ResourceCataloguePersistenceOutcomeUnknown):
        repository(connection).commit()

    assert connection.rollbacks == 0
    assert connection.commits == 1
