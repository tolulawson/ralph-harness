---
name: verify
description: Run the required checks for the active numbered spec, capture exact evidence, and distinguish passing, failing, and blocked verification outcomes.
---

# Verify

## Use When

- Review has passed or the policy explicitly requests verification.

## Inputs

- active task acceptance criteria
- active spec queue entry
- `.ralph/policy/project-policy.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- in-scope artifacts and reports

## Workflow

1. Read the required checks from policy, project facts, the active task, and the active spec plan.
2. Run the smallest set of commands that prove the outcome.
3. Record exact pass, fail, or blocked evidence.
4. Capture durable command truths or failure signatures in `Candidate Learnings` when they are project-relevant.
5. Treat the active PR branch as the verification unit when PR metadata exists.
6. Write a verification report.

## Outputs

- `.ralph/reports/<run-id>/verify.md`
- optional `specs/<spec-key>/verification.md`

## Stop Condition

Stop after the verification result and evidence are recorded.
