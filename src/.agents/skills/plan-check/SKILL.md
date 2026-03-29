---
name: plan-check
description: Review an admitted spec's spec, research, plan, and tasks artifacts before implementation to confirm they are complete, consistent, and safe for deterministic task progression within that spec.
---

# Plan Check

## Use When

- An admitted or next-runnable spec has `spec.md`, `plan.md`, `tasks.md`, and `task-state.json`.
- Implementation must be gated on artifact quality before any code changes begin.

## Inputs

- `.ralph/shared/constitution.md` or the resolved canonical `.ralph/constitution.md`
- `.ralph/shared/runtime-contract.md` or the resolved canonical `.ralph/runtime-contract.md`
- `.ralph/shared/policy/project-policy.md` or the resolved canonical `.ralph/policy/project-policy.md`
- `specs/<spec-key>/spec.md`
- `specs/<spec-key>/research.md` when present
- `specs/<spec-key>/plan.md`
- `specs/<spec-key>/tasks.md`
- `specs/<spec-key>/task-state.json`

## Workflow

1. Read the minimum context needed from the doctrine plus the spec artifacts. When the role runs from an assigned spec worktree, resolve shared doctrine files to the canonical checkout directly or through `.ralph/shared/`.
2. Use the `analyze` helper skill when a compact consistency pass will improve confidence.
3. Check:
   - requirement coverage
   - task freshness for a new worker
   - verification completeness
   - compliance with `research.md`
   - preservation of one-task-at-a-time execution within the admitted spec's own task graph
   - absence of deferred or out-of-scope leakage
4. Present findings first, ordered by severity.
5. If there are no findings, say so explicitly and recommend `implement`.
6. If findings indicate architecture or verification-model drift, recommend `plan`.
7. If findings indicate decomposition or task-state drift, recommend `task-gen`.
8. Write the plan-check report to the canonical `.ralph/reports/<run-id>/<spec-key>/plan-check.md`, typically via `.ralph/shared/reports/`.

## Outputs

- the canonical role report path, typically `.ralph/reports/<run-id>/<spec-key>/plan-check.md`
- optional `specs/<spec-key>/plan-check.md`

## Stop Condition

Stop after findings or approval are recorded and the next role is recommended.
