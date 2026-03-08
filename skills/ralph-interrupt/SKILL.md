---
name: ralph-interrupt
description: Inject a bugfix interrupt into an already-installed Ralph harness by creating a new interrupt spec that preempts the normal queue and resumes paused work after release.
---

# Ralph Interrupt

Create a new interrupt spec in the current repository for a failing out-of-scope bug that should run ahead of the remaining normal queue.

Use this as the public manual entry point when a human identifies a bug that belongs to an earlier spec or no spec at all and wants it fixed before the queue continues.

In this source repository, the root runtime artifacts are dogfood examples. Installed target repos should use their own copied scaffold from `src/` and generate their own runtime records after installation.

## Use When

- The current repository already has the Ralph harness installed.
- A bug has been identified that is outside the current spec's intended scope.
- The bug should preempt the remaining normal queue and be tracked as its own numbered interrupt spec.

## Workflow

1. Verify the Ralph harness exists in the current repository.
2. Read the constitution, runtime contract, project policy, workflow state, and spec queue.
3. Confirm the bug is out of scope for the currently active spec.
4. Create a new numbered spec with `kind = interrupt`.
5. Link the interrupt to `origin_spec_key` and `origin_task_id` when they exist, else leave them `null`.
6. Pause the current spec and task, update `resume_spec_stack`, and mirror the top paused spec in `resume_spec_id`.
7. Seed the new interrupt spec artifacts and `task-state.json`.
8. If the bug belongs to an earlier spec, append an entry to `specs/<origin-spec-key>/amendments.md`.
9. Recommend the next public entry point:
   - `$ralph-execute` when the installed harness should immediately run the interrupt spec
   - `$ralph-plan` only when the interrupt spec still needs broader planning before execution

## Outputs

- updated `.ralph/state/spec-queue.json`
- updated `.ralph/state/workflow-state.json`
- updated `.ralph/state/workflow-state.md`
- updated `specs/INDEX.md`
- new `specs/<spec-key>/spec.md`
- new `specs/<spec-key>/plan.md`
- new `specs/<spec-key>/tasks.md`
- new `specs/<spec-key>/task-state.json`
- updated `specs/<origin-spec-key>/amendments.md` when applicable

## Guardrails

- Do not use this for defects that still belong to the current spec's own scope.
- Do not rewrite the original spec, plan, or tasks in place as part of the canonical interrupt flow.
- Keep earlier specs historically immutable and record corrected guidance through linked amendments.

## Completion

Stop once the interrupt spec is seeded cleanly and the next recommended entry point is clear.
