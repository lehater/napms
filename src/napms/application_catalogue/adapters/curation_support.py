from datetime import datetime
from urllib.parse import quote
from uuid import UUID, uuid4


class LocalApplicationCatalogueIdentityFactory:
    def new_application_id(self) -> UUID:
        return uuid4()

    def new_component_id(self) -> UUID:
        return uuid4()

    def new_component_deployment_id(self) -> UUID:
        return uuid4()

    def new_dcs_revision_id(self) -> UUID:
        return uuid4()


class LocalDeploymentBindingIdentityFactory:
    def new_binding_reference(self) -> str:
        return f"binding:{uuid4()}"


class LocalApplicationCatalogueProvenanceFactory:
    def for_application(self, **kwargs) -> str:
        return _reference("CreateApplication", kwargs["application_id"], kwargs)

    def for_application_retirement(self, **kwargs) -> str:
        return _reference("RetireApplication", kwargs["application_id"], kwargs)

    def for_component(self, **kwargs) -> str:
        return _reference("CreateComponent", kwargs["component_id"], kwargs)

    def for_component_retirement(self, **kwargs) -> str:
        return _reference("RetireComponent", kwargs["component_id"], kwargs)

    def for_component_deployment(self, **kwargs) -> str:
        return _reference(
            "CreateComponentDeployment",
            kwargs["deployment_id"],
            kwargs,
        )

    def for_component_deployment_retirement(self, **kwargs) -> str:
        return _reference(
            "RetireComponentDeployment",
            kwargs["deployment_id"],
            kwargs,
        )

    def for_dcs_revision(self, **kwargs) -> str:
        return _reference("CreateDcsRevision", kwargs["revision_id"], kwargs)


class LocalDeploymentBindingProvenanceFactory:
    def for_binding(self, **kwargs) -> str:
        return _reference(
            "CreateDeploymentResourceBinding",
            kwargs["binding_reference"],
            kwargs,
        )

    def for_binding_end(self, **kwargs) -> str:
        return _reference(
            "EndDeploymentResourceBinding",
            kwargs["binding_reference"],
            kwargs,
        )


def _reference(operation: str, subject, values: dict) -> str:
    actor_id = _required(values["actor_id"], "actor_id")
    authority_reference = _required(
        values["authority_reference"],
        "authority_reference",
    )
    effective_time = values["effective_time"]
    if not isinstance(effective_time, datetime):
        raise ValueError("effective_time must be datetime")
    if effective_time.tzinfo is None or effective_time.utcoffset() is None:
        raise ValueError("effective_time must be offset-aware")

    return (
        "napms:interactive:acc:"
        f"{quote(operation, safe='')}"
        f"?subject={quote(str(subject), safe='')}"
        f"&actor={quote(actor_id, safe='')}"
        f"&authority={quote(authority_reference, safe='')}"
        f"&at={quote(effective_time.isoformat(), safe='')}"
    )


def _required(value, field_name: str) -> str:
    normalized = str(value).strip() if value is not None else ""
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized
