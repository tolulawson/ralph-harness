---
name: ralph-prd
description: Generate or update a Ralph-style project PRD in the current repository by asking a small number of high-value clarifying questions, then writing a structured PRD with epochs, bounded user stories, and verifiable acceptance criteria.
---

# Ralph PRD

Generate or update a Ralph-style project PRD for the current repository without invoking the full execution loop.

Use this as the direct public entry point for shaping work before planning or execution.

This public entrypoint is a thin launcher. It should keep the invoking thread focused on Ralph doctrine and immediately hand PRD work to a dedicated `prd` subagent.

In this source repository, the installable scaffold lives under `src/`, and target runtime records are created after installation rather than copied from repo-root source materials.

## Use When

- The user wants a PRD without running the full harness.
- A new project or major initiative needs to be shaped into a durable artifact.
- The installed harness exists and the next useful step is product definition.

## Workflow

1. Read the current project context, existing PRDs, and any active notes relevant to the requested work.
2. Immediately spawn a dedicated `prd` subagent with forked context semantics and the canonical Ralph PRD config.
3. Keep the invoking thread thin after launch. It may pass the repo path or user request into the `prd` subagent, wait for completion, and relay the result, but it must not generate the PRD inline or fall back to current-session PRD authoring.
4. Inside the `prd` subagent, ask `3-5` high-value clarification questions if important ambiguity remains.
5. Prefer short, lettered answer options where that will help the user answer quickly.
6. Write or update `tasks/prd-<project>.md` using a consistent structure.
7. Include an initial epoch map that groups likely specs into ordered milestones.
8. Keep user stories small enough to hand off cleanly into numbered specs and execution.
9. Write verifiable acceptance criteria for each story or requirement.
10. Do not implement code or create downstream execution artifacts in this skill.
11. Recommend the next entry point:
   - `$ralph-plan` when the spec queue should be generated next
   - `$ralph-execute` when the installed harness should continue from state

## Outputs

- `tasks/prd-<project>.md`
- a concise recommendation for the next public entry point

## References

- Read `references/prd-contract.md` for the expected PRD structure and quality bar.

## Completion

Stop once the PRD is written or updated and the next recommended entry point is clear.
