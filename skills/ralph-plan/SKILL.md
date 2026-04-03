---
name: ralph-plan
description: Turn a Ralph project PRD into execution-ready planning artifacts by sequencing specification, research, planning, task generation, and plan-check before implementation begins.
---

# Ralph Plan

Generate execution-ready planning artifacts for a Ralph-managed project without starting implementation.

Use this as the public planning entry point after requirements are understood.

This public entrypoint is a thin launcher. It should keep the invoking thread focused on Ralph doctrine and immediately hand planning work to a dedicated Ralph planning coordinator subagent.

In this source repository, the root runtime artifacts are dogfood examples. Installed target repos should use their own copied scaffold from `src/` and generate their own runtime records after installation.

## Use When

- A project PRD already exists and needs to become execution-ready.
- The user wants a numbered spec queue, synchronized `spec.md`, `plan.md`, `tasks.md`, and `task-state.json` artifacts without starting implementation.
- The installed harness exists and the next useful step is planning rather than execution.

## Workflow

1. Read the project PRD, project policy, and any related artifacts.
2. Immediately spawn a dedicated Ralph planning coordinator subagent with forked context semantics and the canonical Ralph plan config.
3. Keep the invoking thread thin after launch. It may pass the repo path or user request into the planning coordinator, wait for completion, and relay the result, but it must not produce planning artifacts inline.
4. Inside the planning coordinator, decompose the PRD into ordered epochs and numbered specs, then delegate `specify` for any seeded or refreshed spec that still needs a decision-complete `spec.md`.
5. Delegate same-batch `research` only when the refreshed planning batch needs research before implementation planning can settle.
6. Delegate `plan` to produce or refresh `.ralph/state/spec-queue.json`, `specs/INDEX.md`, `specs/<spec-id>-<slug>/plan.md`, and any plan-owned supporting artifacts.
7. Delegate `task-gen` for every spec that should leave planning execution-ready so `specs/<spec-id>-<slug>/tasks.md` and `specs/<spec-id>-<slug>/task-state.json` are synchronized.
8. Delegate `plan-check` before finishing whenever the intent is to hand the repo to `$ralph-execute`.
9. Seed or refresh scheduler metadata such as `depends_on_spec_ids`, admission state, and default worktree metadata for each spec.
10. Reject dependency cycles or missing dependency references instead of guessing.
11. Keep tasks dependency-ordered and small enough for focused implementation passes.
12. Do not invent implicit dependencies or queue-head priority. Later execution should honor explicit scheduling targets first, then fill the remaining ready set.
13. Keep any planning-time parallelism bounded to same-batch `research` only; later execution uses the scheduler admission window and hard dependencies.
14. Stop before code changes or implementation begin.
15. Recommend the next entry point:
   - `$ralph-execute` when the installed harness should take over execution
   - `$ralph-prd` when requirements are still too unclear and need reshaping

## Outputs

- `.ralph/state/spec-queue.json`
- `specs/INDEX.md`
- `specs/<spec-id>-<slug>/spec.md`
- `specs/<spec-id>-<slug>/research.md` when research is complete for that spec
- `specs/<spec-id>-<slug>/plan.md`
- `specs/<spec-id>-<slug>/tasks.md` when planning is sufficiently complete
- `specs/<spec-id>-<slug>/task-state.json` when the spec is meant to leave planning execution-ready
- a `plan-check` outcome or equivalent confirmation when the spec is meant to hand off directly to execution
- a concise recommendation for the next public entry point

## References

- Read `references/planning-artifacts.md` for the planning artifact set and sequencing expectations.

## Completion

Stop once the planning coordinator has written or updated the intended planning artifacts, every execution-ready spec has synchronized `tasks.md` plus `task-state.json`, and the next recommended entry point is clear.
