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
3. If no PR exists yet and policy requires one, create or record the GitHub PR.
4. Update PR metadata in the queue and workflow state.
5. If review and verification pass, merge the PR or record the merge result.
6. Advance workflow state and spec status only after the PR outcome is known.
7. Write a release report.

## Outputs

- `.ralph/reports/<run-id>/release.md`
- updated workflow state
- updated spec queue state

## Stop Condition

Stop after the PR or merge outcome and next action are recorded.
