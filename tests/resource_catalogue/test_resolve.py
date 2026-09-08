from datetime import datetime, timedelta, timezone

from napms.policy_export.application.ports import (
    ResourceRealizationOutcome,
    ResourceReference,
)
from napms.resource_catalogue.adapters.policy_export import (
    PolicyExportResourceCatalogueAdapter,
)
from napms.resource_catalogue.application.resolve import (
    ResolveResourceRealization,
    ResourceResolutionOutcome,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceRealizationVersion,
)


AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)


def realization(reference="fact-1", resource="resource-1"):
    return ResourceRealizationVersion(
        fact_reference=reference,
        resource_reference=resource,
        endpoint_realizations=(
            EndpointAddress("endpoint-b", "203.0.113.2"),
            EndpointAddress("endpoint-a", "203.0.113.1"),
        ),
        valid_from=AS_OF - timedelta(days=1),
        valid_to=AS_OF + timedelta(days=1),
        provenance_reference=f"provenance-{reference}",
    )


class FakeCatalogue:
    def __init__(self, matches=(), has_facts=False):
        self.matches = tuple(matches)
        self.has_facts = has_facts

    def find_effective_realizations(self, *, resource_reference, as_of):
        return self.matches

    def has_realization_facts(self, *, resource_reference):
        return self.has_facts


def test_single_effective_realization_is_resolved_deterministically():
    result = ResolveResourceRealization(
        catalogue=FakeCatalogue([realization()], has_facts=True)
    ).execute(resource_reference="resource-1", as_of=AS_OF)

    assert result.outcome is ResourceResolutionOutcome.RESOLVED
    assert result.resource_reference == "resource-1"
    assert result.endpoint_realizations == (
        EndpointAddress("endpoint-a", "203.0.113.1"),
        EndpointAddress("endpoint-b", "203.0.113.2"),
    )
    assert result.fact_reference == "fact-1"
    assert result.validity_reference == "rc-validity:fact-1"
    assert result.provenance_reference == "provenance-fact-1"


def test_no_known_fact_is_missing():
    result = ResolveResourceRealization(catalogue=FakeCatalogue()).execute(
        resource_reference="resource-1",
        as_of=AS_OF,
    )
    assert result.outcome is ResourceResolutionOutcome.MISSING


def test_known_but_not_effective_fact_is_stale():
    result = ResolveResourceRealization(
        catalogue=FakeCatalogue(has_facts=True)
    ).execute(resource_reference="resource-1", as_of=AS_OF)

    assert result.outcome is ResourceResolutionOutcome.STALE


def test_overlapping_effective_versions_fail_closed_unknown():
    result = ResolveResourceRealization(
        catalogue=FakeCatalogue(
            [realization("fact-1"), realization("fact-2")],
            has_facts=True,
        )
    ).execute(resource_reference="resource-1", as_of=AS_OF)

    assert result.outcome is ResourceResolutionOutcome.UNKNOWN


def test_policy_export_adapter_preserves_exact_resource_and_provenance():
    adapter = PolicyExportResourceCatalogueAdapter(
        resolver=ResolveResourceRealization(
            catalogue=FakeCatalogue([realization()], has_facts=True)
        )
    )

    result = adapter.resolve_realization(
        resource_reference=ResourceReference("resource-1"),
        as_of=AS_OF,
    )

    assert result.outcome is ResourceRealizationOutcome.RESOLVED
    assert result.resource_reference == ResourceReference("resource-1")
    assert result.as_of == AS_OF
    assert tuple(
        (endpoint.endpoint_reference, endpoint.technical_address)
        for endpoint in result.endpoint_realizations
    ) == (
        ("endpoint-a", "203.0.113.1"),
        ("endpoint-b", "203.0.113.2"),
    )
    assert result.fact_reference == "fact-1"
    assert result.validity_reference == "rc-validity:fact-1"
    assert result.provenance_reference == "provenance-fact-1"
