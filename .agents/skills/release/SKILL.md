---
name: release
description: Manage branch, GitHub PR, merge, and state advancement for an approved numbered spec, and only mark the spec done after the PR lifecycle is complete.
---

# Release

## Use When

- Review and verification are complete and the active spec is ready to move through PR or merge.

## Inputs

- review report
- verification report
- active workflow state
- active spec queue entry
- git status and branch information
- GitHub PR metadata when available

## Workflow

1. Confirm review and verification evidence exists.
2. Confirm the active branch matches the active spec queue entry.
3. Confirm the worktree is clean before attempting PR or merge actions. A clean worktree is required for release.
4. Read the latest `Commit Evidence` and summarize the task-to-commit traceability in the release report.
5. If no PR exists yet and policy requires one, create or record the GitHub PR.
6. If review and verification pass, merge the PR or record the merge result.
7. Record the release outcome in role-local artifacts and the release report only.
8. Do not mutate shared queue or workflow state directly.
9. Write a release report.

## Outputs

- `.ralph/reports/<run-id>/release.md`

## Stop Condition

Stop after the PR or merge outcome and next action are recorded.
