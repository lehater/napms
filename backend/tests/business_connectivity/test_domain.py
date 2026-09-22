from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.business_connectivity.domain.model import (
    BusinessProcess,
    ConnectivityNeed,
    NeedStatus,
)


NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


def test_need_is_business_justification_with_explicit_lifecycle() -> None:
    need = ConnectivityNeed.declare(
        need_ref=UUID(int=1),
        interaction_ref=UUID(int=2),
        participant_component_ref=UUID(int=3),
        business_basis="Order processing",
        created_by_subject="subject:alice",
    )
    retired = need.retire(retired_at=NOW)

    assert need.status is NeedStatus.ACTIVE
    assert retired.status is NeedStatus.RETIRED
    assert retired.interaction_ref == need.interaction_ref
    assert retired.participant_component_ref == need.participant_component_ref


def test_criticality_is_opaque_descriptive_text() -> None:
    process = BusinessProcess.register(
        process_ref=UUID(int=10),
        name="Order fulfillment",
        criticality_label="Tier-37 custom",
    )
    assert process.criticality_label == "Tier-37 custom"
