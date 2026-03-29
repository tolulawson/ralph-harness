---
name: ralph-upgrade
description: Upgrade an already-installed Ralph multi-agent runtime in the current repository from the latest tagged scaffold surface while preserving project-owned runtime files and history.
---

# Ralph Upgrade

Upgrade the Ralph multi-agent runtime in the current repository using the tagged scaffold surface in `https://github.com/tolulawson/ralph-harness`.

This is the main external entry point for refreshing an existing install without overwriting project-owned runtime data.

`UPGRADING.md` is the canonical upgrade source of truth. This skill is only the execution adapter for that guide.

## Use When

- The current repository already has the Ralph harness installed.
- You want to move that install to a newer tagged Ralph scaffold release.
- You want the active coding agent to preserve project-owned runtime files while refreshing only scaffold-owned files.

## Workflow

1. Confirm the current repository is a target project with the Ralph harness already installed.
2. Fetch or clone `https://github.com/tolulawson/ralph-harness` at the requested release tag.
3. Read `UPGRADING.md` first and follow it as the authoritative upgrade workflow.
4. Run `python3 scripts/check-upgrade-surface.py --repo <target-repo>` from the checked-out source repo before any scaffold-owned files are refreshed.
5. If the preflight reports direct edits to `.ralph/runtime-contract.md`, stop and move those project-specific runtime rules into `.ralph/policy/runtime-overrides.md` instead of overwriting the base contract.
6. Use `src/upgrade-manifest.txt` exactly as `UPGRADING.md` specifies.
7. Refresh only the managed Ralph blocks inside `AGENTS.md` and `CLAUDE.md` instead of replacing the full files.
8. Run `python3 scripts/migrate-installed-runtime.py --repo <target-repo>` from the checked-out source repo after the scaffold-owned files have been refreshed.
9. Let the migration preserve user-owned runtime-specific settings while Ralph-managed adapter packs, repo-local hook configs, and shared runtime files are refreshed.
10. Do not upgrade over a healthy held orchestrator lease; if the migration reports a live lease-holder, stop and retry after the active run releases or expires.
11. Let the migration rewrite only Ralph-owned runtime state and projections, recover stale lease state, create or normalize the durable intents file, preserve or backfill `.ralph/context/project-facts.json` canonical `base_branch` data plus the new bootstrap or stop-hook facts, seed collision-safe worktree metadata, regenerate `.ralph/shared/` overlays for admitted worktrees, propagate bootstrap lifecycle fields into claims and queue summaries, normalize clear legacy worker report paths into spec-scoped aliases, create `.ralph/policy/runtime-overrides.md` when it is missing, and create missing `task-state.json` files when inference is clear.
12. Preserve unknown runtime skills under `.agents/skills/`, and stop when a Ralph-managed runtime skill directory has local drift instead of deleting or overwriting it silently.
13. Confirm the upgraded runtime still enforces worktree-only execution, bootstrap-gated implementation, and `active_spec_ids` as the authoritative active-spec set instead of relying on compatibility mirrors.
14. If migration reports ambiguous history, duplicate branch ownership across specs, or ambiguous shared legacy report ownership, stop and repair that state instead of guessing.
15. Update `.ralph/harness-version.json` with the selected tag, resolved commit, and runtime-contract baseline metadata.
16. Complete the upgrade without overwriting project-owned runtime files unless a named migration step requires it.

## Outputs

- the current repository ends up upgraded exactly as `UPGRADING.md` describes

## Completion

At the end of upgrade:

- verify the upgrade against the checklist and verification section in `UPGRADING.md`
- confirm the upgraded runtime still matches the latest control-plane doctrine around ephemeral lease windows, canonical shared-state ownership, `.ralph/shared/` worktree overlays, bootstrap lifecycle tracking, and conservative repo-local stop-boundary hooks
- remind the user to restart their coding agent if it needs to reload newly upgraded project instructions
