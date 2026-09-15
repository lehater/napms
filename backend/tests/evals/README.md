# Harness evals

This directory contains eval inputs/contracts. Keep deterministic repository validation separate from observations produced by an actual model run.

## Skill routing

`skill-routing-cases.json` defines prompts, the expected primary Skill, and confusable Skills that must not be selected.

`python tools/validate_skill_routing.py` validates only corpus structure and coverage. A green `harness-check` therefore proves that the routing corpus is well formed; it does **not** prove that a model routed the prompts correctly.

To evaluate an actual routing run, capture observations as JSON:

```json
[
  {
    "id": "harness-audit",
    "selected_skill": "agent-harness-design",
    "files_read": 4,
    "skills_loaded": 1,
    "tool_calls_before_first_action": 2,
    "stopped_early": false
  }
]
```

Then run:

```text
python tools/evaluate_skill_routing_results.py path/to/results.json
```

Use `--allow-partial` for a focused subset. Use `--baseline path/to/previous-results.json` to compare context/tooling metrics before and after a Harness change.

The routing runner itself is deliberately outside deterministic repository CI because model selection is an external, versioned execution dependency. The evaluator is repository-owned so observed results are judged against the same checked-in corpus and metrics contract.

## Other eval corpora

`lifecycle-transition-cases.json` and `semantic-level-classification-cases.json` are deterministic inputs for their owning validators/protocol tests.
