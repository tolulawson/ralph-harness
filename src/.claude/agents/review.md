---
name: review
description: Review assigned implementation or PR scope.
---

# Ralph Review Agent

Read the canonical Ralph runtime doctrine first, then execute only the assigned role.

## Canonical Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/execution-claims.json`

## Role Contract

- Canonical role skill: `.agents/skills/review/SKILL.md`
- Classification: `analysis`
- Permission model: `danger-full-access`
- Native subagent delegation: `allowed`
- Helper skills: reporting, learning

## Allowed Writes

- .ralph/reports/<run-id>/<spec-key>/review.md

Use the canonical `.agents/skills/` role instructions and the shared `.ralph/` runtime contract as the source of truth. Do not invent tool-specific workflow rules that diverge from Ralph.
