CREATE TABLE IF NOT EXISTS napms_access_policy.access_rule_effective_windows (
    rule_id uuid PRIMARY KEY
        REFERENCES napms_access_policy.access_rules(rule_id),
    start_at timestamptz NOT NULL,
    end_at timestamptz NOT NULL,
    CHECK (start_at < end_at)
);

CREATE TABLE IF NOT EXISTS napms_access_policy.access_rule_effective_window_changes (
    rule_id uuid NOT NULL
        REFERENCES napms_access_policy.access_rules(rule_id),
    sequence_no integer NOT NULL
        CHECK (sequence_no > 0),
    previous_start timestamptz NULL,
    previous_end timestamptz NULL,
    new_start timestamptz NULL,
    new_end timestamptz NULL,
    actor_id text NOT NULL,
    effective_time timestamptz NOT NULL,
    governance_scope text NOT NULL,
    authority_reference text NOT NULL,
    PRIMARY KEY (rule_id, sequence_no),
    CHECK ((previous_start IS NULL) = (previous_end IS NULL)),
    CHECK ((new_start IS NULL) = (new_end IS NULL)),
    CHECK (previous_start IS NULL OR previous_start < previous_end),
    CHECK (new_start IS NULL OR new_start < new_end),
    CHECK (
        ROW(previous_start, previous_end)
        IS DISTINCT FROM
        ROW(new_start, new_end)
    )
);
