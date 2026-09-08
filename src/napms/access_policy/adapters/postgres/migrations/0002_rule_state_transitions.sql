CREATE TABLE IF NOT EXISTS napms_access_policy.access_rule_state_transitions (
    rule_id uuid NOT NULL
        REFERENCES napms_access_policy.access_rules(rule_id),
    sequence_no integer NOT NULL
        CHECK (sequence_no > 0),
    from_state text NOT NULL
        CHECK (from_state IN ('Active', 'Inactive')),
    to_state text NOT NULL
        CHECK (to_state IN ('Active', 'Inactive')),
    actor_id text NOT NULL,
    effective_time timestamptz NOT NULL,
    governance_scope text NOT NULL,
    authority_reference text NOT NULL,
    PRIMARY KEY (rule_id, sequence_no),
    CHECK (from_state <> to_state)
);
