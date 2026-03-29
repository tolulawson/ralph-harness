---
name: bootstrap
description: Prepare the assigned spec worktree and local validation environment before any execution role begins.
---

# Worktree Bootstrap

## Use When

- A runtime session has claimed a spec role slot and must prepare the local worktree before execution.
- `implement` or another worker role is about to run in a session that has not yet passed bootstrap for that claim.

## Inputs

- active spec entry from `.ralph/shared/state/spec-queue.json` or the resolved canonical `.ralph/state/spec-queue.json`
- current claim from `.ralph/shared/state/worker-claims.json` or the resolved canonical `.ralph/state/worker-claims.json`
- `.ralph/shared/context/project-truths.md` or the resolved canonical `.ralph/context/project-truths.md`
- `.ralph/shared/context/project-facts.json` or the resolved canonical `.ralph/context/project-facts.json`
- `.ralph/shared/context/learning-summary.md` or the resolved canonical `.ralph/context/learning-summary.md`
- `.ralph/shared/policy/project-policy.md` or the resolved canonical `.ralph/policy/project-policy.md`
- `git status --short --branch`

## Workflow

1. Read the active spec entry, project facts, and current claim.
2. Resolve the canonical base branch from `.ralph/context/project-facts.json`, unless the spec queue entry explicitly overrides `base_branch`.
3. Create or reuse the assigned spec worktree under `.ralph/worktrees/`.
4. Verify the worktree branch matches the assigned spec branch, that the canonical checkout is not being used as the execution worktree, and that `.ralph/shared/` resolves shared artifacts back to the canonical checkout.
5. Hydrate the fresh worktree conservatively:
   - copy only allowlisted files from `.ralph/context/project-facts.json` `bootstrap_env_files`
   - do not copy dependency, cache, build, or other generated artifacts that match `bootstrap_copy_exclude_globs`
   - leave `node_modules`, virtualenvs, `.next`, `dist`, `build`, `.turbo`, `.cache`, and similar paths alone unless the project facts explicitly opt into a narrower policy
6. Prepare the local environment in this order:
   - `.ralph/context/project-facts.json` `worktree_bootstrap_commands`
   - `.ralph/context/project-facts.json` `validation_bootstrap_commands`
   - then `.ralph/context/project-facts.json` `verification_commands` when they are safe as bootstrap checks
7. Record exact command results, copied files, skipped files, exclusions, and any missing prerequisites.
8. Update the active claim bootstrap lifecycle in the canonical `.ralph/state/worker-claims.json` so the claim records whether bootstrap is `in_progress`, `passed`, or `failed`.
9. Write the bootstrap report to the canonical `.ralph/reports/<run-id>/<spec-key>/bootstrap.md`, typically via `.ralph/shared/reports/`.
10. Recommend `implement` only when bootstrap passed and the claim is validation-ready.

## Outputs

- prepared assigned spec worktree
- generated `.ralph/shared/` overlay inside the assigned worktree
- copied or skipped allowlisted env or config files
- bootstrap lifecycle updates in `.ralph/state/worker-claims.json`
- `.ralph/reports/<run-id>/<spec-key>/bootstrap.md`

## Stop Condition

Stop after the assigned claim has a terminal bootstrap result, the bootstrap report is written, and the next role is clear.
