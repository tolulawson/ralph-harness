---
name: reporting
description: Standardize role handoff reports so every worker writes the same evidence-driven sections and the next fresh run can resume without hidden context.
---

# Reporting

## Use When

- Any role is writing a handoff report.

## Contract

Every report must include:

- `Objective`
- `Inputs Read`
- `Artifacts Written`
- `Verification`
- `Commit Evidence`
- `Candidate Learnings`
- `Open Issues`
- `Recommended Next Role`

## Rules

- Keep the report concise.
- Include exact artifact paths.
- Worker reports should use `.ralph/reports/<run-id>/<spec-key>/<role>.md`; the orchestrator report stays at `.ralph/reports/<run-id>/orchestrator.md`.
- Distinguish confirmed facts from recommendations.
- `Commit Evidence` must identify the task checkpoint commit under handoff, the matching commit subject, covered task ids, and the validation run tied to that checkpoint. When the report itself lands in a later bookkeeping commit, keep the checkpoint SHA from the implemented work and list any later report-only commit in `Additional commits or range`.
- Use `Candidate Learnings` to list durable observations or say `None` explicitly.
- Name blockers explicitly instead of implying them.
