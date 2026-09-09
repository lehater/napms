from napms.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)


class LocalDevAllowedConnectivityDecisionAdapter:
    """Explicit local-dev-only Decision seam that allows every validated proposal."""

    def obtain(self, *, subject, governance_scope, as_of):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="local-dev:allowed",
        )
