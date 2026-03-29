---
name: release
description: Manage branch, GitHub PR, merge, and state advancement for an approved numbered spec, and only mark the spec done after the PR lifecycle is complete.
---

# Release

## Use When

- Review and verification are complete and the active spec worktree is ready to move through PR or merge.

## Inputs

- review report from the canonical checkout, typically via `.ralph/shared/reports/`
- verification report from the canonical checkout, typically via `.ralph/shared/reports/`
- active workflow state from `.ralph/shared/state/workflow-state.json` or the resolved canonical `.ralph/state/workflow-state.json`
- active spec queue entry from `.ralph/shared/state/spec-queue.json` or the resolved canonical `.ralph/state/spec-queue.json`
- git status and branch information
- GitHub PR metadata when available

## Workflow

1. Confirm review and verification evidence exists.
2. Confirm the active branch matches the active spec queue entry in the assigned spec worktree.
3. Confirm the assigned spec worktree is clean before attempting PR or merge actions. A clean worktree is required for release.
4. Resolve shared-state reads and shared report reads to the canonical checkout directly or through `.ralph/shared/`; do not rely on tracked shared-control-plane copies inside the worktree.
5. Read the latest `Commit Evidence` and summarize the task-to-commit traceability in the release report.
6. If no PR exists yet and policy requires one, create or record the GitHub PR.
7. If review and verification pass, merge the PR or record the merge result.
8. Record the release outcome in role-local artifacts and the release report only.
9. Do not mutate shared queue or workflow state directly.
10. Write the release report to the canonical `.ralph/reports/<run-id>/<spec-key>/release.md`, typically via `.ralph/shared/reports/`.

## Outputs

- the canonical role report path, typically `.ralph/reports/<run-id>/<spec-key>/release.md`

## Stop Condition

Stop after the PR or merge outcome and next action are recorded.
