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


class LocalPlacementKnowledgeImportError(
    ValueError
):
    """Local NEP input cannot be normalized without semantic invention."""


class LocalPlacementKnowledgeImportAdapter:
    """Strict local JSON import -> NEP-owned placement capture."""

    _SOURCE_NAMESPACE = "local-import"

    def normalize(
        self,
        raw: str | bytes,
    ) -> PlacementKnowledgeCapture:
        try:
            document = json.loads(
                raw,
                object_pairs_hook=(
                    self._object_from_pairs
                ),
            )
        except (
            json.JSONDecodeError,
            UnicodeDecodeError,
            TypeError,
        ) as exc:
            raise (
                LocalPlacementKnowledgeImportError(
                    "invalid JSON import payload"
                )
            ) from exc

        try:
            root = self._require_object(
                document,
                field_name="document",
            )
            self._reject_unknown(
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
                },
                field_name="document",
            )

            validity = self._validity(
                root.get("validity"),
                field_name="validity",
            )
            path = self._path(
                root.get("path"),
                validity=validity,
            )
            no_path = self._no_path(
                root.get(
                    "no_forwarding_path"
                ),
                validity=validity,
            )

            return PlacementKnowledgeCapture(
                source=KnowledgeSourceReference(
                    self._SOURCE_NAMESPACE,
                    self._require_string(
                        root.get(
                            "source_reference"
                        ),
                        field_name=(
                            "source_reference"
                        ),
                    ),
                ),
                source_capture_reference=(
                    SourceCaptureReference(
                        self._require_string(
                            root.get(
                                "source_capture_reference"
                            ),
                            field_name=(
                                "source_capture_reference"
                            ),
                        )
                    )
                ),
                relation=self._relation(
                    root.get("relation")
                ),
                validity=validity,
                knowledge=(
                    PlacementKnowledgeSnapshot(
                        path=path,
                        no_forwarding_path=(
                            no_path
                        ),
                        logical_firewalls=tuple(
                            self._firewall(
                                item,
                                index=index,
                            )
                            for index, item
                            in enumerate(
                                self._array(
                                    root.get(
                                        "logical_firewalls"
                                    ),
                                    field_name=(
                                        "logical_firewalls"
                                    ),
                                )
                            )
                        ),
                        correspondences=tuple(
                            self._correspondence(
                                item,
                                index=index,
                            )
                            for index, item
                            in enumerate(
                                self._array(
                                    root.get(
                                        "correspondences"
                                    ),
                                    field_name=(
                                        "correspondences"
                                    ),
                                )
                            )
                        ),
                        attachments=tuple(
                            self._attachment(
                                item,
                                index=index,
                            )
                            for index, item
                            in enumerate(
                                self._array(
                                    root.get(
                                        "attachments"
                                    ),
                                    field_name=(
                                        "attachments"
                                    ),
                                )
                            )
                        ),
                        complete_for_pair=(
                            self._boolean(
                                root.get(
                                    "complete_for_pair"
                                ),
                                field_name=(
                                    "complete_for_pair"
                                ),
                            )
                        ),
                        complete_for_attachments=(
                            self._boolean(
                                root.get(
                                    "complete_for_attachments"
                                ),
                                field_name=(
                                    "complete_for_attachments"
                                ),
                            )
                        ),
                    )
                ),
            )
        except PlacementInvariantError as exc:
            raise (
                LocalPlacementKnowledgeImportError(
                    str(exc)
                )
            ) from exc

    def _relation(
        self,
        raw,
    ) -> TrafficRelation:
        value = self._require_object(
            raw,
            field_name="relation",
        )
        self._reject_unknown(
            value,
            {
                "source_ip",
                "destination_ip",
            },
            field_name="relation",
        )
        return TrafficRelation(
            self._require_string(
                value.get("source_ip"),
                field_name=(
                    "relation.source_ip"
                ),
            ),
            self._require_string(
                value.get("destination_ip"),
                field_name=(
                    "relation.destination_ip"
                ),
            ),
        )

    def _path(
        self,
        raw,
        *,
        validity: EffectiveWindow,
    ) -> ForwardingPath | None:
        if raw is None:
            return None
        value = self._require_object(
            raw,
            field_name="path",
        )
        self._reject_unknown(
            value,
            {
                "path_reference",
                "traversal_points",
                "provenance",
            },
            field_name="path",
        )
        points = self._array(
            value.get("traversal_points"),
            field_name=(
                "path.traversal_points"
            ),
        )
        return ForwardingPath(
            self._require_string(
                value.get("path_reference"),
                field_name=(
                    "path.path_reference"
                ),
            ),
            tuple(
                self._traversal(
                    item,
                    index=index,
                )
                for index, item
                in enumerate(points)
            ),
            validity,
            self._provenance(
                value.get("provenance"),
                field_name=(
                    "path.provenance"
                ),
            ),
        )

    def _no_path(
        self,
        raw,
        *,
        validity: EffectiveWindow,
    ) -> NoForwardingPath | None:
        if raw is None:
            return None
        value = self._require_object(
            raw,
            field_name=(
                "no_forwarding_path"
            ),
        )
        self._reject_unknown(
            value,
            {"provenance"},
            field_name=(
                "no_forwarding_path"
            ),
        )
        return NoForwardingPath(
            validity,
            self._provenance(
                value.get("provenance"),
                field_name=(
                    "no_forwarding_path.provenance"
                ),
            ),
        )

    def _traversal(
        self,
        raw,
        *,
        index: int,
    ) -> TraversalPoint:
        name = (
            f"path.traversal_points[{index}]"
        )
        value = self._require_object(
            raw,
            field_name=name,
        )
        self._reject_unknown(
            value,
            {
                "provider_realization",
                "path_attachment",
                "provenance",
            },
            field_name=name,
        )
        return TraversalPoint(
            self._provider(
                value.get(
                    "provider_realization"
                ),
                field_name=(
                    f"{name}.provider_realization"
                ),
            ),
            self._path_attachment(
                value.get(
                    "path_attachment"
                ),
                field_name=(
                    f"{name}.path_attachment"
                ),
            ),
            self._provenance(
                value.get("provenance"),
                field_name=(
                    f"{name}.provenance"
                ),
            ),
        )

    def _firewall(
        self,
        raw,
        *,
        index: int,
    ) -> LogicalFirewall:
        name = (
            f"logical_firewalls[{index}]"
        )
        value = self._require_object(
            raw,
            field_name=name,
        )
        self._reject_unknown(
            value,
            {
                "logical_firewall_id",
                "validity",
                "provenance",
            },
            field_name=name,
        )
        return LogicalFirewall(
            self._uuid(
                value.get(
                    "logical_firewall_id"
                ),
                field_name=(
                    f"{name}.logical_firewall_id"
                ),
            ),
            self._validity(
                value.get("validity"),
                field_name=(
                    f"{name}.validity"
                ),
            ),
            self._provenance(
                value.get("provenance"),
                field_name=(
                    f"{name}.provenance"
                ),
            ),
        )

    def _correspondence(
        self,
        raw,
        *,
        index: int,
    ) -> LogicalFirewallCorrespondence:
        name = (
            f"correspondences[{index}]"
        )
        value = self._require_object(
            raw,
            field_name=name,
        )
        self._reject_unknown(
            value,
            {
                "logical_firewall_id",
                "provider_realization",
                "validity",
                "provenance",
            },
            field_name=name,
        )
        return (
            LogicalFirewallCorrespondence(
                self._uuid(
                    value.get(
                        "logical_firewall_id"
                    ),
                    field_name=(
                        f"{name}.logical_firewall_id"
                    ),
                ),
                self._provider(
                    value.get(
                        "provider_realization"
                    ),
                    field_name=(
                        f"{name}.provider_realization"
                    ),
                ),
                self._validity(
                    value.get("validity"),
                    field_name=(
                        f"{name}.validity"
                    ),
                ),
                self._provenance(
                    value.get(
                        "provenance"
                    ),
                    field_name=(
                        f"{name}.provenance"
                    ),
                ),
            )
        )

    def _attachment(
        self,
        raw,
        *,
        index: int,
    ) -> EnforcementAttachment:
        name = f"attachments[{index}]"
        value = self._require_object(
            raw,
            field_name=name,
        )
        self._reject_unknown(
            value,
            {
                "enforcement_attachment_id",
                "logical_firewall_id",
                "provider_realization",
                "path_attachment",
                "validity",
                "provenance",
            },
            field_name=name,
        )
        return EnforcementAttachment(
            self._uuid(
                value.get(
                    "enforcement_attachment_id"
                ),
                field_name=(
                    f"{name}.enforcement_attachment_id"
                ),
            ),
            self._uuid(
                value.get(
                    "logical_firewall_id"
                ),
                field_name=(
                    f"{name}.logical_firewall_id"
                ),
            ),
            self._provider(
                value.get(
                    "provider_realization"
                ),
                field_name=(
                    f"{name}.provider_realization"
                ),
            ),
            self._path_attachment(
                value.get(
                    "path_attachment"
                ),
                field_name=(
                    f"{name}.path_attachment"
                ),
            ),
            self._validity(
                value.get("validity"),
                field_name=(
                    f"{name}.validity"
                ),
            ),
            self._provenance(
                value.get("provenance"),
                field_name=(
                    f"{name}.provenance"
                ),
            ),
        )

    def _provider(
        self,
        raw,
        *,
        field_name: str,
    ) -> ProviderRealizationReference:
        value = self._reference(
            raw,
            field_name=field_name,
        )
        return ProviderRealizationReference(
            value["namespace"],
            value["reference"],
        )

    def _path_attachment(
        self,
        raw,
        *,
        field_name: str,
    ) -> PathAttachmentReference:
        value = self._reference(
            raw,
            field_name=field_name,
        )
        return PathAttachmentReference(
            value["namespace"],
            value["reference"],
        )

    def _reference(
        self,
        raw,
        *,
        field_name: str,
    ) -> dict:
        value = self._require_object(
            raw,
            field_name=field_name,
        )
        self._reject_unknown(
            value,
            {
                "namespace",
                "reference",
            },
            field_name=field_name,
        )
        return {
            "namespace": (
                self._require_string(
                    value.get("namespace"),
                    field_name=(
                        f"{field_name}.namespace"
                    ),
                )
            ),
            "reference": (
                self._require_string(
                    value.get("reference"),
                    field_name=(
                        f"{field_name}.reference"
                    ),
                )
            ),
        }

    def _validity(
        self,
        raw,
        *,
        field_name: str,
    ) -> EffectiveWindow:
        value = self._require_object(
            raw,
            field_name=field_name,
        )
        self._reject_unknown(
            value,
            {
                "valid_from",
                "valid_until",
            },
            field_name=field_name,
        )
        end = value.get("valid_until")
        return EffectiveWindow(
            self._datetime(
                value.get("valid_from"),
                field_name=(
                    f"{field_name}.valid_from"
                ),
            ),
            (
                None
                if end is None
                else self._datetime(
                    end,
                    field_name=(
                        f"{field_name}.valid_until"
                    ),
                )
            ),
        )

    def _provenance(
        self,
        raw,
        *,
        field_name: str,
    ) -> Provenance:
        values = self._array(
            raw,
            field_name=field_name,
        )
        return Provenance(
            tuple(
                self._require_string(
                    item,
                    field_name=(
                        f"{field_name}[{index}]"
                    ),
                )
                for index, item
                in enumerate(values)
            )
        )

    @staticmethod
    def _uuid(
        raw,
        *,
        field_name: str,
    ) -> UUID:
        value = (
            LocalPlacementKnowledgeImportAdapter
            ._require_string(
                raw,
                field_name=field_name,
            )
        )
        try:
            return UUID(value)
        except ValueError as exc:
            raise (
                LocalPlacementKnowledgeImportError(
                    f"{field_name} must be UUID"
                )
            ) from exc

    @staticmethod
    def _datetime(
        raw,
        *,
        field_name: str,
    ) -> datetime:
        value = (
            LocalPlacementKnowledgeImportAdapter
            ._require_string(
                raw,
                field_name=field_name,
            )
        )
        if value.endswith("Z"):
            value = (
                value[:-1] + "+00:00"
            )
        try:
            return datetime.fromisoformat(
                value
            )
        except ValueError as exc:
            raise (
                LocalPlacementKnowledgeImportError(
                    f"{field_name} must be ISO-8601 datetime"
                )
            ) from exc

    @staticmethod
    def _object_from_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise (
                    LocalPlacementKnowledgeImportError(
                        f"duplicate JSON field: {key}"
                    )
                )
            value[key] = item
        return value

    @staticmethod
    def _require_object(
        raw,
        *,
        field_name: str,
    ) -> dict:
        if not isinstance(raw, dict):
            raise LocalPlacementKnowledgeImportError(
                f"{field_name} must be a JSON object"
            )
        return raw

    @staticmethod
    def _require_string(
        raw,
        *,
        field_name: str,
    ) -> str:
        if (
            not isinstance(raw, str)
            or not raw.strip()
        ):
            raise LocalPlacementKnowledgeImportError(
                f"{field_name} must be a non-empty string"
            )
        return raw.strip()

    @staticmethod
    def _array(
        raw,
        *,
        field_name: str,
    ) -> list:
        if not isinstance(raw, list):
            raise LocalPlacementKnowledgeImportError(
                f"{field_name} must be a JSON array"
            )
        return raw

    @staticmethod
    def _boolean(
        raw,
        *,
        field_name: str,
    ) -> bool:
        if not isinstance(raw, bool):
            raise LocalPlacementKnowledgeImportError(
                f"{field_name} must be a boolean"
            )
        return raw

    @staticmethod
    def _reject_unknown(
        value: dict,
        allowed: set[str],
        *,
        field_name: str,
    ) -> None:
        unknown = set(value) - allowed
        if unknown:
            raise LocalPlacementKnowledgeImportError(
                f"{field_name} contains unsupported fields: "
                + ", ".join(
                    sorted(unknown)
                )
            )
