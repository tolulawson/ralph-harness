---
name: ralph-prd
description: Generate or update a Ralph-style project PRD in the current repository by asking a small number of high-value clarifying questions, then writing a structured PRD with epochs, bounded user stories, and verifiable acceptance criteria.
---

# Ralph PRD

Generate or update a Ralph-style project PRD for the current repository without invoking the full execution loop.

Use this as the direct public entry point for shaping work before planning or execution.

In this source repository, the root `tasks/` and `specs/` files are dogfood runtime artifacts. The installable scaffold lives under `src/`, and target runtime records are created after installation rather than copied from the scaffold history.

## Use When

- The user wants a PRD without running the full harness.
- A new project or major initiative needs to be shaped into a durable artifact.
- The installed harness exists and the next useful step is product definition.

## Workflow

1. Read the current project context, existing PRDs, and any active notes relevant to the requested work.
2. Ask `3-5` high-value clarification questions if important ambiguity remains.
3. Prefer short, lettered answer options where that will help the user answer quickly.
4. Write or update `tasks/prd-<project>.md` using a consistent structure.
5. Include an initial epoch map that groups likely specs into ordered milestones.
6. Keep user stories small enough to hand off cleanly into numbered specs and execution.
7. Write verifiable acceptance criteria for each story or requirement.
8. Do not implement code or create downstream execution artifacts in this skill.
9. Recommend the next entry point:
   - `$ralph-plan` when the spec queue should be generated next
   - `$ralph-execute` when the installed harness should continue from state

## Outputs

- `tasks/prd-<project>.md`
- a concise recommendation for the next public entry point

## References

- Read `references/prd-contract.md` for the expected PRD structure and quality bar.

## Completion

Stop once the PRD is written or updated and the next recommended entry point is clear.
