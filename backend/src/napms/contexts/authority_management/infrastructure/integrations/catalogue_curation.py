from napms.application_catalogue.application.ports import (
    APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
    APPLICATION_CATALOGUE_CURATION_ACTION,
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.resource_catalogue.application.ports import (
    RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
    RESOURCE_CATALOGUE_CURATION_ACTION,
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)


class ApplicationCatalogueCurationAuthorityAdapter:
    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check_curation(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> ApplicationCatalogueAuthorityCheck:
        decision = self._checker.execute(
            actor_id=actor_id,
            action=APPLICATION_CATALOGUE_CURATION_ACTION,
            scope=APPLICATION_CATALOGUE_AUTHORITY_SCOPE,
            effective_time=effective_time,
        )
        outcome = {
            AuthorityOutcome.PERMITTED: ApplicationCatalogueAuthorityOutcome.PERMITTED,
            AuthorityOutcome.DENIED: ApplicationCatalogueAuthorityOutcome.DENIED,
            AuthorityOutcome.UNKNOWN: ApplicationCatalogueAuthorityOutcome.UNKNOWN,
        }[decision.outcome]
        return ApplicationCatalogueAuthorityCheck(
            outcome=outcome,
            authority_reference=(
                decision.authority_reference
                if decision.outcome is AuthorityOutcome.PERMITTED
                else None
            ),
        )


class ResourceCatalogueCurationAuthorityAdapter:
    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check_curation(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> ResourceCatalogueAuthorityCheck:
        decision = self._checker.execute(
            actor_id=actor_id,
            action=RESOURCE_CATALOGUE_CURATION_ACTION,
            scope=RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
            effective_time=effective_time,
        )
        outcome = {
            AuthorityOutcome.PERMITTED: ResourceCatalogueAuthorityOutcome.PERMITTED,
            AuthorityOutcome.DENIED: ResourceCatalogueAuthorityOutcome.DENIED,
            AuthorityOutcome.UNKNOWN: ResourceCatalogueAuthorityOutcome.UNKNOWN,
        }[decision.outcome]
        return ResourceCatalogueAuthorityCheck(
            outcome=outcome,
            authority_reference=(
                decision.authority_reference
                if decision.outcome is AuthorityOutcome.PERMITTED
                else None
            ),
        )
