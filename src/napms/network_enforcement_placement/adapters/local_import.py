import json
from datetime import datetime
from uuid import UUID

from napms.network_enforcement_placement.application.capture import (
    KnowledgeSourceReference,
    PlacementKnowledgeCapture,
    SourceCaptureReference,
)
from napms.network_enforcement_placement.domain.model import (
    EffectiveWindow,
    EnforcementAttachment,
    ForwardingPath,
    KnowledgeGap,
    LogicalFirewall,
    LogicalFirewallCorrespondence,
    NoForwardingPath,
    PathAttachmentReference,
    PlacementInvariantError,
    PlacementKnowledgeSnapshot,
    Provenance,
    ProviderRealizationReference,
    TrafficRelation,
    TraversalPoint,
)


class LocalPlacementKnowledgeImportError(ValueError):
    """Local NEP input cannot be normalized without semantic invention."""


class LocalPlacementKnowledgeImportAdapter:
    """Strict local JSON import -> source-neutral NEP capture."""

    _SOURCE_NAMESPACE = "local-import"

    def normalize(self, raw: str | bytes) -> PlacementKnowledgeCapture:
        try:
            document = json.loads(raw, object_pairs_hook=self._object_from_pairs)
        except LocalPlacementKnowledgeImportError:
            raise
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as exc:
            raise LocalPlacementKnowledgeImportError(
                "invalid JSON import payload"
            ) from exc

        try:
            root = self._object(document, "document")
            self._fields(
                root,
                {
                    "source_reference",
                    "source_capture_reference",
                    "validity",
                    "relation",
                    "path",
                    "no_forwarding_path",
                    "logical_firewalls",
                    "correspondences",
                    "attachments",
                    "complete_for_pair",
                    "complete_for_attachments",
                    "knowledge_gaps",
                },
                "document",
            )
            validity = self._window(root.get("validity"), "validity")
            return PlacementKnowledgeCapture(
                source=KnowledgeSourceReference(
                    self._SOURCE_NAMESPACE,
                    self._string(root.get("source_reference"), "source_reference"),
                ),
                source_capture_reference=SourceCaptureReference(
                    self._string(
                        root.get("source_capture_reference"),
                        "source_capture_reference",
                    )
                ),
                relation=self._relation(root.get("relation")),
                validity=validity,
                knowledge=PlacementKnowledgeSnapshot(
                    path=self._path(root.get("path"), validity),
                    no_forwarding_path=self._no_path(
                        root.get("no_forwarding_path"), validity
                    ),
                    logical_firewalls=tuple(
                        self._firewall(value, index)
                        for index, value in enumerate(
                            self._array(root.get("logical_firewalls"), "logical_firewalls")
                        )
                    ),
                    correspondences=tuple(
                        self._correspondence(value, index)
                        for index, value in enumerate(
                            self._array(root.get("correspondences"), "correspondences")
                        )
                    ),
                    attachments=tuple(
                        self._attachment(value, index)
                        for index, value in enumerate(
                            self._array(root.get("attachments"), "attachments")
                        )
                    ),
                    complete_for_pair=self._boolean(
                        root.get("complete_for_pair"), "complete_for_pair"
                    ),
                    complete_for_attachments=self._boolean(
                        root.get("complete_for_attachments"),
                        "complete_for_attachments",
                    ),
                    knowledge_gaps=tuple(
                        self._knowledge_gap(value, index)
                        for index, value in enumerate(
                            self._array(
                                root.get("knowledge_gaps", []),
                                "knowledge_gaps",
                            )
                        )
                    ),
                ),
            )
        except PlacementInvariantError as exc:
            raise LocalPlacementKnowledgeImportError(str(exc)) from exc

    def _knowledge_gap(self, raw, index: int) -> KnowledgeGap:
        name = f"knowledge_gaps[{index}]"
        value = self._object(raw, name)
        self._fields(
            value,
            {"owner", "reason", "references"},
            name,
        )
        return KnowledgeGap(
            self._string(value.get("owner"), f"{name}.owner"),
            self._string(value.get("reason"), f"{name}.reason"),
            tuple(
                self._string(item, f"{name}.references[{ref_index}]")
                for ref_index, item in enumerate(
                    self._array(value.get("references", []), f"{name}.references")
                )
            ),
        )

    def _relation(self, raw) -> TrafficRelation:
        value = self._object(raw, "relation")
        self._fields(value, {"source_ip", "destination_ip"}, "relation")
        return TrafficRelation(
            self._string(value.get("source_ip"), "relation.source_ip"),
            self._string(value.get("destination_ip"), "relation.destination_ip"),
        )

    def _path(
        self, raw, validity: EffectiveWindow
    ) -> ForwardingPath | None:
        if raw is None:
            return None
        value = self._object(raw, "path")
        self._fields(
            value, {"path_reference", "traversal_points", "provenance"}, "path"
        )
        return ForwardingPath(
            self._string(value.get("path_reference"), "path.path_reference"),
            tuple(
                self._traversal(point, index)
                for index, point in enumerate(
                    self._array(value.get("traversal_points"), "path.traversal_points")
                )
            ),
            validity,
            self._provenance(value.get("provenance"), "path.provenance"),
        )

    def _no_path(
        self, raw, validity: EffectiveWindow
    ) -> NoForwardingPath | None:
        if raw is None:
            return None
        value = self._object(raw, "no_forwarding_path")
        self._fields(value, {"provenance"}, "no_forwarding_path")
        return NoForwardingPath(
            validity,
            self._provenance(
                value.get("provenance"), "no_forwarding_path.provenance"
            ),
        )

    def _traversal(self, raw, index: int) -> TraversalPoint:
        name = f"path.traversal_points[{index}]"
        value = self._object(raw, name)
        self._fields(
            value,
            {"provider_realization", "path_attachment", "provenance"},
            name,
        )
        return TraversalPoint(
            self._provider(value.get("provider_realization"), f"{name}.provider_realization"),
            self._path_ref(value.get("path_attachment"), f"{name}.path_attachment"),
            self._provenance(value.get("provenance"), f"{name}.provenance"),
        )

    def _firewall(self, raw, index: int) -> LogicalFirewall:
        name = f"logical_firewalls[{index}]"
        value = self._object(raw, name)
        self._fields(
            value, {"logical_firewall_id", "validity", "provenance"}, name
        )
        return LogicalFirewall(
            self._uuid(value.get("logical_firewall_id"), f"{name}.logical_firewall_id"),
            self._window(value.get("validity"), f"{name}.validity"),
            self._provenance(value.get("provenance"), f"{name}.provenance"),
        )

    def _correspondence(
        self, raw, index: int
    ) -> LogicalFirewallCorrespondence:
        name = f"correspondences[{index}]"
        value = self._object(raw, name)
        self._fields(
            value,
            {
                "logical_firewall_id",
                "provider_realization",
                "validity",
                "provenance",
            },
            name,
        )
        return LogicalFirewallCorrespondence(
            self._uuid(value.get("logical_firewall_id"), f"{name}.logical_firewall_id"),
            self._provider(value.get("provider_realization"), f"{name}.provider_realization"),
            self._window(value.get("validity"), f"{name}.validity"),
            self._provenance(value.get("provenance"), f"{name}.provenance"),
        )

    def _attachment(self, raw, index: int) -> EnforcementAttachment:
        name = f"attachments[{index}]"
        value = self._object(raw, name)
        self._fields(
            value,
            {
                "enforcement_attachment_id",
                "logical_firewall_id",
                "provider_realization",
                "path_attachment",
                "validity",
                "provenance",
            },
            name,
        )
        return EnforcementAttachment(
            self._uuid(
                value.get("enforcement_attachment_id"),
                f"{name}.enforcement_attachment_id",
            ),
            self._uuid(value.get("logical_firewall_id"), f"{name}.logical_firewall_id"),
            self._provider(value.get("provider_realization"), f"{name}.provider_realization"),
            self._path_ref(value.get("path_attachment"), f"{name}.path_attachment"),
            self._window(value.get("validity"), f"{name}.validity"),
            self._provenance(value.get("provenance"), f"{name}.provenance"),
        )

    def _provider(self, raw, name: str) -> ProviderRealizationReference:
        namespace, reference = self._reference(raw, name)
        return ProviderRealizationReference(namespace, reference)

    def _path_ref(self, raw, name: str) -> PathAttachmentReference:
        namespace, reference = self._reference(raw, name)
        return PathAttachmentReference(namespace, reference)

    def _reference(self, raw, name: str) -> tuple[str, str]:
        value = self._object(raw, name)
        self._fields(value, {"namespace", "reference"}, name)
        return (
            self._string(value.get("namespace"), f"{name}.namespace"),
            self._string(value.get("reference"), f"{name}.reference"),
        )

    def _window(self, raw, name: str) -> EffectiveWindow:
        value = self._object(raw, name)
        self._fields(value, {"valid_from", "valid_until"}, name)
        raw_until = value.get("valid_until")
        return EffectiveWindow(
            self._datetime(value.get("valid_from"), f"{name}.valid_from"),
            None
            if raw_until is None
            else self._datetime(raw_until, f"{name}.valid_until"),
        )

    def _provenance(self, raw, name: str) -> Provenance:
        return Provenance(
            tuple(
                self._string(item, f"{name}[{index}]")
                for index, item in enumerate(self._array(raw, name))
            )
        )

    @staticmethod
    def _uuid(raw, name: str) -> UUID:
        value = LocalPlacementKnowledgeImportAdapter._string(raw, name)
        try:
            return UUID(value)
        except ValueError as exc:
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be UUID"
            ) from exc

    @staticmethod
    def _datetime(raw, name: str) -> datetime:
        value = LocalPlacementKnowledgeImportAdapter._string(raw, name)
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be ISO-8601 datetime"
            ) from exc

    @staticmethod
    def _object_from_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise LocalPlacementKnowledgeImportError(
                    f"duplicate JSON field: {key}"
                )
            value[key] = item
        return value

    @staticmethod
    def _object(raw, name: str) -> dict:
        if not isinstance(raw, dict):
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be a JSON object"
            )
        return raw

    @staticmethod
    def _array(raw, name: str) -> list:
        if not isinstance(raw, list):
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be a JSON array"
            )
        return raw

    @staticmethod
    def _string(raw, name: str) -> str:
        if not isinstance(raw, str) or not raw.strip():
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be a non-empty string"
            )
        return raw.strip()

    @staticmethod
    def _boolean(raw, name: str) -> bool:
        if not isinstance(raw, bool):
            raise LocalPlacementKnowledgeImportError(
                f"{name} must be a boolean"
            )
        return raw

    @staticmethod
    def _fields(value: dict, allowed: set[str], name: str) -> None:
        unknown = set(value) - allowed
        if unknown:
            raise LocalPlacementKnowledgeImportError(
                f"{name} contains unsupported fields: "
                + ", ".join(sorted(unknown))
            )
