---
name: analyze
description: Perform a read-only cross-artifact consistency analysis across a numbered spec's spec, research, plan, and tasks files, surfacing duplication, ambiguity, coverage gaps, and inconsistencies before implementation continues.
---

# Analyze

## Use When

- A numbered spec has `spec.md`, `plan.md`, and `tasks.md`.
- The review target is artifact quality or execution readiness rather than a code diff.

## Goal

Identify inconsistencies, ambiguities, duplicated requirements, research-plan-task drift, coverage gaps, and unmapped tasks across the core planning artifacts before implementation proceeds.

## Inputs

- `.ralph/constitution.md`
- `specs/<spec-key>/spec.md`
- `specs/<spec-key>/research.md` when present
- `specs/<spec-key>/plan.md`
- `specs/<spec-key>/tasks.md`
- `.ralph/policy/project-policy.md`
- any user focus areas for the analysis

## Operating Constraints

- Read-only analysis only
- no artifact edits
- prioritize constitution or policy conflicts, requirement coverage gaps, and untestable criteria

## Workflow

1. Load the minimum required context from the constitution, policy, spec, research artifact when present, plan, and tasks.
2. Build a requirements inventory, user-story inventory, research guidance inventory, and task coverage map.
3. Detect:
   - duplication
   - ambiguity
   - underspecification
   - research-to-plan drift
   - policy or constitution conflicts
   - coverage gaps
   - inconsistencies in terminology, ordering, or artifact references
4. Assign severity:
   - `CRITICAL`
   - `HIGH`
   - `MEDIUM`
   - `LOW`
5. Produce a compact Markdown report with:
   - findings table
   - coverage summary
   - unmapped tasks
   - next actions

## Outputs

- analysis findings in the review report or response

## Stop Condition

Stop after the read-only analysis and next actions are documented.
