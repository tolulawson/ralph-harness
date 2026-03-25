---
name: implement
description: Execute one assigned task in the spec worktree.
---

# Ralph Implement Agent

Read the canonical Ralph runtime doctrine first, then execute only the assigned role.

## Canonical Inputs

- `.ralph/constitution.md`
- `.ralph/runtime-contract.md`
- `.ralph/policy/runtime-overrides.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/state/worker-claims.json`

## Role Contract

- Canonical role skill: `.agents/skills/implement/SKILL.md`
- Classification: `delivery`
- Permission model: `danger-full-access`
- Native subagent delegation: `not allowed`
- Helper skills: reporting, learning, react-effects-without-effects, deslopify-lite

## Allowed Writes

- product files in assigned worktree
- spec-local implementation artifacts
- .ralph/reports/<run-id>/<spec-key>/implement.md

Use the canonical `.agents/skills/` role instructions and the shared `.ralph/` runtime contract as the source of truth. Do not invent tool-specific workflow rules that diverge from Ralph.
