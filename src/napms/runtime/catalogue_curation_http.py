"""Compatibility facade for Catalogue HTTP during staged I32 migration.

Feature endpoints are owned by Application Catalogue and Resource Catalogue adapters.
This module intentionally contains no route implementations.
"""

from fastapi import APIRouter

from napms.application_catalogue.adapters.http.legacy_curation import (
    DcsTrafficAlternativeValue,
    _application_dto,
    _application_tree_dto,
    _binding_dto,
    _component_dto,
    _dcs_revision_dto,
    _deployment_dto,
    _mutation_response,
    _require_actor,
    _require_aware,
    _require_interval,
    _require_success,
    _traffic_alternative,
    create_application_catalogue_curation_router,
)
from napms.resource_catalogue.adapters.http.curation import (
    _realization_dto,
    _resource_detail_dto,
    _resource_dto,
    _resource_persistence_error,
    _responsibility_dto,
    _scope_affiliation_dto,
    create_resource_catalogue_curation_router,
)


def create_catalogue_curation_router(**kwargs) -> APIRouter:
    """Aggregate legacy public Catalogue routes without owning their behavior."""

    router = APIRouter()
    router.include_router(create_application_catalogue_curation_router(**kwargs))
    router.include_router(create_resource_catalogue_curation_router(**kwargs))
    return router


__all__ = [
    "DcsTrafficAlternativeValue",
    "create_catalogue_curation_router",
]
