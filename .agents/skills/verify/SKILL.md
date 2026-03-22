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
- `specs/<spec-key>/research.md` when present
- in-scope artifacts and reports

## Workflow

1. Read the required checks from policy, project facts, the active task, the active spec plan, and the plan's goal-backward verification model.
2. Run the smallest set of commands that prove the outcome.
3. Verify not only commands but also the observable truths, required artifacts, and critical links called out in the plan.
4. Record exact pass, fail, or blocked evidence and tie the result to the checkpoint listed in `Commit Evidence`.
5. Capture durable command truths or failure signatures in `Candidate Learnings` when they are project-relevant.
6. Treat the assigned spec worktree or active PR branch as the verification unit when PR metadata exists.
7. Preserve or refresh the `Commit Evidence` section so the release role can trace the verified checkpoint cleanly.
8. Fill in the `Interruption Assessment` section and use `Scope: interrupt` only for failing out-of-scope bugs that should preempt the normal queue.
9. Write a verification report.

## Outputs

- the assigned role report path, typically `.ralph/reports/<run-id>/<spec-key>/verify.md`
- optional `specs/<spec-key>/verification.md`

## Stop Condition

Stop after the verification result and evidence are recorded.
