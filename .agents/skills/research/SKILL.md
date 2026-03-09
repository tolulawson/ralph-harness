---
name: research
description: Research one numbered spec using project-global and spec-local context, then write a spec-local research artifact that planning can consume without changing shared state.
---

# Spec Research

## Use When

- A numbered spec exists and `spec.md` is stable enough for implementation research.
- The orchestrator has assigned this spec to the research role.
- The spec belongs to the current planning batch selected for bounded parallel research.

## Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/project-policy.md`
- `.ralph/context/project-truths.md`
- `.ralph/context/project-facts.json`
- `.ralph/context/learning-summary.md`
- `specs/<spec-key>/spec.md`
- optional repo files that materially constrain the implementation
- official documentation or other primary sources when current technical behavior matters

## Workflow

1. Read the project-global doctrine and the assigned `spec.md`.
2. Treat `Spec Constraints` and `Deferred Scope` in the spec as binding research boundaries.
3. Gather the smallest set of repo-local and external evidence needed to support implementation planning.
4. Prefer primary sources and official documentation when technical behavior could have changed.
5. Write `specs/<spec-key>/research.md` with these sections:
   - `Summary`
   - `Spec Constraints`
   - `Standard Stack`
   - `Architecture Patterns`
   - `Do Not Hand-Roll`
   - `Pitfalls`
   - `Code/Usage Notes`
   - `Open Questions`
   - `Sources and Confidence`
6. Label findings as `confirmed`, `recommended`, or `open question`.
7. Write only spec-local artifacts and the role report.
8. Do not spawn nested workers.
9. Do not update shared queue state, workflow state, projections, event logs, truths, facts, or promoted learning summaries.

## Outputs

- `specs/<spec-key>/research.md`
- `.ralph/reports/<run-id>/research-<spec-id>.md`

## Stop Condition

Stop after the assigned spec-local research artifact and report are complete.
