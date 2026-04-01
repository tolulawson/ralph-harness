---
name: ralph-plan
description: Turn a Ralph project PRD into queue-ready planning artifacts by producing epochs, numbered specs, implementation plans, and dependency-ordered tasks, then stop before implementation.
---

# Ralph Plan

Generate queue-ready planning artifacts for a Ralph-managed project without starting implementation.

Use this as the public planning entry point after requirements are understood.

This public entrypoint is a thin launcher. It should keep the invoking thread focused on Ralph doctrine and immediately hand planning work to a dedicated `plan` subagent.

In this source repository, the root runtime artifacts are dogfood examples. Installed target repos should use their own copied scaffold from `src/` and generate their own runtime records after installation.

## Use When

- A project PRD already exists and needs to become execution-ready.
- The user wants a numbered spec queue, `spec.md`, `plan.md`, and `tasks.md` artifacts without starting implementation.
- The installed harness exists and the next useful step is planning rather than execution.

## Workflow

1. Read the project PRD, project policy, and any related artifacts.
2. Immediately spawn a dedicated `plan` subagent with forked context semantics and the canonical Ralph plan config.
3. Keep the invoking thread thin after launch. It may pass the repo path or user request into the `plan` subagent, wait for completion, and relay the result, but it must not produce planning artifacts inline.
4. Inside the `plan` subagent, decompose the PRD into ordered epochs and numbered specs.
5. Produce or update `.ralph/state/spec-queue.json`.
6. Produce or update `specs/INDEX.md`.
7. Produce or update `specs/<spec-id>-<slug>/spec.md`.
8. Produce or update spec-local `research.md` artifacts when the planning batch is ready for research.
9. Produce or update `specs/<spec-id>-<slug>/plan.md`.
10. Produce or update `specs/<spec-id>-<slug>/tasks.md` when enough information exists.
11. Seed or refresh scheduler metadata such as `depends_on_spec_ids`, admission state, and default worktree metadata for each spec.
12. Reject dependency cycles or missing dependency references instead of guessing.
13. Keep the tasks dependency-ordered and small enough for focused implementation passes.
14. Do not invent implicit dependencies or queue-head priority. Later execution should honor explicit scheduling targets first, then fill the remaining ready set.
15. Keep any planning-time parallelism bounded to same-batch `research` only; later execution uses the scheduler admission window and hard dependencies.
16. Stop before code changes or implementation begin.
17. Recommend the next entry point:
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
