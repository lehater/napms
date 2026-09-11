from datetime import datetime
from urllib.parse import quote
from uuid import uuid4


class LocalResourceCatalogueIdentityFactory:
    def new_resource_reference(self) -> str:
        return f"resource:{uuid4()}"

    def new_realization_reference(self) -> str:
        return f"realization:{uuid4()}"

    def new_endpoint_reference(self) -> str:
        return f"endpoint:{uuid4()}"

    def new_scope_affiliation_reference(self) -> str:
        return f"affiliation:{uuid4()}"

    def new_responsibility_reference(self) -> str:
        return f"responsibility:{uuid4()}"


class LocalResourceCatalogueProvenanceFactory:
    def for_resource(self, **kwargs) -> str:
        return _reference("CreateResource", kwargs["resource_reference"], kwargs)

    def for_resource_retirement(self, **kwargs) -> str:
        return _reference("RetireResource", kwargs["resource_reference"], kwargs)

    def for_realization(self, **kwargs) -> str:
        return _reference("CreateResourceRealization", kwargs["fact_reference"], kwargs)

    def for_realization_end(self, **kwargs) -> str:
        return _reference("EndResourceRealization", kwargs["fact_reference"], kwargs)

    def for_scope_affiliation(self, **kwargs) -> str:
        return _reference(
            "CreateResourceScopeAffiliation",
            kwargs["affiliation_reference"],
            kwargs,
        )

    def for_scope_affiliation_end(self, **kwargs) -> str:
        return _reference(
            "EndResourceScopeAffiliation",
            kwargs["affiliation_reference"],
            kwargs,
        )

    def for_responsibility(self, **kwargs) -> str:
        return _reference(
            "CreateResourceResponsibility",
            kwargs["assignment_reference"],
            kwargs,
        )

    def for_responsibility_end(self, **kwargs) -> str:
        return _reference(
            "EndResourceResponsibility",
            kwargs["assignment_reference"],
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
        "napms:interactive:rc:"
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
