#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
REGISTRY_PATH = SRC / ".ralph/agent-registry.json"


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text())


def render_loader_block(registry: dict) -> str:
    lines = [
        registry["loaders"]["managed_block_start"],
        "# Ralph Harness Loader",
        "",
        "This file is part of the generic Ralph harness scaffold that gets installed into a target repository.",
        "",
        "All paths below are relative to the target repository root, which becomes the live Ralph runtime after installation.",
        "",
        "## Read Order",
        "",
        "Before doing substantial work, read these files in order:",
        "",
    ]
    for index, item in enumerate(registry["loaders"]["read_order"], start=1):
        lines.append(f"{index}. `{item}`")
    lines.extend(
        [
            "",
            "## Purpose Of This File",
            "",
            "This loader is intentionally thin. It points the active coding agent at the canonical Ralph runtime doctrine under `.ralph/`.",
            "",
            "- The project-specific Ralph mission lives in `.ralph/constitution.md`.",
            "- The generic installed-runtime doctrine lives in `.ralph/runtime-contract.md`.",
            "- Project-specific runtime extensions live in `.ralph/policy/runtime-overrides.md`.",
            "- Project-specific workflow rules live in `.ralph/policy/project-policy.md`.",
            "- Project truths and promoted learnings live under `.ralph/context/`.",
            "- Runtime execution state lives in `.ralph/state/`.",
            "",
            "## Operating Rule",
            "",
            "Do not treat conversational memory as the source of truth when the Ralph runtime files already contain the needed state or policy.",
            "",
            "Treat the repository root as the harness work area after installation. Keep agent-specific instructions thin and route all substantive behavior back to the shared Ralph runtime contract.",
            "When a public Ralph entrypoint is invoked, keep the entry thread thin and immediately launch the dedicated Ralph subagent for that entrypoint instead of doing the work inline.",
            "",
            "If this repository already has its own loader file, preserve non-Ralph content and replace only the managed Ralph block between the markers shown here.",
            registry["loaders"]["managed_block_end"],
            "",
        ]
    )
    return "\n".join(lines)


def render_claude_agent(role: dict) -> str:
    helper = ", ".join(role["helper_skills"]) if role["helper_skills"] else "None"
    writes = "\n".join(f"- {item}" for item in role["allowed_writes"])
    native = "allowed" if role["native_subagent_delegation"] else "not allowed"
    lines = [
            "---",
            f"name: {role['id']}",
            f"description: {role['purpose']}",
            "---",
            "",
            f"# Ralph {role['id'].replace('_', ' ').title()} Agent",
            "",
            "Read the canonical Ralph runtime doctrine first, then execute only the assigned role.",
            "",
            "## Canonical Inputs",
            "",
            "- `.ralph/constitution.md`",
            "- `.ralph/runtime-contract.md`",
            "- `.ralph/policy/runtime-overrides.md`",
            "- `.ralph/policy/project-policy.md`",
            "- `.ralph/state/workflow-state.json`",
            "- `.ralph/state/spec-queue.json`",
            "- `.ralph/state/worker-claims.json`",
            "",
            "## Role Contract",
            "",
            f"- Canonical role skill: `.agents/skills/{role['skill']}/SKILL.md`",
            f"- Classification: `{role['classification']}`",
            f"- Permission model: `{role['permission_model']}`",
            f"- Native subagent delegation: `{native}`",
            f"- Helper skills: {helper}",
            (
                "- Launch topology: thin Ralph entry thread -> dedicated orchestrator subagent -> worker subagents or claimed worker sessions"
                if role["id"] == "orchestrator"
                else None
            ),
            (
                "- Worker fan-out: exactly one orchestrator per `ralph-execute` invocation, filling the bounded admission window with worker subagents when dependencies allow"
                if role["id"] == "orchestrator"
                else None
            ),
            "",
            "## Allowed Writes",
            "",
            writes,
            "",
            "Use the canonical `.agents/skills/` role instructions and the shared `.ralph/` runtime contract as the source of truth. Do not invent tool-specific workflow rules that diverge from Ralph.",
            "",
        ]
    return "\n".join(line for line in lines if line is not None)


def render_claude_command(entrypoint: dict) -> str:
    lines = [
            "---",
            f"description: {entrypoint['purpose']}",
            "---",
            "",
            f"Run `{entrypoint['id']}` using the canonical Ralph source of truth at `{entrypoint['doc_path']}`.",
            "",
            "Read the shared Ralph runtime files first, preserve any existing managed Ralph loader blocks, and follow the canonical contract instead of rewriting it from memory.",
    ]
    if entrypoint["id"] == "ralph-execute":
        lines.append("Keep the invoking thread thin: launch a dedicated Ralph orchestrator subagent immediately, then wait and relay its result instead of orchestrating inline on the command thread.")
        lines.append("That orchestrator should fill the admitted-spec execution window with worker subagents up to the bounded thread budget, rather than spawning multiple orchestrators or settling for one-role-at-a-time execution while runnable specs remain.")
    elif entrypoint["id"] == "ralph-plan":
        lines.append("Keep the invoking thread thin: launch a dedicated Ralph planning coordinator subagent immediately, let that coordinator sequence `specify`, same-batch `research`, `plan`, `task-gen`, and `plan-check` as needed, then wait and relay its result instead of planning inline on the command thread.")
    elif entrypoint["id"] == "ralph-prd":
        lines.append("Keep the invoking thread thin: launch a dedicated Ralph `prd` subagent immediately, then wait and relay its result instead of writing the PRD inline on the command thread.")
    lines.append("")
    return "\n".join(line for line in lines if line is not None)


def render_cursor_rule(rule_name: str, description: str, bullets: list[str], always_apply: bool) -> str:
    lines = [
        "---",
        f"description: {description}",
        f"alwaysApply: {'true' if always_apply else 'false'}",
        "---",
        "",
        f"# {rule_name}",
        "",
    ]
    lines.extend(f"- {bullet}" for bullet in bullets)
    lines.append("")
    return "\n".join(lines)


def expected_outputs(registry: dict) -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    loader = render_loader_block(registry)
    outputs[SRC / "AGENTS.md"] = loader
    outputs[SRC / "CLAUDE.md"] = loader

    for role in registry["roles"]:
        outputs[SRC / ".claude/agents" / f"{role['id']}.md"] = render_claude_agent(role)

    for entrypoint in registry["entrypoints"]:
        outputs[SRC / ".claude/commands" / f"{entrypoint['id']}.md"] = render_claude_command(entrypoint)

    outputs[SRC / ".cursor/rules/ralph-core.mdc"] = render_cursor_rule(
        "Ralph Core",
        "Core Ralph runtime guidance for Cursor.",
        [
            "Read the managed Ralph loader block in `AGENTS.md` before doing substantial work.",
            "Treat `.ralph/` as the canonical runtime doctrine and state surface.",
            "Treat the invoking thread as a Ralph launcher only when a public `ralph-*` entrypoint is used. Keep that thread thin and move substantive Ralph work into the dedicated subagent for that entrypoint.",
            "Use `.ralph/state/worker-claims.json` as the shared worker-claims registry for cross-runtime execution.",
            "Execute numbered spec work only from assigned spec worktrees, never from the canonical checkout.",
            "Use `.cursor/rules/` only as Cursor-native wrappers around the shared Ralph contract, not as a divergent workflow definition.",
            "When a task references a Ralph role or entrypoint, route back to `.agents/skills/` and the public `skills/ralph-*` docs."
        ],
        True,
    )
    outputs[SRC / ".cursor/rules/ralph-execute.mdc"] = render_cursor_rule(
        "Ralph Execute",
        "How Cursor should resume an installed Ralph runtime.",
        [
            "Read `.ralph/constitution.md`, `.ralph/runtime-contract.md`, `.ralph/policy/runtime-overrides.md`, `.ralph/policy/project-policy.md`, `.ralph/state/workflow-state.json`, `.ralph/state/spec-queue.json`, and `.ralph/state/worker-claims.json` before execution.",
            "Keep the invoking thread thin: immediately launch a dedicated Ralph orchestrator subagent for `ralph-execute`, then wait and relay its result instead of orchestrating inline.",
            "That orchestrator should fill the admitted-spec execution window with bounded worker subagents, keeping at most one non-research worker per admitted spec and refilling freed slots while runnable work remains.",
            "A Cursor session may act as the lease-holder for a brief reconciliation window or claim a runnable worker slot, and a finishing session may reconcile its own validated work after acquiring the lease.",
            "Use the canonical behavior from `skills/ralph-execute/SKILL.md` and `.agents/skills/orchestrator/SKILL.md`."
        ],
        False,
    )
    outputs[SRC / ".cursor/rules/ralph-install-upgrade.mdc"] = render_cursor_rule(
        "Ralph Install And Upgrade",
        "How Cursor should install or upgrade Ralph.",
        [
            "Install from `src/` only.",
            "Install and upgrade all supported adapter packs together: `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/`, `.cursor/`, and the shared `.ralph/` scaffold.",
            "Preserve non-Ralph content in existing loader files and replace only the managed Ralph blocks.",
            "Follow `INSTALLATION.md` and `UPGRADING.md` as the canonical source of truth."
        ],
        False,
    )
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify the shipped Ralph runtime adapters.")
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs do not match the checked-in files.")
    args = parser.parse_args()

    registry = load_registry()
    outputs = expected_outputs(registry)
    failures: list[str] = []

    for path, expected in outputs.items():
        if args.check:
            if not path.exists():
                failures.append(f"missing generated adapter file: {path.relative_to(ROOT)}")
                continue
            actual = path.read_text()
            if actual != expected:
                failures.append(f"stale generated adapter file: {path.relative_to(ROOT)}")
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected)

    if args.check and failures:
        for failure in failures:
            print(f"generate-runtime-adapters: {failure}")
        return 1

    if args.check:
        print("generate-runtime-adapters: ok")
        return 0

    print("generate-runtime-adapters: wrote adapter files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
