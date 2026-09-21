CREATE SCHEMA IF NOT EXISTS application_deployment;

CREATE TABLE IF NOT EXISTS application_deployment.component_deployment (
    deployment_ref uuid PRIMARY KEY,
    component_ref uuid NOT NULL,
    resource_ref uuid NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
