---
name: plan
description: Convert a project PRD or numbered feature specification into an epoch-aware implementation plan, seed or refresh the FIFO spec queue, and create the planning artifacts needed for execution.
---

# Queue-Aware Plan

## Use When

- A project PRD is ready to be decomposed into epochs and numbered specs.
- A numbered spec exists and execution design needs to be locked in.

## Inputs

- `tasks/prd-<project>.md`
- optional active `specs/<spec-key>/spec.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- `.ralph/state/spec-queue.json`
- `.ralph/policy/project-policy.md`
- optional active `specs/<spec-key>/research.md`
- current harness state

If the project PRD is missing, stop and report that the PRD step must complete first.

## Workflow

1. Load the project PRD, queue state, and any existing spec artifacts.
2. If the queue does not exist yet, decompose the PRD into ordered epochs and numbered specs.
3. Create or refresh:
   - `.ralph/state/spec-queue.json`
   - `specs/INDEX.md`
   - `specs/<spec-key>/` directories for seeded specs
4. For the active spec, define the canonical `task-state.json` lifecycle expectations before task generation begins.
5. For the active spec, require `research.md` when the queue entry says `research_status = done`.
6. For the active spec, fill the implementation plan structure in `specs/<spec-key>/plan.md`.
7. Build a technical context section that captures architecture, interfaces, dependencies, verification strategy, orchestration stop conditions, and rollout or migration considerations.
8. Add:
   - `Research Inputs`
   - `Implementation Guardrails`
   - `Goal-Backward Verification` with observable truths, required artifacts, and critical links
9. Create supporting artifacts only when needed:
   - `research.md`
   - `data-model.md`
   - `contracts/`
   - `quickstart.md`
10. Record any explicit project truths or optional structured facts discovered during planning when they are clearly established.
11. Recheck the plan after the supporting artifacts exist and ensure the implementation path is decision-complete.
12. Write the role report and recommend the next role.

## Outputs

- `.ralph/state/spec-queue.json`
- `specs/INDEX.md`
- `specs/<spec-key>/plan.md`
- `specs/<spec-key>/research.md` when needed
- `specs/<spec-key>/data-model.md` when needed
- `specs/<spec-key>/contracts/` when needed
- `specs/<spec-key>/quickstart.md` when needed
- optional updates to `.ralph/context/project-truths.md`
- optional updates to `.ralph/context/project-facts.json`
- `.ralph/reports/<run-id>/plan.md`

## Stop Condition

Stop after the queue-visible planning artifacts and report are complete.
