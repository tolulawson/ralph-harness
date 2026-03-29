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
- latest implementation report
- `git status --short --branch`
- `.ralph/shared/context/project-truths.md` or the resolved canonical `.ralph/context/project-truths.md`
- `.ralph/shared/context/learning-summary.md` or the resolved canonical `.ralph/context/learning-summary.md`
- `specs/<spec-key>/research.md` when present
- related spec and plan

## Workflow

1. Review the assigned work without editing files.
2. Prioritize findings by severity.
3. If the target is spec, plan, or tasks quality, use the `analyze` helper skill to perform a read-only consistency pass across the artifacts before writing findings.
4. Treat missing or failed `Quality Gate`, missing `Commit Evidence`, a dirty worktree at handoff, or obviously mixed-scope task commits as findings.
5. If there are no findings, say so explicitly.
6. Call out residual risks or verification gaps.
7. Record any durable anti-patterns, review rules, or repeat failure signatures in `Candidate Learnings`.
8. Treat the assigned spec worktree or active PR branch as the review unit when PR metadata exists, but read shared state and prior reports from the canonical checkout directly or through `.ralph/shared/`.
9. Flag any implementation that materially violates the spec constraints or the confirmed guidance in `research.md`.
10. Preserve or refresh the `Quality Gate` section so `React Effects Audit` and `Deslopify Lite` status remain explicit for the next role.
11. Preserve or refresh the `Commit Evidence` section so the verified checkpoint remains explicit for the next role.
12. Fill in the `Interruption Assessment` section and use `Scope: interrupt` only when a failing finding is outside the current spec's intended scope.
13. Write the review report to the canonical `.ralph/reports/<run-id>/<spec-key>/review.md`, typically via `.ralph/shared/reports/`.

## Outputs

- the assigned role report path, typically `.ralph/reports/<run-id>/<spec-key>/review.md`
- optional `specs/<spec-key>/review.md`

## Stop Condition

Stop after findings or approval are recorded and the next role is recommended.
