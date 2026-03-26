---
name: bootstrap
description: Prepare the assigned spec worktree and local validation environment before any execution role begins.
---

# Worktree Bootstrap

## Use When

- A runtime session has claimed a spec role slot and must prepare the local worktree before execution.
- `implement` or another worker role is about to run in a session that has not yet passed bootstrap for that claim.

## Inputs

- active spec entry from `.ralph/state/spec-queue.json`
- current claim from `.ralph/state/worker-claims.json`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- `.ralph/policy/project-policy.md`
- `git status --short --branch`

## Workflow

1. Read the active spec entry, project facts, and current claim.
2. Resolve the canonical base branch from `.ralph/context/project-facts.json`, unless the spec queue entry explicitly overrides `base_branch`.
3. Create or reuse the assigned spec worktree under `.ralph/worktrees/`.
4. Verify the worktree branch matches the assigned spec branch and that the canonical checkout is not being used as the execution worktree.
5. Prepare the local validation environment using:
   - `.ralph/context/project-facts.json` `validation_bootstrap_commands`
   - then `.ralph/context/project-facts.json` `verification_commands` when they are safe as bootstrap checks
6. Record exact command results and any missing prerequisites.
7. Update the active claim bootstrap lifecycle so the claim records whether bootstrap is `in_progress`, `passed`, or `failed`.
8. Write `.ralph/reports/<run-id>/<spec-key>/bootstrap.md`.
9. Recommend `implement` only when bootstrap passed and the claim is validation-ready.

## Outputs

- prepared assigned spec worktree
- bootstrap lifecycle updates in `.ralph/state/worker-claims.json`
- `.ralph/reports/<run-id>/<spec-key>/bootstrap.md`

## Stop Condition

Stop after the assigned claim has a terminal bootstrap result, the bootstrap report is written, and the next role is clear.
