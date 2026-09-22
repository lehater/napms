#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluate_frontend_presentation_semantics import (
    evaluate as evaluate_presentation_semantics,
)
from evaluate_security_identity_semantics import (
    evaluate as evaluate_security_identity_semantics,
)


def evaluate() -> dict[str, Any]:
    evaluations: list[dict[str, Any]] = []
    for result in (
        evaluate_security_identity_semantics(),
        evaluate_presentation_semantics(),
    ):
        evaluations.extend(result.get("semantic_evaluations", []) or [])
    return {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": evaluations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--require-accepted", action="store_true")
    args = parser.parse_args()

    result = evaluate()
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)

    rejected = [
        item
        for item in result["semantic_evaluations"]
        if item.get("status") != "ACCEPTED"
    ]
    if args.require_accepted and rejected:
        for item in rejected:
            print(f"{item.get('artifact')}: semantic acceptance REJECTED")
            for finding in item.get("findings", []) or []:
                print(
                    f"  - {finding.get('code')}: {finding.get('message')}"
                )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
