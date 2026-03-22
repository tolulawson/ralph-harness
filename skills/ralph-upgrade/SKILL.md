---
name: ralph-upgrade
description: Upgrade an already-installed Ralph harness in the current repository from the latest tagged scaffold surface while preserving project-owned runtime files and history.
---

# Ralph Upgrade

Upgrade the Codex-native Ralph harness in the current repository using the tagged scaffold surface in `https://github.com/tolulawson/ralph-harness`.

This is the main external entry point for refreshing an existing install without overwriting project-owned runtime data.

`UPGRADING.md` is the canonical upgrade source of truth. This skill is only the execution adapter for that guide.

## Use When

- The current repository already has the Ralph harness installed.
- You want to move that install to a newer tagged Ralph scaffold release.
- You want Codex to preserve project-owned runtime files while refreshing only scaffold-owned files.

## Workflow

1. Confirm the current repository is a target project with the Ralph harness already installed.
2. Fetch or clone `https://github.com/tolulawson/ralph-harness` at the requested release tag.
3. Read `UPGRADING.md` first and follow it as the authoritative upgrade workflow.
4. Run `python3 scripts/check-upgrade-surface.py --repo <target-repo>` from the checked-out source repo before any scaffold-owned files are refreshed.
5. If the preflight reports direct edits to `.ralph/runtime-contract.md`, stop and move those project-specific runtime rules into `.ralph/policy/runtime-overrides.md` instead of overwriting the base contract.
6. Use `src/upgrade-manifest.txt` exactly as `UPGRADING.md` specifies.
7. Refresh only the managed Ralph block inside `AGENTS.md` instead of replacing the full file.
8. Run `python3 scripts/migrate-installed-runtime.py --repo <target-repo>` from the checked-out source repo after the scaffold-owned files have been refreshed.
9. Let the migration merge `.codex/config.toml` so user-owned settings survive while Ralph-required feature flags and managed role mappings are refreshed.
10. Do not upgrade over a healthy held orchestrator lease; if the migration reports a live lease-holder, stop and retry after the active run releases or expires.
11. Let the migration rewrite only Ralph-owned runtime state and projections, recover stale lease state, create or normalize the durable intents file, seed collision-safe worktree metadata, normalize clear legacy worker report paths into spec-scoped aliases, create `.ralph/policy/runtime-overrides.md` when it is missing, and create missing `task-state.json` files when inference is clear.
12. If migration reports ambiguous history, duplicate branch ownership across specs, or ambiguous shared legacy report ownership, stop and repair that state instead of guessing.
13. Update `.ralph/harness-version.json` with the selected tag, resolved commit, and runtime-contract baseline metadata.
14. Complete the upgrade without overwriting project-owned runtime files unless a named migration step requires it.

## Outputs

- the current repository ends up upgraded exactly as `UPGRADING.md` describes

## Completion

At the end of upgrade:

- verify the upgrade against the checklist and verification section in `UPGRADING.md`
- remind the user: `Restart Codex to pick up new skills.` if this skill was newly installed globally
