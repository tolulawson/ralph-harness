---
name: verify
description: Run the required checks for the active numbered spec, capture exact evidence, and distinguish passing, failing, and blocked verification outcomes.
---

# Verify

## Use When

- Review has passed or the policy explicitly requests verification.

## Inputs

- active task acceptance criteria
- canonical task entry from `specs/<spec-key>/task-state.json`
- active spec queue entry
- latest implementation or review report
- `.ralph/policy/project-policy.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- in-scope artifacts and reports

## Workflow

1. Read the required checks from policy, project facts, the active task, and the active spec plan.
2. Run the smallest set of commands that prove the outcome.
3. Record exact pass, fail, or blocked evidence and tie the result to the checkpoint listed in `Commit Evidence`.
4. Capture durable command truths or failure signatures in `Candidate Learnings` when they are project-relevant.
5. Treat the active PR branch as the verification unit when PR metadata exists.
6. Preserve or refresh the `Commit Evidence` section so the release role can trace the verified checkpoint cleanly.
7. Fill in the `Interruption Assessment` section and use `Scope: interrupt` only for failing out-of-scope bugs that should preempt the normal queue.
8. Write a verification report.

## Outputs

- `.ralph/reports/<run-id>/verify.md`
- optional `specs/<spec-key>/verification.md`

## Stop Condition

Stop after the verification result and evidence are recorded.
