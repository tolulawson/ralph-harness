#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime_state_helpers import check_runtime_preflight, resolve_canonical_checkout_root


CATEGORY_LABELS = {
    "self_healed": "Self-healed",
    "route_to_planning_task_gen": "Route To Planning/Task-Gen",
    "upgrade_required": "Upgrade Required",
    "hard_repair_required": "Hard Repair Required",
}


def print_group(label: str, messages: list[str]) -> None:
    print(f"{label}:")
    for message in messages:
        print(f"- {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an installed Ralph runtime for drift and mixed-version state.")
    parser.add_argument("--repo", default=".", help="Repository root to validate.")
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Report current preflight status without attempting self-heal repairs for derived state or admitted worktrees.",
    )
    args = parser.parse_args()

    repo_root = resolve_canonical_checkout_root(Path(args.repo).resolve())
    results = check_runtime_preflight(repo_root, apply_repairs=not args.no_repair)

    printed = False
    for category in (
        "self_healed",
        "route_to_planning_task_gen",
        "upgrade_required",
        "hard_repair_required",
    ):
        messages = results.get(category) or []
        if not messages:
            continue
        if printed:
            print()
        print_group(CATEGORY_LABELS[category], messages)
        printed = True

    if results["route_to_planning_task_gen"] or results["upgrade_required"] or results["hard_repair_required"]:
        return 1

    if printed:
        print()
    print("check-installed-runtime-state: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
