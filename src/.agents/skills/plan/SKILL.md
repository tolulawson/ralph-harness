---
name: plan
description: Convert a project PRD or numbered feature specification into a dependency-aware implementation plan, seed or refresh the scheduler queue, and create the planning artifacts needed for execution.
---

# Scheduler-Aware Plan

## Use When

- A project PRD is ready to be decomposed into epochs and numbered specs.
- A numbered spec exists and execution design needs to be locked in.

## Inputs

- `tasks/prd-<project>.md`
- optional active `specs/<spec-key>/spec.md`
- `.ralph/shared/context/project-truths.md` or the resolved canonical `.ralph/context/project-truths.md`
- `.ralph/shared/context/project-facts.json` or the resolved canonical `.ralph/context/project-facts.json`
- `.ralph/shared/context/learning-summary.md` or the resolved canonical `.ralph/context/learning-summary.md`
- `.ralph/shared/state/spec-queue.json` or the resolved canonical `.ralph/state/spec-queue.json`
- `.ralph/shared/policy/project-policy.md` or the resolved canonical `.ralph/policy/project-policy.md`
- optional active `specs/<spec-key>/research.md`
- current harness state

If the project PRD is missing, stop and report that the PRD step must complete first.

## Workflow

1. Load the project PRD, queue state, and any existing spec artifacts. Shared-state reads and writes must resolve to the canonical checkout directly or through `.ralph/shared/`.
2. If the queue does not exist yet, decompose the PRD into ordered epochs and numbered specs.
3. Create or refresh:
   - `.ralph/state/spec-queue.json`
   - `specs/INDEX.md`
   - `specs/<spec-key>/` directories for seeded specs
4. Seed or refresh scheduler metadata for each spec:
   - `depends_on_spec_ids`
   - `admission_status`
   - default worktree metadata
   - canonical `base_branch` from `.ralph/context/project-facts.json` unless a spec explicitly overrides it
   - compatibility mirrors only when needed
5. Reject dependency cycles or missing dependency targets instead of guessing.
6. For the active spec, define the canonical `task-state.json` lifecycle expectations before task generation begins.
7. For the active spec, require `research.md` when the queue entry says `research_status = done`.
8. For the active spec, fill the implementation plan structure in `specs/<spec-key>/plan.md`.
9. Build a technical context section that captures architecture, interfaces, dependencies, verification strategy, orchestration stop conditions, worktree rules, bootstrap requirements, and rollout or migration considerations.
8. Add:
   - `Research Inputs`
   - `Implementation Guardrails`
   - `Goal-Backward Verification` with observable truths, required artifacts, and critical links
10. Create supporting artifacts only when needed:
   - `research.md`
   - `data-model.md`
   - `contracts/`
   - `quickstart.md`
11. Record any explicit project truths or optional structured facts discovered during planning when they are clearly established, including the canonical `base_branch` and any `validation_bootstrap_commands` that bootstrap should run before implementation.
12. Recheck the plan after the supporting artifacts exist and ensure the implementation path is decision-complete.
13. Write the role report to the canonical report path and recommend the next role.

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
- the canonical role report path, typically `.ralph/reports/<run-id>/<spec-key>/plan.md` when planning an existing numbered spec, or `.ralph/reports/<run-id>/plan.md` during project-level queue seeding

## Stop Condition

Stop after the queue-visible planning artifacts and report are complete.
