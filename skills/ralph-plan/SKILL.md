---
name: ralph-plan
description: Turn a Ralph project PRD into queue-ready planning artifacts by producing epochs, numbered specs, implementation plans, and dependency-ordered tasks, then stop before implementation.
---

# Ralph Plan

Generate queue-ready planning artifacts for a Ralph-managed project without starting implementation.

Use this as the public planning entry point after requirements are understood.

In this source repository, the root runtime artifacts are dogfood examples. Installed target repos should use their own copied scaffold from `src/` and generate their own runtime records after installation.

## Use When

- A project PRD already exists and needs to become execution-ready.
- The user wants a numbered spec queue, `spec.md`, `plan.md`, and `tasks.md` artifacts without starting implementation.
- The installed harness exists and the next useful step is planning rather than execution.

## Workflow

1. Read the project PRD, project policy, and any related artifacts.
2. Decompose the PRD into ordered epochs and numbered specs.
3. Produce or update `.ralph/state/spec-queue.json`.
4. Produce or update `specs/INDEX.md`.
5. Produce or update `specs/<spec-id>-<slug>/spec.md`.
6. Produce or update spec-local `research.md` artifacts when the planning batch is ready for research.
7. Produce or update `specs/<spec-id>-<slug>/plan.md`.
8. Produce or update `specs/<spec-id>-<slug>/tasks.md` when enough information exists.
9. Seed or refresh scheduler metadata such as `depends_on_spec_ids`, admission state, and default worktree metadata for each spec.
10. Keep the tasks dependency-ordered and small enough for focused implementation passes.
11. Keep any parallelism bounded to same-batch `research` only during planning; later execution uses the scheduler admission window and hard dependencies.
12. Stop before code changes or implementation begin.
13. Recommend the next entry point:
   - `$ralph-execute` when the installed harness should take over execution
   - `$ralph-prd` when requirements are still too unclear and need reshaping

## Outputs

- `.ralph/state/spec-queue.json`
- `specs/INDEX.md`
- `specs/<spec-id>-<slug>/spec.md`
- `specs/<spec-id>-<slug>/research.md` when research is complete for that spec
- `specs/<spec-id>-<slug>/plan.md`
- `specs/<spec-id>-<slug>/tasks.md` when planning is sufficiently complete
- a concise recommendation for the next public entry point

## References

- Read `references/planning-artifacts.md` for the planning artifact set and sequencing expectations.

## Completion

Stop once the queue-ready planning artifacts are written or updated and the next recommended entry point is clear.
