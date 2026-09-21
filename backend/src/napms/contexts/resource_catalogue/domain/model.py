from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from ipaddress import ip_address, ip_network
from uuid import UUID


class AddressKind(str, Enum):
    HOST = "HOST"
    PREFIX = "PREFIX"


class ResponsibilityRole(str, Enum):
    OWNER = "OWNER"
    ADMINISTRATOR = "ADMINISTRATOR"


@dataclass(frozen=True)
class AddressRealization:
    kind: AddressKind
    value: str

    @classmethod
    def host(cls, value: str) -> "AddressRealization":
        return cls(kind=AddressKind.HOST, value=str(ip_address(value)))

    @classmethod
    def prefix(cls, value: str) -> "AddressRealization":
        return cls(kind=AddressKind.PREFIX, value=str(ip_network(value, strict=True)))


@dataclass(frozen=True)
class AddressFact:
    address: AddressRealization
    effective_from: datetime
    effective_to: datetime | None
    changed_by_subject: str


@dataclass(frozen=True)
class SiteFact:
    site_ref: UUID
    effective_from: datetime
    effective_to: datetime | None
    changed_by_subject: str


@dataclass(frozen=True)
class ResponsibilityFact:
    role: ResponsibilityRole
    group_ref: UUID
    effective_from: datetime
    effective_to: datetime | None
    changed_by_subject: str


@dataclass(frozen=True)
class ResourceEndpoint:
    endpoint_ref: UUID
    current_address: AddressFact | None = None
    address_history: tuple[AddressFact, ...] = ()

    def set_address(
        self,
        address: AddressRealization,
        *,
        effective_at: datetime,
        subject: str,
    ) -> "ResourceEndpoint":
        _require_aware(effective_at)
        history = self.address_history
        if self.current_address is not None:
            _require_later(effective_at, self.current_address.effective_from)
            history += (replace(self.current_address, effective_to=effective_at),)
        return replace(
            self,
            current_address=AddressFact(
                address=address,
                effective_from=effective_at,
                effective_to=None,
                changed_by_subject=subject,
            ),
            address_history=history,
        )

    def clear_address(self, *, effective_at: datetime, subject: str) -> "ResourceEndpoint":
        _require_aware(effective_at)
        if self.current_address is None:
            return self
        _require_later(effective_at, self.current_address.effective_from)
        ended = replace(
            self.current_address,
            effective_to=effective_at,
            changed_by_subject=subject,
        )
        return replace(self, current_address=None, address_history=self.address_history + (ended,))


@dataclass(frozen=True)
class Resource:
    resource_ref: UUID
    display_name: str
    authority_scope_ref: str
    version: int
    endpoints: tuple[ResourceEndpoint, ...] = ()
    current_site: SiteFact | None = None
    site_history: tuple[SiteFact, ...] = ()
    responsibilities: tuple[ResponsibilityFact, ...] = ()
    responsibility_history: tuple[ResponsibilityFact, ...] = ()

    @classmethod
    def register(
        cls,
        *,
        resource_ref: UUID,
        display_name: str,
        authority_scope_ref: str,
    ) -> "Resource":
        display_name = display_name.strip()
        authority_scope_ref = authority_scope_ref.strip()
        if not display_name:
            raise ValueError("display_name must be non-empty")
        if not authority_scope_ref:
            raise ValueError("authority_scope_ref must be non-empty")
        return cls(
            resource_ref=resource_ref,
            display_name=display_name,
            authority_scope_ref=authority_scope_ref,
            version=1,
        )

    def add_endpoint(self, endpoint_ref: UUID) -> "Resource":
        if any(endpoint.endpoint_ref == endpoint_ref for endpoint in self.endpoints):
            raise ValueError("endpoint_ref already belongs to resource")
        return replace(
            self,
            endpoints=self.endpoints + (ResourceEndpoint(endpoint_ref=endpoint_ref),),
            version=self.version + 1,
        )

    def set_endpoint_address(
        self,
        endpoint_ref: UUID,
        address: AddressRealization,
        *,
        effective_at: datetime,
        subject: str,
    ) -> "Resource":
        endpoint = self._endpoint(endpoint_ref)
        updated = endpoint.set_address(address, effective_at=effective_at, subject=subject)
        if updated is endpoint:
            return self
        return replace(
            self,
            endpoints=tuple(updated if item.endpoint_ref == endpoint_ref else item for item in self.endpoints),
            version=self.version + 1,
        )

    def clear_endpoint_address(
        self,
        endpoint_ref: UUID,
        *,
        effective_at: datetime,
        subject: str,
    ) -> "Resource":
        endpoint = self._endpoint(endpoint_ref)
        updated = endpoint.clear_address(effective_at=effective_at, subject=subject)
        if updated == endpoint:
            return self
        return replace(
            self,
            endpoints=tuple(updated if item.endpoint_ref == endpoint_ref else item for item in self.endpoints),
            version=self.version + 1,
        )

    def set_site(
        self,
        site_ref: UUID | None,
        *,
        effective_at: datetime,
        subject: str,
    ) -> "Resource":
        _require_aware(effective_at)
        history = self.site_history
        if self.current_site is not None:
            _require_later(effective_at, self.current_site.effective_from)
            history += (replace(self.current_site, effective_to=effective_at),)
        current = (
            None
            if site_ref is None
            else SiteFact(
                site_ref=site_ref,
                effective_from=effective_at,
                effective_to=None,
                changed_by_subject=subject,
            )
        )
        return replace(
            self,
            current_site=current,
            site_history=history,
            version=self.version + 1,
        )

    def set_responsibility(
        self,
        role: ResponsibilityRole,
        group_ref: UUID | None,
        *,
        effective_at: datetime,
        subject: str,
    ) -> "Resource":
        _require_aware(effective_at)
        current_for_role = next(
            (item for item in self.responsibilities if item.role is role),
            None,
        )
        history = self.responsibility_history
        if current_for_role is not None:
            _require_later(effective_at, current_for_role.effective_from)
            history += (replace(current_for_role, effective_to=effective_at),)
        remaining = tuple(item for item in self.responsibilities if item.role is not role)
        current = (
            ()
            if group_ref is None
            else (
                ResponsibilityFact(
                    role=role,
                    group_ref=group_ref,
                    effective_from=effective_at,
                    effective_to=None,
                    changed_by_subject=subject,
                ),
            )
        )
        return replace(
            self,
            responsibilities=remaining + current,
            responsibility_history=history,
            version=self.version + 1,
        )

    def _endpoint(self, endpoint_ref: UUID) -> ResourceEndpoint:
        for endpoint in self.endpoints:
            if endpoint.endpoint_ref == endpoint_ref:
                return endpoint
        raise KeyError(f"unknown endpoint_ref: {endpoint_ref}")


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("effective time must be timezone-aware")


def _require_later(value: datetime, previous: datetime) -> None:
    if value <= previous:
        raise ValueError("replacement time must be later than current fact")
