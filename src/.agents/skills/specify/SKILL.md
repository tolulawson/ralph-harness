---
name: specify
description: Turn an approved project PRD or queued spec seed into a decision-complete numbered feature specification with clear scope, requirements, edge cases, and delivery notes.
---

# Spec-Style Specify

## Use When

- A numbered spec exists in the queue and needs a concrete spec artifact.

## Inputs

- `tasks/prd-<project>.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/policy/project-policy.md`
- related repo context

If the project PRD or spec queue entry is missing, stop and report that planning must complete first.

## Workflow

1. Treat the project PRD and the active queue entry as the canonical inputs.
2. Use the queue entry's `spec_id`, `spec_slug`, and `epoch_id` to determine the output path.
3. Extract actors, actions, data, constraints, and success expectations from the PRD and queue entry.
4. Make informed guesses for low-risk gaps. Only mark critical ambiguities as `NEEDS CLARIFICATION` when they materially change scope or user experience.
5. Write `specs/<spec-key>/spec.md` with:
   - metadata
   - summary
   - scope
   - spec constraints
   - user stories
   - requirements
   - edge cases
   - delivery notes
   - deferred scope
6. Ensure each requirement is testable and each user story is actionable.
7. Create a lightweight quality checklist at `specs/<spec-key>/checklists/requirements.md`.
8. Review the spec against the checklist and update it until it passes or until any remaining clarification items are explicit.
9. Write the role report and recommend the next role.

## Outputs

- `specs/<spec-key>/spec.md`
- `specs/<spec-key>/checklists/requirements.md`
- `.ralph/reports/<run-id>/specify.md`

## Stop Condition

Stop after the spec and report are complete.
