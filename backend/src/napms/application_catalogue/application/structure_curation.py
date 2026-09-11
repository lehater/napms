"""Compatibility exports for pre-M5 Application Catalogue structure mutation imports."""

from napms.application_catalogue.application.application_structure_curation import (
    ApplicationMutationResult,
    RenameApplication,
    RenameApplicationCommand,
    RetireApplication,
    RetireApplicationCommand,
)
from napms.application_catalogue.application.component_structure_curation import (
    ComponentMutationResult,
    CreateComponent,
    CreateComponentCommand,
    RenameComponent,
    RenameComponentCommand,
    RetireComponent,
    RetireComponentCommand,
)
from napms.application_catalogue.application.curation_mutation import (
    CatalogueMutationOutcome,
)

__all__ = [
    "ApplicationMutationResult",
    "CatalogueMutationOutcome",
    "ComponentMutationResult",
    "CreateComponent",
    "CreateComponentCommand",
    "RenameApplication",
    "RenameApplicationCommand",
    "RenameComponent",
    "RenameComponentCommand",
    "RetireApplication",
    "RetireApplicationCommand",
    "RetireComponent",
    "RetireComponentCommand",
]
