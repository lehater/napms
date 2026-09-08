# Decision and unknown protocol

## States

Every material statement used for design must be distinguishable as:
- **accepted/known** — supported by canonical project truth or explicit owner decision;
- **hypothesis** — plausible proposition being tested;
- **unknown** — evidence/decision is insufficient;
- **conflict** — authoritative sources disagree.

## No-invention rule

Never represent a hypothesis or unknown as accepted product/domain truth because it makes implementation convenient.

For a material unknown:
1. inspect canonical repository evidence first;
2. determine whether it is factual, semantic or a To-Be choice;
3. resolve it with evidence, focused owner decision or an accepted explicit deferral;
4. keep the relevant gate closed if the unknown is blocking.

A deferral is valid only when it states why the unknown is non-blocking now and what event requires revisiting it.

## Decision record

Consequential target choices belong in the canonical domain/requirements/architecture artifact or an ADR. Chat transcripts are not canonical decisions.
