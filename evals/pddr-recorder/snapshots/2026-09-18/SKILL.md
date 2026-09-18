---
name: pddr-recorder
description: Create or update Project Design Decision Records when a project needs to preserve the reasoning, decision state, implementation state, evidence, and validation around a consequential Project, Product, or Process choice. Do not use for ordinary task logs or meeting transcripts.
---

# PDDR Recorder

Create a traceable record that lets the next human or agent understand what changed, why, what is actually approved, and what remains unimplemented or unverified.

Read the repository's PDDR specification and template before creating or updating a record. Prefer local project conventions when they are stricter.

## Invariants

- Never invent motives, agreement, dates, owners, or evidence.
- Never convert an AI suggestion or ambiguous user statement into an accepted decision.
- Use `needs-confirmation` when approval or historical state cannot be verified.
- Track `decision_status` and `delivery_status` independently.
- Use `delivery_status: unknown` when delivery cannot be verified; missing implementation evidence does not prove `not-started`.
- Do not mark delivery as `validated` without concrete evidence and a stated validation criterion.
- When superseding a record, create the successor, add reciprocal links, mark the old decision as superseded, and preserve its historical content.
- Exclude credentials, personal data, private conversation transcripts, and unnecessary confidential detail. Use a minimal summary and stable reference.

## Workflow

1. Determine whether the change is consequential enough for a PDDR. Skip routine work logs and simple implementation details.
2. Collect only supported facts: observation, options, explicit decision, delivery status, evidence, consequences, and revisit conditions. For a proposal, retain known options without implying consensus.
3. Search existing PDDR and ADR / DDR records to avoid duplicates and identify supersession links.
4. Draft from `templates/pddr.md`. If reconstructing history, separate `decision_date` from `recorded_date`.
5. Call out unknowns and confirmation needs directly in the record.
6. Validate the metadata, links, and the semantic distinction between proposed, accepted, implemented, and validated.
7. Present the record as a reviewable draft unless reliable evidence shows the required human approval already occurred.

When asked only to analyze or propose, do not write files or change external systems without separate authorization.
