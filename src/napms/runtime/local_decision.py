from napms.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)


class LocalDevAllowedConnectivityDecisionAdapter:
    """Explicit local-dev-only Decision seam that allows every validated proposal."""

    def obtain(self, *, subject):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            decision_reference="local-dev:allowed",
        )
