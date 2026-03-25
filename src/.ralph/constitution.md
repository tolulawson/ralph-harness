# Ralph Harness Constitution

## Mission

This document is part of the generic Ralph harness scaffold installed into a target repository.

This file captures project-specific mission, priority, and target-repo adaptation rules for an installed harness.

The generic installed-runtime doctrine lives in `.ralph/runtime-contract.md`.

## Constitutional Priority

Interpret the harness in this order:

1. this constitution
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/runtime-overrides.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/context/project-truths.md`
6. `.ralph/context/project-facts.json`
7. `.ralph/context/learning-summary.md`
8. `.ralph/state/workflow-state.json`
9. `.ralph/state/spec-queue.json`
10. active spec artifacts and latest role reports

`AGENTS.md` and `CLAUDE.md` are loader surfaces only. They point the active coding agent at the real operating doctrine under `.ralph/`.

After installation, the target repository root is the live harness runtime.

The public source skills used to install, plan, execute, or upgrade the harness live in the source repository, not inside the installed runtime. The installed runtime uses the role skills under `.agents/skills/`.

## Source Scaffold Contract

- This scaffold is generic and should be adapted to the target project during installation.
- Runtime records such as `tasks/todo.md`, `tasks/lessons.md`, `.ralph/logs/events.jsonl`, and `.ralph/reports/` are generated during installation or first run.
- Project-specific PRDs, specs, tasks, reports, and event history belong to the target repository runtime, not to the scaffold source.
- Automatic upgrades overwrite only the scaffold-owned paths listed in `src/upgrade-manifest.txt` from the source repository.
- Project-owned runtime files remain outside the automatic upgrade surface unless a named migration step explicitly targets them.
- `.ralph/runtime-contract.md` is scaffold-owned and should remain the canonical base contract from the installed Ralph version.
- Project-specific runtime rules belong in `.ralph/policy/runtime-overrides.md`, which is preserved across upgrade.

## Knowledge Layer

- `.ralph/context/project-truths.md` stores explicit human-provided project truths and rules.
- `.ralph/context/project-facts.json` stores optional structured facts that actually apply to the target project.
- `.ralph/context/learning-summary.md` stores promoted stable learnings that should become normal harness context.
- `.ralph/context/learning-log.jsonl` is an append-only ledger for candidate implicit learnings and promotion history.
- `.ralph/harness-version.json` records which Ralph release tag and resolved commit the target repository is using.
- Explicit truths become canonical immediately.
- Implicit learnings append to the log first and are promoted only after validation or explicit approval.

## Planning Hierarchy

The durable planning hierarchy is:

1. project PRD
2. epochs
3. numbered specs
4. spec-local research
5. dependency-ordered tasks
6. branch and GitHub PR execution

Epochs are a grouping and reporting layer. Specs are the actual execution queue.

## State Rules

- `.ralph/state/workflow-state.json` is the canonical machine-readable runtime state.
- `.ralph/state/spec-queue.json` is the canonical machine-readable spec queue and spec-state registry.
- `.ralph/state/worker-claims.json` is the canonical machine-readable worker claim registry for cross-runtime execution claims.
- `.ralph/state/workflow-state.md` is a human-readable companion file and must agree with the JSON state.
- `specs/<spec-id>-<slug>/task-state.json` is the canonical machine-readable task lifecycle registry for a spec when it exists.
- `specs/<spec-id>-<slug>/research.md` is the canonical spec-local research artifact when research has been completed for that spec.
- `.ralph/policy/runtime-overrides.md` is the preserved project-owned extension surface for runtime-specific additions.
- `.ralph/context/project-truths.md`, `.ralph/context/project-facts.json`, and `.ralph/context/learning-summary.md` are part of the default harness context.
- `.ralph/context/learning-log.jsonl` is the append-only learning ledger and should be tailed selectively rather than loaded in full.
- `specs/INDEX.md` is a human-readable projection of the spec queue.
- `tasks/`, `specs/`, `.ralph/reports/`, and `.ralph/logs/events.jsonl` are part of the durable memory of the harness.
- do not rely on conversational memory when a file can carry the state.

Only neutral seed state and installable contracts belong in the scaffold state and spec files. Project-specific runtime records are created after installation.

## Resume Order

Use this order whenever a fresh coding-agent run resumes work:

1. `.ralph/constitution.md`
2. `.ralph/runtime-contract.md`
3. `.ralph/policy/runtime-overrides.md`
4. `.ralph/policy/project-policy.md`
5. `.ralph/context/project-truths.md`
6. `.ralph/context/project-facts.json`
7. `.ralph/context/learning-summary.md`
8. `.ralph/state/workflow-state.json`
9. `.ralph/state/spec-queue.json`
10. `.ralph/state/worker-claims.json`
11. `.ralph/reports/<current-run-id>/` or `last_report_path`
12. active spec files in `specs/<spec-id>-<slug>/`
13. `specs/<spec-id>-<slug>/task-state.json` when present
14. `specs/INDEX.md`
15. active PRD files in `tasks/`
16. `tasks/todo.md`
17. recent events from `.ralph/logs/events.jsonl`
18. recent learning entries from `.ralph/context/learning-log.jsonl` only when needed
19. older logs only if the recent context is insufficient

## Canonical Phases

- `bootstrap`
- `prd`
- `epoch_planning`
- `specification`
- `research`
- `planning`
- `task_generation`
- `plan_review`
- `implementation`
- `review`
- `verification`
- `release`
- `blocked`
- `complete`

## Canonical Task Statuses

- `queued`
- `ready`
- `in_progress`
- `paused`
- `awaiting_review`
- `review_failed`
- `awaiting_verification`
- `verification_failed`
- `awaiting_release`
- `released`
- `done`
- `blocked`

## Canonical Spec Statuses

- `draft`
- `planned`
- `ready`
- `in_progress`
- `awaiting_pr`
- `awaiting_review`
- `review_failed`
- `awaiting_verification`
- `verification_failed`
- `plan_check_failed`
- `awaiting_merge`
- `done`
- `blocked`
- `superseded`
- `paused`

## Report Contract

Every role report must include these sections:

- `Objective`
- `Inputs Read`
- `Artifacts Written`
- `Verification`
- `Quality Gate`
- `Commit Evidence`
- `Interruption Assessment`
- `Candidate Learnings`
- `Open Issues`
- `Recommended Next Role`

Role reports are the handoff contract for the next fresh run and should name the active spec and active PR context whenever applicable. `Quality Gate` must capture `React Effects Audit` and `Deslopify Lite` status for handoffs past implementation. `Commit Evidence` is the git traceability layer for task handoff and must capture the checkpoint commit, covered task ids, and validation linkage without storing git SHAs in canonical machine state. Candidate learnings must either list concrete observations with evidence or explicitly say `None`.

## Git And PR Policy

Default policy is one branch and one GitHub PR per spec:

- branch format: `ralph/<spec-key>`
- optional task branch suffix: `ralph/<spec-key>/<task-id>` when policy explicitly allows it
- base branch defaults to the project policy setting
- direct-to-main is disabled by default
- review is required before merge
- verification is required before merge
- a spec is not `done` until its GitHub PR is merged

The reference repo may contain example queue entries with null PR metadata when no live PR was opened locally. Installed target projects should treat real GitHub PR tracking as required.

Completed tasks must also satisfy the atomic commit rule before handoff:

- create at least one atomic commit for each completed task
- keep each commit scoped to one task or one coherent sub-slice of that task
- include `Quality Gate` evidence before handing work to review
- tie the report's validation evidence to the checkpoint commit or explicit commit list
- do not hand a task to review, verification, or release from a dirty worktree
