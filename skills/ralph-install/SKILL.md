---
name: ralph-install
description: Install the Ralph multi-agent runtime into the current repository from the canonical scaffold under src/, preserving any existing loader files and initializing the target project's queue-driven state, PRD, and numbered spec register.
---

# Ralph Install

Install the Ralph multi-agent runtime into the current repository using the canonical tagged scaffold under `src/` in `https://github.com/tolulawson/ralph-harness`.

This is the main external entry point for adopting the harness in a target repository.

`INSTALLATION.md` is the canonical install source of truth. This skill is only the execution adapter for that guide.

## Use When

- The current repository does not have the Ralph harness installed yet.
- You want to install the harness into a new or existing project.
- You want the active coding agent to preserve the target repo's existing loader files and update only the Ralph-managed blocks.

## Workflow

1. Confirm the current repository is the target project and not the source template repo.
2. Fetch or clone `https://github.com/tolulawson/ralph-harness` at the desired release tag as the scaffold source.
3. Treat `src/` as the only installable scaffold root.
4. Read `INSTALLATION.md` first and follow it as the authoritative install workflow.
5. Use `src/install-manifest.txt` and `src/generated-runtime-manifest.txt` exactly as `INSTALLATION.md` specifies.
6. Use the runtime's question/input tool before writing `.ralph/context/project-facts.json` to ask whether the current checkout should be the canonical control plane or whether the user wants a custom path or branch; persist the answer in `canonical_control_plane.mode`, `canonical_control_plane.checkout_path`, and optional `canonical_control_plane.base_branch`.
7. Use the runtime's question/input tool to ask whether control-plane artifacts should be tracked in version control or excluded via `.gitignore`; persist that answer in `control_plane_versioning.mode` and `control_plane_versioning.gitignore_patterns`, and only edit `.gitignore` when the user chooses that mode.
8. Persist the project's canonical `base_branch` into `.ralph/context/project-facts.json` during installation, seed `validation_bootstrap_commands` there only when the project already has known environment-prep commands, and initialize `orchestrator_stop_hook`, `worktree_bootstrap_commands`, `bootstrap_env_files`, and `bootstrap_copy_exclude_globs` with the shipped conservative defaults.
9. Install the canonical-control-plane model so shared state stays in the selected canonical checkout and admitted spec worktrees later receive generated `.ralph/shared/` overlays for shared reads and canonical report writes.
10. Install the repo-local hook surfaces for Codex, Claude Code, and Cursor plus the shared `.ralph/hooks/stop-boundary.py` file.
11. Use the canonical `AGENTS.md` and `CLAUDE.md` loader guidance plus the install checklist from `INSTALLATION.md` rather than inventing or rephrasing the install flow.
12. Complete the installation without copying any repo-root source files outside `src/` from the source repository.

## Outputs

- the current repository ends up installed exactly as `INSTALLATION.md` describes

## References

- Read `INSTALLATION.md` for the canonical installation workflow, AGENTS loader snippet, reset steps, and verification checklist.
- Read `references/source-vs-runtime.md` for the distinction between distributable source skills and installed runtime skills.

## Completion

At the end of installation:

- verify the installation against the checklist and verification section in `INSTALLATION.md`
- confirm the installed runtime reflects worktree-only execution, canonical shared-state ownership, `.ralph/shared/` worktree overlays, bootstrap-gated implementation, and repo-local stop-boundary hook setup before handing it back
- remind the user to restart their coding agent if it needs to reload newly installed project instructions
