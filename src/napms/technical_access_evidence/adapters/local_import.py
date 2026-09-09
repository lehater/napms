import json
from datetime import datetime

from napms.technical_access_evidence.application.record import RecordEvidenceSet
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceAction,
    EvidenceInvariantError,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntryPayload,
    TechnicalAccessPredicate,
)


class LocalEvidenceImportError(ValueError):
    """Local import payload cannot be normalized without semantic loss."""


class LocalEvidenceImportAdapter:
    """Strict local JSON import -> source-neutral TAE record command."""

    _SOURCE_NAMESPACE = "local-import"

    def normalize(self, raw: str | bytes) -> RecordEvidenceSet:
        try:
            document = json.loads(raw, object_pairs_hook=self._object_from_pairs)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise LocalEvidenceImportError("invalid JSON import payload") from exc

        try:
            root = self._require_object(document, field_name="document")
            self._reject_unknown(
                root,
                {
                    "source_reference",
                    "source_scope_reference",
                    "source_capture_reference",
                    "evidence_time",
                    "entries",
                },
                field_name="document",
            )
            entries = root.get("entries")
            if not isinstance(entries, list):
                raise LocalEvidenceImportError("entries must be a JSON array")

            return RecordEvidenceSet(
                kind=EvidenceKind.IMPORTED,
                source=EvidenceSourceReference(
                    self._SOURCE_NAMESPACE,
                    self._require_string(
                        root.get("source_reference"),
                        field_name="source_reference",
                    ),
                ),
                source_scope=SourceScopeReference(
                    self._require_string(
                        root.get("source_scope_reference"),
                        field_name="source_scope_reference",
                    )
                ),
                source_capture_reference=SourceCaptureReference(
                    self._require_string(
                        root.get("source_capture_reference"),
                        field_name="source_capture_reference",
                    )
                ),
                evidence_time=self._evidence_time(root.get("evidence_time")),
                entries=tuple(
                    self._entry(item, index=index)
                    for index, item in enumerate(entries)
                ),
            )
        except EvidenceInvariantError as exc:
            raise LocalEvidenceImportError(str(exc)) from exc

    def _entry(self, raw, *, index: int) -> TechnicalAccessEntryPayload:
        value = self._require_object(raw, field_name=f"entries[{index}]")
        self._reject_unknown(
            value,
            {
                "source_addresses",
                "destination_addresses",
                "protocol",
                "source_ports",
                "destination_ports",
                "action",
                "source_entry_reference",
                "source_position",
            },
            field_name=f"entries[{index}]",
        )

        action = value.get("action")
        if action is not None:
            try:
                normalized_action = EvidenceAction(
                    self._require_string(
                        action,
                        field_name=f"entries[{index}].action",
                    )
                )
            except ValueError as exc:
                raise LocalEvidenceImportError(
                    f"entries[{index}].action must be Permit or Block"
                ) from exc
        else:
            normalized_action = None

        source_position = value.get("source_position")
        if source_position is not None and (
            not isinstance(source_position, int)
            or isinstance(source_position, bool)
            or source_position < 0
        ):
            raise LocalEvidenceImportError(
                f"entries[{index}].source_position must be a non-negative integer"
            )

        source_entry_reference = value.get("source_entry_reference")
        if source_entry_reference is not None:
            source_entry_reference = self._require_string(
                source_entry_reference,
                field_name=f"entries[{index}].source_entry_reference",
            )

        return TechnicalAccessEntryPayload(
            predicate=TechnicalAccessPredicate(
                source_addresses=self._addresses(
                    value.get("source_addresses"),
                    field_name=f"entries[{index}].source_addresses",
                ),
                destination_addresses=self._addresses(
                    value.get("destination_addresses"),
                    field_name=f"entries[{index}].destination_addresses",
                ),
                protocol=self._protocol(
                    value.get("protocol"),
                    field_name=f"entries[{index}].protocol",
                ),
                source_ports=self._ports(
                    value.get("source_ports"),
                    field_name=f"entries[{index}].source_ports",
                ),
                destination_ports=self._ports(
                    value.get("destination_ports"),
                    field_name=f"entries[{index}].destination_ports",
                ),
            ),
            action=normalized_action,
            source_entry_reference=source_entry_reference,
            source_position=source_position,
        )

    def _evidence_time(self, raw) -> EvidenceTime:
        value = self._require_object(raw, field_name="evidence_time")
        kind = self._require_string(
            value.get("kind"),
            field_name="evidence_time.kind",
        )
        if kind == "Unknown":
            self._reject_unknown(
                value,
                {"kind"},
                field_name="evidence_time",
            )
            return EvidenceTime.unknown()
        if kind == "Instant":
            self._reject_unknown(
                value,
                {"kind", "at"},
                field_name="evidence_time",
            )
            return EvidenceTime.instant(
                self._datetime(
                    value.get("at"),
                    field_name="evidence_time.at",
                )
            )
        if kind == "Window":
            self._reject_unknown(
                value,
                {"kind", "start", "end"},
                field_name="evidence_time",
            )
            return EvidenceTime.window(
                self._datetime(
                    value.get("start"),
                    field_name="evidence_time.start",
                ),
                self._datetime(
                    value.get("end"),
                    field_name="evidence_time.end",
                ),
            )
        raise LocalEvidenceImportError(
            "evidence_time.kind must be Unknown, Instant or Window"
        )

    def _addresses(self, raw, *, field_name: str) -> AddressConstraint:
        value = self._require_object(raw, field_name=field_name)
        kind = self._require_string(
            value.get("kind"),
            field_name=f"{field_name}.kind",
        )
        if kind == "Any":
            self._reject_unknown(value, {"kind"}, field_name=field_name)
            return AddressConstraint.any()
        if kind != "Ranges":
            raise LocalEvidenceImportError(
                f"{field_name}.kind must be Any or Ranges"
            )
        self._reject_unknown(
            value,
            {"kind", "ranges"},
            field_name=field_name,
        )
        ranges = value.get("ranges")
        if not isinstance(ranges, list):
            raise LocalEvidenceImportError(
                f"{field_name}.ranges must be a JSON array"
            )
        return AddressConstraint.ranged(
            *(
                self._address_range(
                    item,
                    field_name=f"{field_name}.ranges[{index}]",
                )
                for index, item in enumerate(ranges)
            )
        )

    def _address_range(self, raw, *, field_name: str) -> AddressRange:
        value = self._require_object(raw, field_name=field_name)
        self._reject_unknown(
            value,
            {"first", "last"},
            field_name=field_name,
        )
        return AddressRange(
            self._require_string(
                value.get("first"),
                field_name=f"{field_name}.first",
            ),
            self._require_string(
                value.get("last"),
                field_name=f"{field_name}.last",
            ),
        )

    def _ports(self, raw, *, field_name: str) -> PortConstraint:
        value = self._require_object(raw, field_name=field_name)
        kind = self._require_string(
            value.get("kind"),
            field_name=f"{field_name}.kind",
        )
        if kind == "Any":
            self._reject_unknown(value, {"kind"}, field_name=field_name)
            return PortConstraint.any()
        if kind == "NotApplicable":
            self._reject_unknown(value, {"kind"}, field_name=field_name)
            return PortConstraint.not_applicable()
        if kind != "Ranges":
            raise LocalEvidenceImportError(
                f"{field_name}.kind must be Any, NotApplicable or Ranges"
            )
        self._reject_unknown(
            value,
            {"kind", "ranges"},
            field_name=field_name,
        )
        ranges = value.get("ranges")
        if not isinstance(ranges, list):
            raise LocalEvidenceImportError(
                f"{field_name}.ranges must be a JSON array"
            )
        return PortConstraint.ranged(
            *(
                self._port_range(
                    item,
                    field_name=f"{field_name}.ranges[{index}]",
                )
                for index, item in enumerate(ranges)
            )
        )

    def _port_range(self, raw, *, field_name: str) -> PortRange:
        value = self._require_object(raw, field_name=field_name)
        self._reject_unknown(
            value,
            {"first", "last"},
            field_name=field_name,
        )
        return PortRange(
            value.get("first"),
            value.get("last"),
        )

    def _protocol(self, raw, *, field_name: str) -> ProtocolSelector:
        if isinstance(raw, str):
            normalized = raw.strip().lower()
            aliases = {
                "any": None,
                "tcp": 6,
                "udp": 17,
            }
            if normalized not in aliases:
                raise LocalEvidenceImportError(
                    f"{field_name} must be any, tcp, udp or an IP protocol number"
                )
            number = aliases[normalized]
            return (
                ProtocolSelector.any()
                if number is None
                else ProtocolSelector.ip_protocol(number)
            )
        if isinstance(raw, int) and not isinstance(raw, bool):
            return ProtocolSelector.ip_protocol(raw)
        raise LocalEvidenceImportError(
            f"{field_name} must be any, tcp, udp or an IP protocol number"
        )

    @staticmethod
    def _datetime(raw, *, field_name: str) -> datetime:
        value = LocalEvidenceImportAdapter._require_string(
            raw,
            field_name=field_name,
        )
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise LocalEvidenceImportError(
                f"{field_name} must be ISO-8601 datetime"
            ) from exc

    @staticmethod
    def _object_from_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise LocalEvidenceImportError(
                    f"duplicate JSON field: {key}"
                )
            value[key] = item
        return value

    @staticmethod
    def _require_object(raw, *, field_name: str) -> dict:
        if not isinstance(raw, dict):
            raise LocalEvidenceImportError(
                f"{field_name} must be a JSON object"
            )
        return raw

    @staticmethod
    def _require_string(raw, *, field_name: str) -> str:
        if not isinstance(raw, str) or not raw.strip():
            raise LocalEvidenceImportError(
                f"{field_name} must be a non-empty string"
            )
        return raw.strip()

    @staticmethod
    def _reject_unknown(
        value: dict,
        allowed: set[str],
        *,
        field_name: str,
    ) -> None:
        unknown = set(value) - allowed
        if unknown:
            raise LocalEvidenceImportError(
                f"{field_name} contains unsupported fields: "
                + ", ".join(sorted(unknown))
            )
