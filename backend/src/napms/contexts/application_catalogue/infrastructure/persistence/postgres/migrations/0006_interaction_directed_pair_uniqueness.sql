CREATE UNIQUE INDEX IF NOT EXISTS uq_interaction_directed_pair
ON napms_application_catalogue.interaction_definitions (
    application_id,
    source_component_id,
    destination_component_id
);
