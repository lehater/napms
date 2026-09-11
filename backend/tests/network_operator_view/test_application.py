from datetime import datetime, timezone

from napms.contexts.access_policy_realization.domain.realization import DesiredDerivationStatus
from napms.contexts.access_policy_realization.domain.rendering import RenderStatus
from napms.network_operator_view.application import (
    AuthorityResult,
    Availability,
    ReadNetworkOperatorRealization,
    ReadOutcome,
)

NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)


class Value:
    def __init__(self, status):
        self.status = status


class Authority:
    def __init__(self, result):
        self.result = result

    def check(self, **_):
        return self.result


class Service:
    def __init__(self, value):
        self.value = value
        self.calls = []

    def execute(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.value


def reader(*, authority=None, desired=None, rendered=()):
    return ReadNetworkOperatorRealization(
        authority=authority or Authority(AuthorityResult(True, "authority-1")),
        derive_desired=Service(desired or Value(DesiredDerivationStatus.DERIVED)),
        build_configured=Service(object()),
        reconcile=Service(Value("Satisfied")),
        render=Service(rendered),
    )


def test_missing_configured_and_operation_inputs_remain_not_available():
    rendered = (Value(RenderStatus.RENDERED),)
    result = reader(rendered=rendered).execute(
        actor_id="actor-1",
        scope="scope-1",
        as_of=NOW,
    )

    assert result.outcome is ReadOutcome.AVAILABLE
    assert result.view is not None
    assert result.view.desired.availability is Availability.AVAILABLE
    assert result.view.rendering.availability is Availability.AVAILABLE
    assert result.view.reconciliation.availability is Availability.NOT_AVAILABLE
    assert result.view.operation.availability is Availability.NOT_AVAILABLE


def test_unknown_desired_is_never_promoted_to_available():
    result = reader(
        desired=Value(DesiredDerivationStatus.UNKNOWN),
        rendered=(),
    ).execute(actor_id="actor-1", scope="scope-1", as_of=NOW)

    assert result.view is not None
    assert result.view.desired.availability is Availability.UNKNOWN
    assert result.view.rendering.availability is Availability.NOT_AVAILABLE


def test_unknown_or_denied_authority_returns_no_view():
    unknown = reader(authority=Authority(AuthorityResult(None))).execute(
        actor_id="actor-1", scope="scope-1", as_of=NOW
    )
    denied = reader(authority=Authority(AuthorityResult(False))).execute(
        actor_id="actor-1", scope="scope-1", as_of=NOW
    )

    assert unknown.outcome is ReadOutcome.AUTHORITY_UNKNOWN
    assert unknown.view is None
    assert denied.outcome is ReadOutcome.AUTHORITY_DENIED
    assert denied.view is None
