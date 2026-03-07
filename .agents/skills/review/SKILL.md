---
name: review
description: Review an assigned task, branch, or GitHub PR for the active numbered spec with a findings-first mindset and record whether the work is ready for verification or needs another implementation pass.
---

# Review

## Use When

- A task or active spec branch has been implemented and needs review.

## Inputs

- in-scope diff, branch, or PR
- active task
- canonical task entry from `specs/<spec-key>/task-state.json`
- active spec queue entry
- related spec and plan

## Workflow

1. Review the assigned work without editing files.
2. Prioritize findings by severity.
3. If the target is spec, plan, or tasks quality, use the `analyze` helper skill to perform a read-only consistency pass across the artifacts before writing findings.
4. If there are no findings, say so explicitly.
5. Call out residual risks or verification gaps.
6. Treat the active PR branch as the review unit when PR metadata exists.
7. Write a review report.

## Outputs

- `.ralph/reports/<run-id>/review.md`
- optional `specs/<spec-key>/review.md`

## Stop Condition

Stop after findings or approval are recorded and the next role is recommended.
