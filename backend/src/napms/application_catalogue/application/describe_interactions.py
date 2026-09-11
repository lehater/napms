from dataclasses import dataclass

from napms.application_catalogue.application.ports import ApplicationCatalogueRepository
from napms.application_catalogue.domain.model import DirectedInteractionIdentity


@dataclass(frozen=True, slots=True)
class DirectedInteractionDescription:
    identity: DirectedInteractionIdentity
    source_display_name: str | None
    destination_display_name: str | None
    dcs_display_name: str | None
    dcs_projection_payload: bytes | None
    dcs_provenance_reference: str | None


class DescribeDirectedInteractions:
    """Describe exact identities already admitted by an enclosing use case."""

    def __init__(self, *, catalogue: ApplicationCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        identities: tuple[DirectedInteractionIdentity, ...],
    ) -> tuple[DirectedInteractionDescription, ...]:
        if not identities:
            return ()

        deployment_ids = tuple(
            dict.fromkeys(
                deployment_id
                for identity in identities
                for deployment_id in (
                    identity.source_component_deployment_id,
                    identity.destination_component_deployment_id,
                )
            )
        )
        revision_ids = tuple(
            dict.fromkeys(
                identity.dcs_contract_revision_id for identity in identities
            )
        )

        deployments = {
            deployment.deployment_id: deployment
            for deployment in self._catalogue.get_component_deployments(deployment_ids)
        }
        revisions = {
            revision.revision_id: revision
            for revision in self._catalogue.get_dcs_revisions(revision_ids)
        }

        descriptions: list[DirectedInteractionDescription] = []
        for identity in identities:
            source = deployments.get(identity.source_component_deployment_id)
            destination = deployments.get(
                identity.destination_component_deployment_id
            )
            revision = revisions.get(identity.dcs_contract_revision_id)

            exact_revision = (
                revision
                if revision is not None
                and revision.source_component_deployment_id
                == identity.source_component_deployment_id
                and revision.destination_component_deployment_id
                == identity.destination_component_deployment_id
                else None
            )

            descriptions.append(
                DirectedInteractionDescription(
                    identity=identity,
                    source_display_name=(
                        source.display_name if source is not None else None
                    ),
                    destination_display_name=(
                        destination.display_name
                        if destination is not None
                        else None
                    ),
                    dcs_display_name=(
                        exact_revision.display_name
                        if exact_revision is not None
                        else None
                    ),
                    dcs_projection_payload=(
                        exact_revision.projection_payload
                        if exact_revision is not None
                        else None
                    ),
                    dcs_provenance_reference=(
                        exact_revision.provenance_reference
                        if exact_revision is not None
                        else None
                    ),
                )
            )

        return tuple(descriptions)
