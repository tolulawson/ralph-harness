---
name: deslopify-lite
description: Lightweight pre-review quality gate that removes common slop from changed code before handoff. Focuses on type strictness, single-responsibility boundaries, fail-fast error handling, DRY cleanup, and dead-code/workaround removal.
---

# Deslopify Lite

## Use When

- Any implementation task is preparing to hand off to review.

## Goal

Apply a focused anti-slop pass to touched files before review handoff without adding external queue or score tooling.

## Workflow

1. Scope the pass to files changed for the active task checkpoint.
2. Run a targeted quality sweep across five categories:
   - type strictness
   - single responsibility
   - fail-fast error handling
   - DRY duplication cleanup
   - dead code and workaround removal
3. Fix issues found in scope or explicitly record why none were present.
4. Keep the pass within task scope; do not expand into unrelated refactors.

## Quality Checks

### Type Strictness

- Remove avoidable weak types (`any`, broad unions, unchecked dynamic casts).
- Prefer domain-specific and validated types at boundaries.

### Single Responsibility

- Break up overly large handlers, hooks, or helper units when they mix concerns.
- Keep each module focused on one clear responsibility.

### Fail Fast

- Avoid swallowed exceptions and silent fallback branches.
- Surface invalid state and unexpected inputs explicitly.

### DRY

- Collapse obvious duplicate logic into focused helpers.
- Avoid copy-paste branches that diverge behavior accidentally.

### Dead Code And Workarounds

- Remove unreachable code, stale flags, and temporary hacks no longer needed.
- Replace workaround comments with root-cause fixes where feasible in scope.

## Output Expectations

- Report `pass` only when the in-scope sweep is complete.
- List fixed slop issues in one concise line each, or write `none found`.
- If a slop issue is intentionally deferred, mark the handoff as not ready for review.
