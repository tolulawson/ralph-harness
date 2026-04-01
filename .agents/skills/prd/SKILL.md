---
name: prd
description: Create a comprehensive product requirements document from a project idea by asking a few critical questions, defining bounded user stories, and mapping the work into ordered epochs without doing implementation work.
---

# PRD Generator

## Use When

- A new project or major initiative needs a master PRD.
- Existing product intent is too vague for spec queue planning.

## The Job

1. Receive the project or initiative description.
2. Ask 3-5 essential clarifying questions with lettered options.
3. Generate a structured project PRD based on the answers and reasonable defaults.
4. Define an initial ordered epoch map.
5. Record any explicit project truths already stated by the user in `.ralph/context/project-truths.md`.
6. Save the PRD to `tasks/prd-<project>.md`.
7. Write the harness report to the canonical `.ralph/reports/<run-id>/prd.md`.

**Important:** Do not start implementing. Just create the PRD, epoch framing, and report.

## Step 1: Clarifying Questions

Ask only the questions that materially change:

- the problem or goal
- the core functionality
- the scope or boundaries
- the success criteria
- how the work should be grouped into major phases

Use lettered options so a user can answer quickly.

If the user has already answered the important questions, do not ask them again.

## Step 2: PRD Structure

Generate the PRD with these sections:

1. `Introduction`
2. `Goals`
3. `Epoch Map`
4. `User Stories`
5. `Functional Requirements`
6. `Non-Goals`
7. `Design Considerations` when relevant
8. `Technical Considerations` when relevant
9. `Success Metrics`
10. `Open Questions`

### Epoch Rules

- Epochs are ordered themes or milestones.
- Each epoch should name the specs it is expected to contain.
- Epochs are planning groups, not execution units.

## Outputs

- `tasks/prd-<project>.md`
- optional updates to `.ralph/context/project-truths.md`
- the canonical report path `.ralph/reports/<run-id>/prd.md`

## Harness Adaptation Rules

- Replace any generic verification wording with this harness's `verify` role and optional UI or mobile helper skills.
- Recommend `plan` as the next role unless the PRD is blocked by unresolved scope decisions.

## Stop Condition

Stop after the PRD and report are complete and the recommended next role is clear.
