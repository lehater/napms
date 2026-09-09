from napms.scoped_connectivity_inventory.application.ports import (
    DecisionSummaryReadResult,
    DependencyAvailability,
)


class DeferredConnectivityDecisionSummaryAdapter:
    """I16A-safe seam until the durable I16B Decision provider exists."""

    def summarize_decisions(
        self,
        *,
        responsibility_scope,
        identities,
        as_of,
    ) -> DecisionSummaryReadResult:
        return DecisionSummaryReadResult(DependencyAvailability.UNAVAILABLE)
