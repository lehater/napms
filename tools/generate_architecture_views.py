#!/usr/bin/env python3
from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "docs-generated" / "architecture"

STRATEGIC_DIR = ROOT / "docs" / "migration" / "revalidated" / "h16-strategic" / "s2" / "strategic"
CAPABILITY_MAP = STRATEGIC_DIR / "capability-map.yaml"
CONTEXT_RELATIONSHIPS = STRATEGIC_DIR / "context-relationships.yaml"

RC_BASE = ROOT / "docs" / "migration" / "revalidated" / "h12-rc-curation" / "s2"
RC_PROCESS = RC_BASE / "process" / "resource-curation-process.yaml"
RC_DOMAIN_MODEL = RC_BASE / "tactical" / "resource-catalogue-domain-model.yaml"

MVP_JOURNEY_BASE = ROOT / "docs" / "migration" / "revalidated" / "h17-mvp-journey"
MVP_REQUIREMENT = MVP_JOURNEY_BASE / "s1" / "mvp-vendor-neutral-policy-export.yaml"
MVP_TACTICAL_MODEL = MVP_JOURNEY_BASE / "s2" / "tactical" / "mvp-journey-domain-model.yaml"

MVP_READINESS = (
    ROOT
    / "docs"
    / "migration"
    / "revalidated"
    / "h19-mvp-implementation-readiness"
    / "s4"
    / "mvp-implementation-readiness.yaml"
)

CONTEXT_MAP_OUTPUT = GENERATED_DIR / "context-map.puml"
COLLABORATION_MAP_OUTPUT = GENERATED_DIR / "strategic-collaboration-map.puml"
MVP_JOURNEY_OUTPUT = GENERATED_DIR / "mvp-journey.puml"
RC_PROCESS_OUTPUT = GENERATED_DIR / "resource-curation-process.puml"
RC_DOMAIN_OUTPUT = GENERATED_DIR / "resource-catalogue-domain-model.puml"
MVP_TACTICAL_OUTPUT = GENERATED_DIR / "mvp-tactical-domain-model.puml"
PERSISTENCE_OWNERSHIP_OUTPUT = GENERATED_DIR / "persistence-ownership.puml"


def load_accepted_document(path: Path, expected_type: str) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    if data.get("status") != "ACCEPTED":
        raise ValueError(f"{path}: projection source must have status ACCEPTED")
    if data.get("type_id") != expected_type:
        raise ValueError(
            f"{path}: expected type_id {expected_type!r}, got {data.get('type_id')!r}"
        )
    payload = data.get("canonical_payload")
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: canonical_payload must be a mapping")
    return data


def load_accepted_payload(path: Path, expected_type: str) -> dict[str, Any]:
    return load_accepted_document(path, expected_type)["canonical_payload"]


def plantuml_alias(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    if not slug:
        raise ValueError(f"cannot create PlantUML alias from {name!r}")
    return f"node_{slug}"


def plantuml_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def wrapped_lines(value: str, width: int = 78) -> list[str]:
    return textwrap.wrap(
        value,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]


def wrapped_label(value: str, width: int = 42) -> str:
    return "\\n".join(plantuml_text(line) for line in wrapped_lines(value, width=width))


def ensure_string_list(value: Any, *, path: Path, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{path}: {field} must be a list of strings")
    return value


def projection_header(sources: list[Path], authority: str) -> list[str]:
    lines = [
        "' GENERATED FILE - DO NOT EDIT",
        f"' Projection only; semantic authority remains in {authority}.",
    ]
    lines.extend(f"' Source: {source.relative_to(ROOT).as_posix()}" for source in sources)
    return lines


def diagram_prelude(
    title: str, *, direction: str | None = "left to right direction"
) -> list[str]:
    lines = ["@startuml", f"title {title}"]
    if direction:
        lines.append(direction)
    lines.extend(
        [
            "skinparam shadowing false",
            "skinparam roundcorner 12",
            "skinparam ArrowColor #5b6573",
            "skinparam ArrowFontColor #3f4752",
            "skinparam ArrowFontSize 9",
            "skinparam legendBackgroundColor #FFFFFF",
            "skinparam legendBorderColor #FFFFFF",
            "skinparam legendFontColor #27313d",
            "skinparam legendFontSize 10",
            "skinparam rectangle {",
            "  BorderColor #2f5597",
            "  FontColor #1f2937",
            "}",
            "",
        ]
    )
    return lines


def append_text_legend(
    lines: list[str], title: str, entries: list[tuple[str, str]]
) -> None:
    lines.extend(["", "legend bottom", f"  <b>{plantuml_text(title)}</b>"])
    for key, value in entries:
        lines.append(f"  <b>{plantuml_text(key)}</b>")
        for semantic_line in wrapped_lines(value):
            lines.append(f"      {plantuml_text(semantic_line)}")
    lines.append("endlegend")


def load_strategic_model() -> tuple[list[str], list[str], list[dict[str, str]]]:
    capability_payload = load_accepted_payload(CAPABILITY_MAP, "capability-map")
    relationship_payload = load_accepted_payload(
        CONTEXT_RELATIONSHIPS, "context-relationship-map"
    )

    capabilities = capability_payload.get("capabilities", [])
    peer_cluster = next(
        (
            cluster
            for cluster in capability_payload.get("clustering", [])
            if cluster.get("cluster_id") == "CLUSTER-PEER-BOUNDED-CONTEXTS"
        ),
        None,
    )
    if peer_cluster is None:
        raise ValueError(f"{CAPABILITY_MAP}: missing CLUSTER-PEER-BOUNDED-CONTEXTS")

    capability_by_id = {item["capability_id"]: item for item in capabilities}
    peer_names: list[str] = []
    for capability_id in peer_cluster.get("capability_ids", []):
        if capability_id not in capability_by_id:
            raise ValueError(
                f"{CAPABILITY_MAP}: cluster references unknown capability {capability_id}"
            )
        peer_names.append(capability_by_id[capability_id]["name"])

    composition_names = [
        item["id"] for item in capability_payload.get("non_peer_compositions", [])
    ]
    known_nodes = set(peer_names) | set(composition_names)
    relationships = relationship_payload.get("relationships", [])

    normalized_relationships: list[dict[str, str]] = []
    for index, relationship in enumerate(relationships, start=1):
        source = relationship.get("from")
        target = relationship.get("to")
        semantics = relationship.get("semantics")
        if not isinstance(source, str) or not isinstance(target, str) or not isinstance(
            semantics, str
        ):
            raise ValueError(
                f"{CONTEXT_RELATIONSHIPS}: every relationship requires string from/to/semantics"
            )
        for endpoint_name, endpoint_value in (("from", source), ("to", target)):
            if endpoint_value not in known_nodes:
                raise ValueError(
                    f"{CONTEXT_RELATIONSHIPS}: relationship {endpoint_name} endpoint "
                    f"{endpoint_value!r} is not declared by the accepted capability map"
                )
        normalized_relationships.append(
            {
                "id": f"R{index:02d}",
                "from": source,
                "to": target,
                "semantics": semantics,
            }
        )

    return peer_names, composition_names, normalized_relationships


def append_relationship_legend(
    lines: list[str],
    relationships: list[dict[str, str]],
    *,
    include_composition_notation: bool,
) -> None:
    notation = "Blue = peer Bounded Context"
    if include_composition_notation:
        notation += "; grey = non-peer composition"
    lines.extend(
        [
            "",
            "legend bottom",
            f"  <b>Notation:</b> {notation}",
            "  Arrow numbers identify accepted collaboration relationships; no DDD Context Mapping pattern is inferred.",
            "",
            "  <b>Relationships</b>",
        ]
    )
    for relationship in relationships:
        lines.append(
            f"  <b>{relationship['id']}</b>  {plantuml_text(relationship['from'])} -> "
            f"{plantuml_text(relationship['to'])}"
        )
        for semantic_line in wrapped_lines(relationship["semantics"]):
            lines.append(f"      {plantuml_text(semantic_line)}")
    lines.append("endlegend")


def append_relationships(
    lines: list[str], relationships: list[dict[str, str]]
) -> None:
    lines.append("")
    for relationship in relationships:
        lines.append(
            f"{plantuml_alias(relationship['from'])} --> "
            f"{plantuml_alias(relationship['to'])} : {relationship['id']}"
        )


def render_context_map(
    peer_names: list[str], relationships: list[dict[str, str]]
) -> str:
    peer_set = set(peer_names)
    peer_relationships = [
        relationship
        for relationship in relationships
        if relationship["from"] in peer_set and relationship["to"] in peer_set
    ]

    lines = projection_header(
        [CAPABILITY_MAP, CONTEXT_RELATIONSHIPS],
        "the accepted S2 strategic anchors below",
    ) + diagram_prelude("NAPMS DDD Context Map")
    for name in peer_names:
        lines.append(
            f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #dbeafe'
        )

    append_relationships(lines, peer_relationships)
    append_relationship_legend(
        lines, peer_relationships, include_composition_notation=False
    )
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_collaboration_map(
    peer_names: list[str],
    composition_names: list[str],
    relationships: list[dict[str, str]],
) -> str:
    lines = projection_header(
        [CAPABILITY_MAP, CONTEXT_RELATIONSHIPS],
        "the accepted S2 strategic anchors below",
    ) + diagram_prelude("NAPMS Strategic Collaboration Map")
    for name in peer_names:
        lines.append(
            f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #dbeafe'
        )

    if composition_names:
        lines.append("")
        for name in composition_names:
            lines.append(
                f'rectangle "{plantuml_text(name)}" as {plantuml_alias(name)} #f3f4f6'
            )

    append_relationships(lines, relationships)
    append_relationship_legend(lines, relationships, include_composition_notation=True)
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_mvp_journey() -> str:
    payload = load_accepted_payload(MVP_REQUIREMENT, "product-requirement")
    journey = ensure_string_list(
        payload.get("journey"), path=MVP_REQUIREMENT, field="canonical_payload.journey"
    )
    if not journey:
        raise ValueError(f"{MVP_REQUIREMENT}: journey must not be empty")

    lines = projection_header(
        [MVP_REQUIREMENT], "the accepted S1 product requirement below"
    ) + diagram_prelude("First MVP Journey", direction="top to bottom direction")
    aliases: list[str] = []
    for index, step in enumerate(journey, start=1):
        alias = f"journey_{index:02d}"
        aliases.append(alias)
        label = wrapped_label(f"{index}. {step}", width=54)
        lines.append(f'rectangle "{label}" as {alias} #eef6ff')
    lines.append("")
    for source, target in zip(aliases, aliases[1:]):
        lines.append(f"{source} --> {target}")

    goal = payload.get("goal")
    if isinstance(goal, str):
        append_text_legend(lines, "Goal", [("Accepted S1 goal", goal)])
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_resource_curation_process() -> str:
    payload = load_accepted_payload(RC_PROCESS, "domain-process-model")
    flows = payload.get("process_flows")
    if not isinstance(flows, list) or not flows:
        raise ValueError(
            f"{RC_PROCESS}: canonical_payload.process_flows must be a non-empty list"
        )

    named_sections: dict[str, tuple[str, str]] = {}
    for section, kind in (
        ("policies", "policy"),
        ("commands", "command"),
        ("domain_events", "event"),
    ):
        items = payload.get(section, [])
        if not isinstance(items, list):
            raise ValueError(f"{RC_PROCESS}: canonical_payload.{section} must be a list")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"{RC_PROCESS}: {section} items must be mappings")
            identifier = next(
                (
                    item.get(key)
                    for key in ("policy_id", "command_id", "event_id")
                    if isinstance(item.get(key), str)
                ),
                None,
            )
            name = item.get("name")
            if identifier is None or not isinstance(name, str):
                raise ValueError(f"{RC_PROCESS}: {section} items require id and name")
            named_sections[identifier] = (kind, name)

    colors = {
        "policy": "#fef3c7",
        "command": "#dbeafe",
        "event": "#dcfce7",
        "action": "#f3f4f6",
    }

    lines = projection_header(
        [RC_PROCESS], "the accepted S2 Resource Catalogue process model below"
    ) + diagram_prelude("Resource Catalogue Curation Process")

    for flow_index, flow in enumerate(flows, start=1):
        if not isinstance(flow, dict):
            raise ValueError(f"{RC_PROCESS}: process flow entries must be mappings")
        flow_id = flow.get("flow_id")
        flow_name = flow.get("name")
        if not isinstance(flow_id, str) or not isinstance(flow_name, str):
            raise ValueError(f"{RC_PROCESS}: every process flow requires flow_id and name")

        raw_sequences: list[list[str]]
        if "sequence" in flow:
            raw_sequences = [
                ensure_string_list(
                    flow["sequence"],
                    path=RC_PROCESS,
                    field=f"process_flows[{flow_id}].sequence",
                )
            ]
        elif "alternatives" in flow:
            alternatives = flow["alternatives"]
            if not isinstance(alternatives, list) or not alternatives:
                raise ValueError(f"{RC_PROCESS}: {flow_id}.alternatives must be non-empty")
            raw_sequences = [
                ensure_string_list(
                    alternative,
                    path=RC_PROCESS,
                    field=f"process_flows[{flow_id}].alternatives",
                )
                for alternative in alternatives
            ]
        else:
            raise ValueError(f"{RC_PROCESS}: {flow_id} requires sequence or alternatives")

        lines.append("")
        lines.append(f'package "{plantuml_text(flow_name)}" {{')
        for sequence_index, sequence in enumerate(raw_sequences, start=1):
            aliases: list[str] = []
            for step_index, ref in enumerate(sequence, start=1):
                alias = f"flow_{flow_index:02d}_{sequence_index:02d}_{step_index:02d}"
                aliases.append(alias)
                kind, name = named_sections.get(ref, ("action", ref))
                label = wrapped_label(name, width=34)
                lines.append(f'  rectangle "{label}" as {alias} {colors[kind]}')
            for source, target in zip(aliases, aliases[1:]):
                lines.append(f"  {source} --> {target}")
            if sequence_index != len(raw_sequences):
                lines.append("")
        lines.append("}")

    lines.extend(
        [
            "",
            "legend bottom",
            "  <b>Notation</b>",
            "  Yellow = policy/check",
            "  Blue = command",
            "  Green = domain event",
            "  Grey = explicit process action not modeled as command/event/policy",
            "  Alternatives are rendered as separate chains exactly as declared by the canonical process model.",
            "endlegend",
            "",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def render_resource_catalogue_domain_model() -> str:
    payload = load_accepted_payload(RC_DOMAIN_MODEL, "domain-model")
    aggregates = payload.get("aggregates")
    entities = payload.get("entities")
    value_objects = payload.get("value_objects")
    invariants = payload.get("invariants")
    if not isinstance(aggregates, list) or not aggregates:
        raise ValueError(f"{RC_DOMAIN_MODEL}: aggregates must be a non-empty list")
    if not isinstance(entities, list) or not entities:
        raise ValueError(f"{RC_DOMAIN_MODEL}: entities must be a non-empty list")
    if not isinstance(value_objects, list):
        raise ValueError(f"{RC_DOMAIN_MODEL}: value_objects must be a list")
    if not isinstance(invariants, list):
        raise ValueError(f"{RC_DOMAIN_MODEL}: invariants must be a list")

    entity_by_id = {
        entity["entity_id"]: entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("entity_id"), str)
    }
    vo_by_name = {
        vo["name"]: vo
        for vo in value_objects
        if isinstance(vo, dict) and isinstance(vo.get("name"), str)
    }

    lines = projection_header(
        [RC_DOMAIN_MODEL], "the accepted S2 Resource Catalogue tactical model below"
    ) + diagram_prelude("Resource Catalogue Domain Model")

    rendered_entities: set[str] = set()
    root_by_aggregate: dict[str, str] = {}

    for aggregate in aggregates:
        if not isinstance(aggregate, dict):
            raise ValueError(f"{RC_DOMAIN_MODEL}: aggregate entries must be mappings")
        aggregate_id = aggregate.get("aggregate_id")
        root_ref = aggregate.get("root_entity_ref")
        if not isinstance(aggregate_id, str) or not isinstance(root_ref, str):
            raise ValueError(
                f"{RC_DOMAIN_MODEL}: each aggregate requires aggregate_id and root_entity_ref"
            )
        root = entity_by_id.get(root_ref)
        if root is None:
            raise ValueError(
                f"{RC_DOMAIN_MODEL}: aggregate {aggregate_id} references unknown root entity {root_ref}"
            )
        root_by_aggregate[aggregate_id] = root_ref
        alias = plantuml_alias(root_ref)
        rendered_entities.add(root_ref)
        lines.append(
            f'class "{plantuml_text(root["name"])}\\n<<aggregate root>>" as {alias} #dbeafe'
        )

    for entity in entities:
        if not isinstance(entity, dict):
            raise ValueError(f"{RC_DOMAIN_MODEL}: entity entries must be mappings")
        entity_id = entity.get("entity_id")
        name = entity.get("name")
        if not isinstance(entity_id, str) or not isinstance(name, str):
            raise ValueError(f"{RC_DOMAIN_MODEL}: entities require entity_id and name")
        if entity_id not in rendered_entities:
            lines.append(
                f'class "{plantuml_text(name)}\\n<<entity>>" as {plantuml_alias(entity_id)} #eff6ff'
            )

    lines.append("")
    for vo in value_objects:
        if not isinstance(vo, dict):
            raise ValueError(f"{RC_DOMAIN_MODEL}: value object entries must be mappings")
        vo_id = vo.get("value_object_id")
        name = vo.get("name")
        if not isinstance(vo_id, str) or not isinstance(name, str):
            raise ValueError(
                f"{RC_DOMAIN_MODEL}: value objects require value_object_id and name"
            )
        lines.append(
            f'class "{plantuml_text(name)}\\n<<value object>>" as {plantuml_alias(vo_id)} #f5f3ff'
        )

    lines.append("")
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("entity_id")
        if not isinstance(entity_id, str):
            continue
        owner_aggregate = entity.get("owner_aggregate_ref")
        if isinstance(owner_aggregate, str):
            root_ref = root_by_aggregate.get(owner_aggregate)
            if root_ref is None:
                raise ValueError(
                    f"{RC_DOMAIN_MODEL}: entity {entity_id} references unknown aggregate {owner_aggregate}"
                )
            lines.append(f"{plantuml_alias(root_ref)} *-- {plantuml_alias(entity_id)} : owns")

        identity = entity.get("identity")
        if isinstance(identity, str) and identity in vo_by_name:
            lines.append(
                f"{plantuml_alias(entity_id)} --> "
                f"{plantuml_alias(vo_by_name[identity]['value_object_id'])} : identity"
            )

        attributes = entity.get("attributes", [])
        if attributes is None:
            attributes = []
        if not isinstance(attributes, list):
            raise ValueError(
                f"{RC_DOMAIN_MODEL}: entity {entity_id} attributes must be a list"
            )
        for attribute in attributes:
            if isinstance(attribute, str) and attribute in vo_by_name:
                lines.append(
                    f"{plantuml_alias(entity_id)} --> "
                    f"{plantuml_alias(vo_by_name[attribute]['value_object_id'])} : "
                    f"{plantuml_text(attribute)}"
                )

    invariant_entries: list[tuple[str, str]] = []
    for invariant in invariants:
        if not isinstance(invariant, dict):
            raise ValueError(f"{RC_DOMAIN_MODEL}: invariant entries must be mappings")
        invariant_id = invariant.get("invariant_id")
        rule = invariant.get("rule")
        if not isinstance(invariant_id, str) or not isinstance(rule, str):
            raise ValueError(f"{RC_DOMAIN_MODEL}: invariants require invariant_id and rule")
        invariant_entries.append((invariant_id, rule))
    append_text_legend(lines, "Accepted invariants", invariant_entries)

    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_mvp_tactical_domain_model() -> str:
    payload = load_accepted_payload(MVP_TACTICAL_MODEL, "tactical-domain-model")
    contexts = payload.get("participating_contexts")
    if not isinstance(contexts, dict) or not contexts:
        raise ValueError(
            f"{MVP_TACTICAL_MODEL}: participating_contexts must be a non-empty mapping"
        )

    lines = projection_header(
        [MVP_TACTICAL_MODEL], "the accepted S2 first-MVP tactical model below"
    ) + diagram_prelude("First MVP Tactical Domain Model")

    for context_index, (context_name, details) in enumerate(contexts.items(), start=1):
        if not isinstance(details, dict):
            raise ValueError(
                f"{MVP_TACTICAL_MODEL}: participating context {context_name!r} must be a mapping"
            )
        lines.append("")
        lines.append(f'package "{plantuml_text(context_name)}" {{')
        node_aliases: list[str] = []

        if isinstance(details.get("aggregate"), str):
            aggregate = details["aggregate"]
            alias = f"tactical_{context_index:02d}_aggregate"
            node_aliases.append(alias)
            lines.append(
                f'  class "{plantuml_text(aggregate)}\\n<<aggregate>>" as {alias} #dbeafe'
            )
            entities = details.get("entities", [])
            if entities is None:
                entities = []
            if not isinstance(entities, list):
                raise ValueError(
                    f"{MVP_TACTICAL_MODEL}: {context_name}.entities must be a list"
                )
            for entity_index, entity in enumerate(entities, start=1):
                if not isinstance(entity, str):
                    raise ValueError(
                        f"{MVP_TACTICAL_MODEL}: {context_name}.entities must contain strings"
                    )
                entity_alias = f"tactical_{context_index:02d}_entity_{entity_index:02d}"
                lines.append(
                    f'  class "{plantuml_text(entity)}\\n<<entity>>" as {entity_alias} #eff6ff'
                )
                lines.append(f"  {alias} *-- {entity_alias}")
                node_aliases.append(entity_alias)

        aggregate_semantics = details.get("aggregate_semantics")
        if aggregate_semantics is not None:
            semantics = ensure_string_list(
                aggregate_semantics,
                path=MVP_TACTICAL_MODEL,
                field=f"participating_contexts.{context_name}.aggregate_semantics",
            )
            for semantic_index, semantic in enumerate(semantics, start=1):
                alias = f"tactical_{context_index:02d}_semantic_{semantic_index:02d}"
                node_aliases.append(alias)
                lines.append(
                    f'  class "{plantuml_text(semantic)}\\n<<aggregate semantics>>" '
                    f"as {alias} #dbeafe"
                )

        child_entity = details.get("child_entity")
        if isinstance(child_entity, str):
            parent = next(
                (alias for alias in node_aliases if alias.endswith("_aggregate")), None
            )
            alias = f"tactical_{context_index:02d}_child"
            lines.append(
                f'  class "{plantuml_text(child_entity)}\\n<<child entity>>" as {alias} #eff6ff'
            )
            if parent:
                lines.append(f"  {parent} *-- {alias}")
            node_aliases.append(alias)

        reused_truth = details.get("reused_current_truth")
        if isinstance(reused_truth, str) and not node_aliases:
            alias = f"tactical_{context_index:02d}_reused"
            lines.append(
                f'  rectangle "{wrapped_label(reused_truth, width=44)}" as {alias} #f3f4f6'
            )
            node_aliases.append(alias)

        if not node_aliases:
            raise ValueError(
                f"{MVP_TACTICAL_MODEL}: {context_name} has no renderable aggregate/entity/reused truth"
            )
        lines.append("}")

    cross_context_flow = payload.get("cross_context_flow", [])
    if not isinstance(cross_context_flow, list):
        raise ValueError(f"{MVP_TACTICAL_MODEL}: cross_context_flow must be a list")
    flow_entries: list[tuple[str, str]] = []
    for step in cross_context_flow:
        if not isinstance(step, dict):
            raise ValueError(
                f"{MVP_TACTICAL_MODEL}: cross_context_flow entries must be mappings"
            )
        step_number = step.get("step")
        owner = step.get("owner")
        result = step.get("result")
        if not isinstance(owner, str) or not isinstance(result, str):
            raise ValueError(
                f"{MVP_TACTICAL_MODEL}: cross_context_flow entries require owner/result strings"
            )
        flow_entries.append((f"Step {step_number}: {owner}", result))
    if flow_entries:
        append_text_legend(lines, "Cross-context flow", flow_entries)

    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def render_persistence_ownership() -> str:
    payload = load_accepted_payload(MVP_READINESS, "implementation-plan")
    persistence = payload.get("persistence")
    if not isinstance(persistence, dict):
        raise ValueError(f"{MVP_READINESS}: canonical_payload.persistence must be a mapping")
    database = persistence.get("database")
    schemas = persistence.get("schemas")
    rules = persistence.get("rules", [])
    if not isinstance(database, str):
        raise ValueError(f"{MVP_READINESS}: persistence.database must be a string")
    if not isinstance(schemas, dict) or not schemas:
        raise ValueError(f"{MVP_READINESS}: persistence.schemas must be a non-empty mapping")
    if not isinstance(rules, list) or not all(isinstance(rule, str) for rule in rules):
        raise ValueError(f"{MVP_READINESS}: persistence.rules must be a list of strings")

    lines = projection_header(
        [MVP_READINESS],
        "the accepted S4 implementation-readiness persistence ownership below",
    ) + diagram_prelude("MVP Persistence Ownership (not ERD)")

    lines.append(f'frame "{plantuml_text(database)}" {{')
    for schema_index, (schema_name, tables) in enumerate(schemas.items(), start=1):
        table_names = ensure_string_list(
            tables,
            path=MVP_READINESS,
            field=f"persistence.schemas.{schema_name}",
        )
        table_lines = "\\n".join(f"• {plantuml_text(table)}" for table in table_names)
        label = f"{plantuml_text(schema_name)}\\n{table_lines}"
        lines.append(
            f'  rectangle "{label}" as persistence_schema_{schema_index:02d} #eef6ff'
        )
    lines.append("}")

    append_text_legend(
        lines,
        "Scope",
        [
            (
                "Projection boundary",
                "Shows accepted database/schema/table ownership only. It does not claim columns, keys, foreign keys, cardinalities, indexes, or a full persistence model.",
            ),
            *[(f"Rule {index}", rule) for index, rule in enumerate(rules, start=1)],
        ],
    )
    lines.extend(["", "@enduml", ""])
    return "\n".join(lines)


def main() -> int:
    peer_names, composition_names, relationships = load_strategic_model()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    projections = {
        CONTEXT_MAP_OUTPUT: render_context_map(peer_names, relationships),
        COLLABORATION_MAP_OUTPUT: render_collaboration_map(
            peer_names, composition_names, relationships
        ),
        MVP_JOURNEY_OUTPUT: render_mvp_journey(),
        RC_PROCESS_OUTPUT: render_resource_curation_process(),
        RC_DOMAIN_OUTPUT: render_resource_catalogue_domain_model(),
        MVP_TACTICAL_OUTPUT: render_mvp_tactical_domain_model(),
        PERSISTENCE_OWNERSHIP_OUTPUT: render_persistence_ownership(),
    }
    for path, content in projections.items():
        path.write_text(content, encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
