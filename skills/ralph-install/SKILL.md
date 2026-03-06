---
name: ralph-install
description: Install the Codex-native Ralph harness into the current repository from the canonical scaffold under src/, preserving any existing AGENTS.md and initializing the target project's queue-driven state, PRD, and numbered spec register.
---

# Ralph Install

Install the Codex-native Ralph harness into the current repository using the canonical scaffold under `src/` in `https://github.com/tolulawson/ralph-harness`.

This is the main external entry point for adopting the harness in a target repository.

## Use When

- The current repository does not have the Ralph harness installed yet.
- You want to install the harness into a new or existing project.
- You want Codex to preserve the target repo's existing `AGENTS.md` and append Ralph loader instructions instead of replacing it.

## What This Skill Installs

- `AGENTS.md` merge or loader section
- `.ralph/constitution.md`
- `.ralph/policy/project-policy.md`
- `.ralph/state/workflow-state.json`
- `.ralph/state/spec-queue.json`
- `.ralph/templates/*`
- `.codex/config.toml`
- `agents/*.toml`
- `.agents/skills/*`
- neutral seed `specs/INDEX.md`
- generated runtime files listed in `src/generated-runtime-manifest.txt`

## Workflow

1. Confirm the current repository is the target project and not the source template repo.
2. Fetch or clone `https://github.com/tolulawson/ralph-harness` as the scaffold source.
3. Treat `src/` as the only installable scaffold root.
4. Read `src/install-manifest.txt`.
5. Copy only the manifest-listed scaffold paths into the current repository.
6. Read `src/generated-runtime-manifest.txt`.
7. Generate the runtime files and directories listed there for the target repository.
8. If the target repo already has `AGENTS.md`, preserve it and append a short Ralph harness loader section that tells Codex to read:
   - `.ralph/constitution.md`
   - `.ralph/policy/project-policy.md`
   - `.ralph/state/workflow-state.json`
   - `.ralph/state/spec-queue.json`
   - the latest report referenced by `last_report_path`
9. Install the control-plane files, runtime contracts, and runtime role skills from `src/`.
10. Do not copy the source repo's root dogfood logs, reports, TODOs, lessons, PRD, or numbered spec history.
11. Rewrite the installed state files so they reflect the target project rather than the scaffold seed.
12. Adapt `.ralph/constitution.md` and `.ralph/policy/project-policy.md` to the target repo's workflow.
13. Create the first real project PRD, epoch framing, numbered spec register, and initial tasks.
14. Append the initial event and report trail for the target project.

## Outputs

- installed harness scaffold from `src/` in the current repository
- merged or updated `AGENTS.md`
- initialized `.ralph/` runtime structure and generated runtime records
- initialized target-project PRD, spec queue, and numbered spec artifacts

## References

- Read `references/install-checklist.md` for the installation checklist and copy/reset rules.
- Read `references/agents-loader-snippet.md` for the loader text that should be appended to an existing `AGENTS.md`.
- Read `references/source-vs-runtime.md` for the distinction between distributable source skills and installed runtime skills.

## Completion

At the end of installation:

- verify the harness files exist in the target repo
- verify the generated runtime files from `src/generated-runtime-manifest.txt` exist in the target repo
- verify the loader points to the constitution, policy, workflow state, spec queue, and latest report
- verify the target project has its first real PRD, spec queue, and numbered spec set
- remind the user: `Restart Codex to pick up new skills.` if this skill was newly installed globally
