from napms.contexts.access_policy_realization.domain.realization import (
    ConfiguredEnforcementSnapshot,
    DesiredEnforcementPolicy,
    PolicyReconciliation,
    reconcile_enforcement_policy,
)


class ReconcileEnforcementPolicy:
    def execute(
        self,
        *,
        desired: DesiredEnforcementPolicy,
        configured: ConfiguredEnforcementSnapshot,
    ) -> PolicyReconciliation:
        return reconcile_enforcement_policy(
            desired=desired,
            configured=configured,
        )
